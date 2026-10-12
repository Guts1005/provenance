"""
Provenance Local Update Staging Server.
Simulates a live release server hosting an update package (e.g. v2.1.0)
for zero-friction local testing and verification of the auto-updater engine.
Zero em-dashes, strictly production-grade.
"""

import os
import sys
import json
import hashlib
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(REPO_ROOT, "dist")
SETUP_EXE = os.path.join(DIST_DIR, "Setup_Provenance.exe")


def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


class LocalUpdateHandler(BaseHTTPRequestHandler):
    version = "2.1.0"
    port = 5895

    def log_message(self, format, *args):
        sys.stderr.write(f"[LOCAL-UPDATE-SERVER] {self.address_string()} - {format % args}\n")

    def do_GET(self):
        if self.path in ("/manifest.json", "/update_manifest.json"):
            if not os.path.exists(SETUP_EXE):
                self.send_error(404, "Setup_Provenance.exe not found in dist/")
                return

            size = os.path.getsize(SETUP_EXE)
            sha256_hash = compute_sha256(SETUP_EXE)
            manifest = {
                "latest_version": self.version,
                "release_date": "2026-10-09",
                "download_url": f"http://127.0.0.1:{self.port}/Setup_Provenance.exe",
                "sha256": sha256_hash,
                "download_size_bytes": size,
                "mandatory": False,
                "release_notes": [
                    f"Provenance Dispatch v{self.version} Industrial Performance Release",
                    "Real-time background update streaming with SHA-256 verification",
                    "Seamless maintenance mode process replacement without operator friction",
                    "Zero downtime packing station workflow"
                ]
            }
            body = json.dumps(manifest, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/Setup_Provenance.exe":
            if not os.path.exists(SETUP_EXE):
                self.send_error(404, "Setup_Provenance.exe not found")
                return

            size = os.path.getsize(SETUP_EXE)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", f'attachment; filename="Setup_Provenance_{self.version}.exe"')
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            with open(SETUP_EXE, "rb") as f:
                while chunk := f.read(65536):
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        break
        else:
            self.send_error(404, "Not Found")


def run_server(port: int = 5895, version: str = "2.1.0"):
    LocalUpdateHandler.port = port
    LocalUpdateHandler.version = version

    if not os.path.exists(SETUP_EXE):
        print(f"[ERROR] Installer executable missing: {SETUP_EXE}")
        print("Please build Setup_Provenance.exe first or verify dist/ directory.")
        sys.exit(1)

    server = HTTPServer(("127.0.0.1", port), LocalUpdateHandler)
    url = f"http://127.0.0.1:{port}/manifest.json"
    print("=" * 65)
    print("PROVENANCE LOCAL UPDATE STAGING SERVER ACTIVE")
    print("=" * 65)
    print(f"Staging Version:  v{version}")
    print(f"Target Binary:    {SETUP_EXE} ({os.path.getsize(SETUP_EXE):,} bytes)")
    print(f"Manifest URL:     {url}")
    print("=" * 65)
    print("HOW TO TEST IN PROVENANCE UI:")
    print(f"1. Open Settings -> Software Updates")
    print(f"2. Enter Update Source: {url}")
    print(f"3. Click 'Save Source', then click 'Check for Updates'")
    print(f"4. The UI will discover v{version} and show the download option!")
    print("=" * 65)
    print("Press Ctrl+C to terminate local server when done.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[LOCAL-UPDATE-SERVER] Shutting down.")
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local update staging server for Provenance.")
    parser.add_argument("--port", type=int, default=5895, help="Listening port (default: 5895)")
    parser.add_argument("--version", default="2.1.0", help="Staged release version (default: 2.1.0)")
    args = parser.parse_args()
    run_server(port=args.port, version=args.version)
