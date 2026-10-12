"""
Automated REST API Test Suite for Barcode Test Server.
Tests endpoints over HTTP on http://127.0.0.1:5892.
"""

import os
import sys
import threading
import unittest
import urllib.request
import urllib.parse
import json
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

BASE_URL = "http://127.0.0.1:5892"


class TestServerRestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Check if server is already running on port 5892
        cls._server_started = False
        try:
            req = urllib.request.Request(f"{BASE_URL}/api/camera/status")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return
        except Exception:
            pass

        import server
        cls._server_started = True
        cls._thread = threading.Thread(
            target=server.start_server,
            kwargs={"port": 5892, "start_video": True},
            daemon=True
        )
        cls._thread.start()

        deadline = time.time() + 10.0
        while time.time() < deadline:
            try:
                req = urllib.request.Request(f"{BASE_URL}/api/camera/status")
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status == 200:
                        st = json.loads(resp.read().decode())
                        if st.get("is_connected") or st.get("connection_error"):
                            break
            except Exception:
                pass
            time.sleep(0.3)

    def test_01_camera_status(self):
        # Allow up to 6 seconds for DirectShow / MediaFoundation hardware negotiation
        deadline = time.time() + 6.0
        data = {}
        while time.time() < deadline:
            req = urllib.request.Request(f"{BASE_URL}/api/camera/status")
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode())
                if data.get("is_connected"):
                    break
            time.sleep(0.3)

        self.assertIn("is_connected", data)
        self.assertIn("connection_error", data)
        self.assertIn("actual_fps", data)
        self.assertTrue(data.get("is_connected"))

    def test_02_session_lifecycle_and_auto_chain(self):
        # 1. Start session PKG-API-01
        payload1 = json.dumps({"barcode": "PKG-API-01"}).encode()
        req1 = urllib.request.Request(
            f"{BASE_URL}/api/session/start",
            data=payload1,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req1) as resp:
            self.assertEqual(resp.status, 200)
            data1 = json.loads(resp.read().decode())
            self.assertTrue(data1["success"])
            self.assertEqual(data1["barcode"], "PKG-API-01")
            id1 = data1["session_id"]

        time.sleep(0.5)

        # 2. Start session PKG-API-02 (auto-chains and finalizes PKG-API-01)
        payload2 = json.dumps({"barcode": "PKG-API-02"}).encode()
        req2 = urllib.request.Request(
            f"{BASE_URL}/api/session/start",
            data=payload2,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req2) as resp:
            self.assertEqual(resp.status, 200)
            data2 = json.loads(resp.read().decode())
            self.assertTrue(data2["success"])
            self.assertEqual(data2["barcode"], "PKG-API-02")
            id2 = data2["session_id"]

        time.sleep(0.5)

        # 3. Finish PKG-API-02
        payload_fin = json.dumps({"reason": "API_TEST_FINISH"}).encode()
        req_fin = urllib.request.Request(
            f"{BASE_URL}/api/session/finish",
            data=payload_fin,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_fin) as resp:
            self.assertEqual(resp.status, 200)
            data_fin = json.loads(resp.read().decode())
            self.assertTrue(data_fin["success"])

        self._wait_for_completed([id1, id2])

    def test_03_sessions_search_and_listing(self):
        req = urllib.request.Request(f"{BASE_URL}/api/sessions?q=PKG-API")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertIn("sessions", data)
            self.assertGreaterEqual(len(data["sessions"]), 1)
            barcodes = [s["barcode"] for s in data["sessions"]]
            self.assertIn("PKG-API-01", barcodes)

    def test_04_settings_endpoint(self):
        # Read settings
        req = urllib.request.Request(f"{BASE_URL}/api/settings")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            settings = json.loads(resp.read().decode())
            self.assertIn("station_id", settings)

        # Update setting
        update_payload = json.dumps({"station_id": "Station 1 - High Volume"}).encode()
        req_up = urllib.request.Request(
            f"{BASE_URL}/api/settings",
            data=update_payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_up) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode())
            self.assertTrue(res["success"])

    def test_05_clip_streaming_and_download(self):
        # 1. Fetch sessions list to find a completed clip
        req = urllib.request.Request(f"{BASE_URL}/api/sessions")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            completed = [
                s for s in data["sessions"]
                if s.get("status") == "completed" and s.get("clip_filename") and (s.get("file_size_bytes") or 0) > 0
            ]
            if not completed:
                self.skipTest("No completed clips available for test")
            fn = completed[0]["clip_filename"]

        # 2. Test streaming header (Accept-Ranges)
        req_stream = urllib.request.Request(f"{BASE_URL}/clips/{fn}")
        with urllib.request.urlopen(req_stream) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("Content-Type"), "video/mp4")
            self.assertEqual(resp.headers.get("Accept-Ranges"), "bytes")

        # 3. Test forced attachment download
        req_dl = urllib.request.Request(f"{BASE_URL}/api/clips/download/{fn}")
        with urllib.request.urlopen(req_dl) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("Content-Type"), "video/mp4")
            disp = resp.headers.get("Content-Disposition")
            self.assertIsNotNone(disp)
            self.assertIn("attachment", disp)
            self.assertIn(fn, disp)

    def test_06_delete_session_and_audit(self):
        # 1. Start a session
        payload = json.dumps({"barcode": "PKG-UNIT-TEST-DEL"}).encode()
        req_start = urllib.request.Request(
            f"{BASE_URL}/api/session/start",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_start) as resp:
            data = json.loads(resp.read().decode())
            session_id = data["session_id"]

        # Try to delete active session -> should fail
        req_del_active = urllib.request.Request(
            f"{BASE_URL}/api/session/delete",
            data=json.dumps({"id": session_id}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_del_active) as resp:
            res_fail = json.loads(resp.read().decode())
            self.assertFalse(res_fail["success"])

        # Finish session
        req_fin = urllib.request.Request(
            f"{BASE_URL}/api/session/finish",
            data=json.dumps({"reason": "TEST"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_fin) as resp:
            res_fin = json.loads(resp.read().decode())
            self.assertTrue(res_fin["success"])

        # Wait for post-roll and background H.264 finalizer completion
        self._wait_for_completed([session_id])

        # Delete finalized session -> should succeed
        req_del = urllib.request.Request(
            f"{BASE_URL}/api/session/delete",
            data=json.dumps({"id": session_id}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_del) as resp:
            res_del = json.loads(resp.read().decode())
            self.assertTrue(res_del["success"])
            self.assertEqual(res_del["deleted_id"], session_id)

    def _wait_for_completed(self, target_ids, timeout=25.0):
        deadline = time.time() + timeout
        target_set = set(target_ids)
        while time.time() < deadline:
            req = urllib.request.Request(f"{BASE_URL}/api/sessions")
            with urllib.request.urlopen(req) as resp:
                sessions = json.loads(resp.read().decode()).get("sessions", [])
                done_ids = {s["id"] for s in sessions if s["id"] in target_set and s.get("status") == "completed"}
                if done_ids == target_set:
                    return True
            time.sleep(0.25)
        return False

    def test_07_export_csv(self):
        req = urllib.request.Request(f"{BASE_URL}/api/export/csv")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/csv", resp.headers.get("Content-Type"))
            disp = resp.headers.get("Content-Disposition")
            self.assertIn("attachment", disp)
            self.assertIn("shipment_dispute_manifest", disp)
            body = resp.read().decode("utf-8")
            self.assertIn("Barcode", body)
            self.assertIn("Order_ID", body)
            self.assertIn("Carrier", body)
            self.assertIn("Status", body)
            self.assertIn("Recorded_At_UTC", body)

    def test_08_scanner_audio_static(self):
        for audio_name in ["scanner-beep.wav", "scanner-finish.wav", "scanner-error.wav", "scanner-delete.wav"]:
            req = urllib.request.Request(f"{BASE_URL}/static/audio/{audio_name}")
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                self.assertGreater(int(resp.headers.get("Content-Length", 0)), 100)

    def test_09_batch_delete_sessions(self):
        # Create two completed sessions via auto-chain + finish
        req1 = urllib.request.Request(
            f"{BASE_URL}/api/session/start",
            data=json.dumps({"barcode": "PKG-BATCH-API-1"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req1) as r1:
            id1 = json.loads(r1.read().decode())["session_id"]

        time.sleep(0.4)

        req2 = urllib.request.Request(
            f"{BASE_URL}/api/session/start",
            data=json.dumps({"barcode": "PKG-BATCH-API-2"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req2) as r2:
            id2 = json.loads(r2.read().decode())["session_id"]

        time.sleep(0.4)

        req_fin = urllib.request.Request(
            f"{BASE_URL}/api/session/finish",
            data=json.dumps({"reason": "TEST_BATCH"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_fin) as r_fin:
            self.assertTrue(json.loads(r_fin.read().decode())["success"])

        self.assertTrue(self._wait_for_completed([id1, id2]))

        # Call batch delete endpoint
        req_batch = urllib.request.Request(
            f"{BASE_URL}/api/session/delete-batch",
            data=json.dumps({"ids": [id1, id2]}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_batch) as r_batch:
            res_batch = json.loads(r_batch.read().decode())
            self.assertTrue(res_batch["success"])
            self.assertEqual(res_batch["deleted_count"], 2)
            self.assertIn(id1, res_batch["deleted_ids"])
            self.assertIn(id2, res_batch["deleted_ids"])

    def test_10_camera_diagnostic_and_simulator(self):
        # Test simulator diagnostic
        req_test = urllib.request.Request(
            f"{BASE_URL}/api/camera/test",
            data=json.dumps({"source": "simulator:demo"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req_test) as r_test:
            res = json.loads(r_test.read().decode())
            self.assertTrue(res["success"])
            self.assertEqual(res["stage"], "SIMULATOR_READY")

    def test_11_update_session_metadata(self):
        # 1. Create and finish a session
        req_start = urllib.request.Request(
            f"{BASE_URL}/api/session/start",
            data=json.dumps({"barcode": "PKG-META-TEST"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_start) as r_start:
            s_id = json.loads(r_start.read().decode())["session_id"]

        time.sleep(0.4)

        req_fin = urllib.request.Request(
            f"{BASE_URL}/api/session/finish",
            data=json.dumps({"reason": "META_TEST"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_fin) as r_fin:
            self.assertTrue(json.loads(r_fin.read().decode())["success"])

        self.assertTrue(self._wait_for_completed([s_id]))

        # 2. Update metadata with unique order ID
        unique_order_id = f"ORD-TEST-{int(time.time()*1000)}"
        meta_payload = {
            "barcode": "PKG-META-TEST",
            "order_id": unique_order_id,
            "carrier": "BlueDart Express",
            "notes": "Verified tamper seal intact"
        }
        req_meta = urllib.request.Request(
            f"{BASE_URL}/api/session/{s_id}/metadata",
            data=json.dumps(meta_payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_meta) as r_meta:
            res_meta = json.loads(r_meta.read().decode())
            self.assertTrue(res_meta["success"])

        # 3. Query search by order_id
        req_search = urllib.request.Request(f"{BASE_URL}/api/sessions?q={unique_order_id}")
        with urllib.request.urlopen(req_search) as r_search:
            res_search = json.loads(r_search.read().decode())
            sessions = res_search.get("sessions", [])
            self.assertEqual(len(sessions), 1)
            s = sessions[0]
            self.assertEqual(s["order_id"], unique_order_id)
            self.assertEqual(s["carrier"], "BlueDart Express")
            self.assertEqual(s["notes"], "Verified tamper seal intact")


if __name__ == "__main__":
    unittest.main(verbosity=2)


