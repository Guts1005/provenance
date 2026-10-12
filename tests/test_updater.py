"""
Unit and Integration Test Suite for Provenance Auto-Updater Module.
Verifies version comparisons, manifest parsing, GitHub Releases discovery,
offline resilience, error classification, SHA-256 integrity validation,
and active recording safeguards.
"""

import os
import sys
import json
import time
import hashlib
import tempfile
import unittest
import urllib.error
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import updater


class TestAutoUpdater(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_updates_dir = updater.UPDATES_DIR
        updater.UPDATES_DIR = self.temp_dir.name

    def tearDown(self):
        updater.UPDATES_DIR = self.original_updates_dir
        self.temp_dir.cleanup()

    def test_01_version_comparison(self):
        # newer versions
        self.assertTrue(updater.is_newer_version("2.1.0", "2.0.0"))
        self.assertTrue(updater.is_newer_version("2.0.1", "2.0.0"))
        self.assertTrue(updater.is_newer_version("3.0.0", "2.9.9"))
        self.assertTrue(updater.is_newer_version("2.10.0", "2.2.0"))

        # equal or older versions
        self.assertFalse(updater.is_newer_version("2.0.0", "2.0.0"))
        self.assertFalse(updater.is_newer_version("1.9.9", "2.0.0"))
        self.assertFalse(updater.is_newer_version("2.0.0", "2.1.0"))
        self.assertFalse(updater.is_newer_version("2.0.1b", "2.0.2"))

    def test_02_parse_manifest_valid(self):
        sample_manifest = {
            "latest_version": "2.1.0",
            "release_date": "2026-10-10",
            "download_url": "https://example.com/Setup_Provenance_2.1.0.exe",
            "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "download_size_bytes": 170000000,
            "mandatory": False,
            "release_notes": [
                "Added 1-click cloud auto-updater",
                "Optimized RTSP wire draining performance"
            ]
        }
        info = updater.parse_manifest(sample_manifest, current_version="2.0.0")
        self.assertTrue(info["update_available"])
        self.assertEqual(info["latest_version"], "2.1.0")
        self.assertEqual(info["current_version"], "2.0.0")
        self.assertEqual(len(info["release_notes"]), 2)

    def test_03_parse_manifest_up_to_date(self):
        sample_manifest = {
            "latest_version": "2.0.0",
            "download_url": "https://example.com/Setup.exe",
            "sha256": "abc"
        }
        info = updater.parse_manifest(sample_manifest, current_version="2.0.0")
        self.assertFalse(info["update_available"])
        self.assertEqual(info["latest_version"], "2.0.0")

    def test_04_offline_resilience(self):
        # Querying an unreachable non-existent local port must fail cleanly and quickly
        start_time = time.time()
        result = updater.check_for_updates(
            source="http://127.0.0.1:59991/nonexistent_manifest.json",
            timeout=1.0
        )
        elapsed = time.time() - start_time

        self.assertLess(elapsed, 2.5)
        self.assertFalse(result["update_available"])
        self.assertEqual(result["status"], "offline")
        self.assertIsNotNone(result["error"])

    def test_05_sha256_verification_and_quarantine(self):
        dummy_content = b"PROVENANCE_TEST_INSTALLER_BINARY_DATA"
        correct_hash = hashlib.sha256(dummy_content).hexdigest()
        bad_hash = "0000000000000000000000000000000000000000000000000000000000000000"

        test_file = os.path.join(self.temp_dir.name, "test_installer.exe")
        with open(test_file, "wb") as f:
            f.write(dummy_content)

        # Correct hash passes
        self.assertTrue(updater.verify_file_hash(test_file, correct_hash))
        self.assertTrue(os.path.exists(test_file))

        # Bad hash fails and removes corrupt file
        self.assertFalse(updater.verify_file_hash(test_file, bad_hash))
        self.assertFalse(os.path.exists(test_file))

    def test_06_active_recording_guard(self):
        # If recording is underway, applying update must be blocked
        with patch("updater.is_session_recording", return_value=True):
            can_apply, reason = updater.can_apply_update()
            self.assertFalse(can_apply)
            self.assertIn("recording", reason.lower())

        with patch("updater.is_session_recording", return_value=False):
            can_apply, reason = updater.can_apply_update()
            self.assertTrue(can_apply)

    def test_07_server_api_status_and_check(self):
        import server
        status_str = server.get_update_status()
        data = json.loads(status_str)
        self.assertIn("current_version", data)
        self.assertIn("status", data)
        self.assertEqual(data["current_version"], updater.CURRENT_VERSION)

    def test_08_resolve_update_source(self):
        # Shorthand GitHub repo
        res1 = updater.resolve_update_source("sharvin/provenance")
        self.assertEqual(res1["type"], "github_repo")
        self.assertEqual(res1["owner"], "sharvin")
        self.assertEqual(res1["repo"], "provenance")

        # Full GitHub repository URL
        res2 = updater.resolve_update_source("https://github.com/my-org/station-provenance")
        self.assertEqual(res2["type"], "github_repo")
        self.assertEqual(res2["owner"], "my-org")
        self.assertEqual(res2["repo"], "station-provenance")

        # GitHub Releases latest URL
        res3 = updater.resolve_update_source("https://github.com/my-org/station-provenance/releases/latest")
        self.assertEqual(res3["type"], "github_repo")
        self.assertEqual(res3["owner"], "my-org")
        self.assertEqual(res3["repo"], "station-provenance")

        # Direct manifest URL
        res4 = updater.resolve_update_source("https://example.com/updates/manifest.json")
        self.assertEqual(res4["type"], "manifest")
        self.assertEqual(res4["url"], "https://example.com/updates/manifest.json")

        # Raw GitHub manifest URL
        res5 = updater.resolve_update_source("https://raw.githubusercontent.com/org/repo/main/update_manifest.json")
        self.assertEqual(res5["type"], "manifest")

    def test_09_github_release_parsing(self):
        mock_release = {
            "tag_name": "v2.1.0",
            "published_at": "2026-10-15T08:30:00Z",
            "body": "## What is new:\n- Added barcode audit log\n- Improved RTSP frame buffer\nSHA256: 11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
            "assets": [
                {
                    "name": "Setup_Provenance_2.1.0.exe",
                    "browser_download_url": "https://github.com/org/repo/releases/download/v2.1.0/Setup_Provenance_2.1.0.exe",
                    "size": 165000000
                }
            ]
        }

        parsed = updater._parse_github_release(mock_release, owner="org", repo="repo", current_version="2.0.0")
        self.assertTrue(parsed["update_available"])
        self.assertEqual(parsed["latest_version"], "2.1.0")
        self.assertEqual(parsed["current_version"], "2.0.0")
        self.assertEqual(parsed["release_date"], "2026-10-15")
        self.assertEqual(parsed["download_size_bytes"], 165000000)
        self.assertEqual(parsed["sha256"], "11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff")
        self.assertIn("Added barcode audit log", parsed["release_notes"])

    def test_10_http_error_distinction_not_offline(self):
        # 404 Not Found must be classified as error, not false offline
        http_404 = urllib.error.HTTPError(
            url="https://api.github.com/repos/org/nonexistent/releases/latest",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None
        )

        with patch("urllib.request.urlopen", side_effect=http_404):
            res = updater.check_github_releases(owner="org", repo="nonexistent", timeout=1.0)
            self.assertEqual(res["status"], "error")
            self.assertFalse(res["update_available"])
            self.assertIn("404", res["error"])

        # 403 Rate Limit must also be classified as error, not false offline
        http_403 = urllib.error.HTTPError(
            url="https://api.github.com/repos/org/repo/releases/latest",
            code=403,
            msg="rate limit exceeded",
            hdrs={},
            fp=None
        )

        with patch("urllib.request.urlopen", side_effect=http_403):
            res = updater.check_github_releases(owner="org", repo="repo", timeout=1.0)
            self.assertEqual(res["status"], "error")
            self.assertIn("rate limit", res["error"].lower())


if __name__ == "__main__":
    unittest.main()
