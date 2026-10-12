"""
Automated Test Suite for Barcode Test Shipment CCTV Proof System.
Verifies Database WAL resilience, Video Engine pre-roll & chaining,
Watermark stamping, SHA-256 hash generation, and Server REST APIs.
"""

import os
import sys
import time
import json
import sqlite3
import hashlib
import unittest
from unittest import mock
import numpy as np

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import database
import video_engine


class TestDatabaseLayer(unittest.TestCase):
    def setUp(self):
        database.init_db()

    def test_database_connection_and_wal_mode(self):
        with database.get_connection() as conn:
            cur = conn.execute("PRAGMA journal_mode;")
            mode = cur.fetchone()[0]
            self.assertEqual(mode.lower(), "wal")

    def test_create_and_complete_session(self):
        barcode = "TEST-UNIT-9901"
        station = "Bench-A1"
        source = "webcam:0"
        session_id = database.create_session(barcode, station, source)
        self.assertIsInstance(session_id, int)
        self.assertGreater(session_id, 0)

        # Check active session
        active = database.get_active_session()
        self.assertIsNotNone(active)
        self.assertEqual(active["barcode"], barcode)
        self.assertEqual(active["status"], "recording")

        # Create dummy file to test SHA-256 and finish
        dummy_clip = os.path.join(database.CLIPS_DIR, "test_clip_dummy.mp4")
        with open(dummy_clip, "wb") as f:
            f.write(b"SAMPLE_MP4_VIDEO_FRAME_BYTES_FOR_TESTING")

        sha = database.calculate_sha256(dummy_clip)
        self.assertEqual(sha, hashlib.sha256(b"SAMPLE_MP4_VIDEO_FRAME_BYTES_FOR_TESTING").hexdigest())

        # Complete session
        completed = database.complete_session(
            session_id=session_id,
            end_time="2026-09-26T02:00:00Z",
            duration_seconds=12.5,
            clip_path=dummy_clip,
            status="completed",
            reason="MANUAL_TEST"
        )
        self.assertIsNotNone(completed)
        self.assertEqual(completed["status"], "completed")

        # Verify search retrieves it
        results = database.search_sessions("TEST-UNIT-9901")
        self.assertGreaterEqual(len(results), 1)
        found = results[0]
        self.assertEqual(found["barcode"], barcode)
        self.assertEqual(found["status"], "completed")
        self.assertEqual(found["sha256_hash"], sha)

        # Clean up dummy file
        if os.path.exists(dummy_clip):
            os.remove(dummy_clip)

    def test_audit_logs(self):
        database.log_audit("TEST_SYSTEM_START", {"agent": "Antigravity", "level": "production"})
        logs = database.get_recent_audit_logs(limit=5)
        self.assertGreaterEqual(len(logs), 1)
        event_types = [l["event_type"] for l in logs]
        self.assertIn("TEST_SYSTEM_START", event_types)

    def test_settings_storage(self):
        database.set_setting("test_key", "test_value_123")
        val = database.get_setting("test_key")
        self.assertEqual(val, "test_value_123")

    def test_batch_delete_sessions(self):
        # Create 3 sessions: complete 2, keep 1 recording
        s1 = database.create_session("BATCH-DEL-01", "Bench-A1", "webcam:0")
        s2 = database.create_session("BATCH-DEL-02", "Bench-A1", "webcam:0")
        s3 = database.create_session("BATCH-DEL-ACTIVE", "Bench-A1", "webcam:0")

        clip1 = os.path.join(database.CLIPS_DIR, "batch_dummy_1.mp4")
        clip2 = os.path.join(database.CLIPS_DIR, "batch_dummy_2.mp4")
        with open(clip1, "wb") as f:
            f.write(b"DUMMY_BYTES_1")
        with open(clip2, "wb") as f:
            f.write(b"DUMMY_BYTES_2")

        database.complete_session(s1, "2026-09-29T06:00:00Z", 5.0, clip1, "completed", "TEST")
        database.complete_session(s2, "2026-09-29T06:01:00Z", 6.0, clip2, "completed", "TEST")

        # Execute batch delete across all 3 (s3 is still 'recording' and must be protected)
        result = database.delete_sessions_batch([s1, s2, s3])
        self.assertEqual(result["deleted_count"], 2)
        self.assertIn(s1, result["deleted_ids"])
        self.assertIn(s2, result["deleted_ids"])
        self.assertIn(s3, result["skipped_ids"])

        # Physical files for s1 and s2 must be removed
        self.assertFalse(os.path.exists(clip1))
        self.assertFalse(os.path.exists(clip2))

        # Clean up s3
        database.complete_session(s3, "2026-09-29T06:02:00Z", 3.0, "", "completed", "TEST")
        database.delete_session(s3)



class TestVideoEngine(unittest.TestCase):
    def test_engine_initialization(self):
        self.assertIsNotNone(video_engine.engine)
        self.assertIsInstance(video_engine.engine, video_engine.VideoEngine)

    def test_watermark_stamp_frame(self):
        # Create a test black frame (480, 640, 3)
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        stamped = video_engine.engine._stamp_frame(dummy_frame, "PKG-WATERMARK-TEST")
        self.assertEqual(stamped.shape, dummy_frame.shape)
        # Verify watermark banner at bottom is not completely black (contains text/banner pixels)
        bottom_strip = stamped[450:480, :]
        self.assertGreater(np.sum(bottom_strip), 0)

    def test_start_and_auto_chain_session(self):
        engine = video_engine.engine

        # Start package 1
        res1 = engine.start_session("TEST-CHAIN-01")
        self.assertTrue(res1["success"])
        self.assertEqual(engine.active_barcode, "TEST-CHAIN-01")
        session_id_1 = res1["session_id"]

        time.sleep(0.3)

        # Scan package 2 while package 1 is still recording -> auto-chain!
        res2 = engine.start_session("TEST-CHAIN-02")
        self.assertTrue(res2["success"])
        self.assertEqual(engine.active_barcode, "TEST-CHAIN-02")
        session_id_2 = res2["session_id"]
        self.assertNotEqual(session_id_1, session_id_2)

        # Synchronously finish package 2 for unit test
        with engine.lock:
            engine._internal_finish_session(status="completed", reason="UNIT_TEST_FINISH")
        self.assertIsNone(engine.active_session_id)


class TestServerEndpoints(unittest.TestCase):
    def test_camera_status_data_structure(self):
        status = video_engine.engine.get_status()
        self.assertIn("is_recording", status)
        self.assertIn("is_connected", status)
        self.assertIn("connection_error", status)
        self.assertIn("actual_fps", status)
        self.assertIn("resolution", status)
        self.assertIn("camera_source", status)

    def test_parse_rtsp_url_with_at_in_password(self):
        # Raw '@' in password (e.g. Ermawk@321)
        parsed = video_engine.parse_rtsp_url("rtsp://admin:Ermawk@321@192.168.0.250:554/Streaming/Channels/101")
        self.assertTrue(parsed["valid"])
        self.assertEqual(parsed["username"], "admin")
        self.assertEqual(parsed["password"], "Ermawk@321")
        self.assertEqual(parsed["host"], "192.168.0.250")
        self.assertEqual(parsed["port"], 554)
        self.assertEqual(parsed["path"], "/Streaming/Channels/101")

        # Percent-encoded '%40' in password
        parsed_enc = video_engine.parse_rtsp_url("rtsp://admin:Ermawk%40321@192.168.0.250:554/Streaming/Channels/102")
        self.assertTrue(parsed_enc["valid"])
        self.assertEqual(parsed_enc["username"], "admin")
        self.assertEqual(parsed_enc["password"], "Ermawk@321")
        self.assertEqual(parsed_enc["path"], "/Streaming/Channels/102")

    def test_get_latest_jpeg_never_none(self):
        jpeg = video_engine.engine.get_latest_jpeg()
        self.assertIsNotNone(jpeg)
        self.assertIsInstance(jpeg, bytes)
        self.assertGreater(len(jpeg), 500)

    @mock.patch("subprocess.Popen")
    def test_reveal_endpoints(self, mock_popen):
        import server
        session_id = database.create_session("TEST-REVEAL-01", "Station 1", "webcam:0")
        resp_str = server.reveal_session_in_explorer(session_id)
        resp = json.loads(resp_str)
        self.assertTrue(resp["success"])
        self.assertTrue(mock_popen.called)

        # Test non-existent session
        resp_none = json.loads(server.reveal_session_in_explorer(999999))
        self.assertFalse(resp_none["success"])
        self.assertIn("not found", resp_none["error"].lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)

