"""
Provenance Release Manifest Generator.
Computes SHA-256 cryptographic signature, file size, and generates
the update_manifest.json and sha256 checksum files for GitHub Releases.
Zero em-dashes, strict adherence to production standards.
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime

DEFAULT_INSTALLER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist", "Setup_Provenance.exe")


def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def generate_manifest(
    installer_path: str = DEFAULT_INSTALLER,
    version: str = "2.0.0",
    repo: str = "Guts1005/provenance",
    notes: list = None,
    output_dir: str = None
) -> dict:
    if not os.path.exists(installer_path):
        raise FileNotFoundError(f"Installer binary not found at: {installer_path}")

    filename = os.path.basename(installer_path)
    file_size = os.path.getsize(installer_path)
    sha256_hash = compute_sha256(installer_path)
    release_date = datetime.utcnow().strftime("%Y-%m-%d")

    if not notes:
        notes = [
            "GitHub Releases integration with automatic update detection",
            "Hardware licensing and explorer proof integration",
            "Maintenance mode setup wizard with 1-click update and repair"
        ]

    clean_repo = repo.strip()
    if clean_repo.startswith("https://github.com/"):
        clean_repo = clean_repo[len("https://github.com/"):]
    elif clean_repo.startswith("http://github.com/"):
        clean_repo = clean_repo[len("http://github.com/"):]
    clean_repo = clean_repo.rstrip("/")
    parts = [p for p in clean_repo.split("/") if p]
    if len(parts) >= 2:
        clean_repo = f"{parts[0]}/{parts[1]}"

    download_url = f"https://github.com/{clean_repo}/releases/download/v{version}/{filename}"

    manifest = {
        "latest_version": version,
        "release_date": release_date,
        "download_url": download_url,
        "sha256": sha256_hash,
        "download_size_bytes": file_size,
        "mandatory": False,
        "release_notes": notes
    }

    if not output_dir:
        output_dir = os.path.dirname(installer_path)

    manifest_path = os.path.join(output_dir, "update_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    checksum_path = os.path.join(output_dir, f"{filename}.sha256")
    with open(checksum_path, "w", encoding="utf-8") as f:
        f.write(f"{sha256_hash} *{filename}\n")

    return {
        "manifest_path": manifest_path,
        "checksum_path": checksum_path,
        "sha256": sha256_hash,
        "size_bytes": file_size,
        "version": version,
        "download_url": download_url
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Provenance update manifest for GitHub Releases.")
    parser.add_argument("--installer", default=DEFAULT_INSTALLER, help="Path to Setup_Provenance.exe")
    parser.add_argument("--version", default="2.0.0", help="Release version number (e.g. 2.0.0)")
    parser.add_argument("--repo", default="Guts1005/provenance", help="GitHub repo (e.g. owner/repo)")
    parser.add_argument("--notes", nargs="*", help="Release note bullet items")
    args = parser.parse_args()

    try:
        res = generate_manifest(
            installer_path=args.installer,
            version=args.version,
            repo=args.repo,
            notes=args.notes
        )
        print("=" * 60)
        print("PROVENANCE UPDATE MANIFEST GENERATED")
        print("=" * 60)
        print(f"Version:      v{res['version']}")
        print(f"Installer:    {args.installer}")
        print(f"File Size:    {res['size_bytes']:,} bytes ({res['size_bytes'] / 1048576:.1f} MB)")
        print(f"SHA-256:      {res['sha256']}")
        print(f"Manifest:     {res['manifest_path']}")
        print(f"Checksum:     {res['checksum_path']}")
        print(f"Download URL: {res['download_url']}")
        print("=" * 60)
        print("GITHUB RELEASE INSTRUCTIONS:")
        print(f"1. Tag and create release 'v{res['version']}' on GitHub:")
        print(f"   https://github.com/{args.repo}/releases/new?tag=v{res['version']}")
        print("2. Upload the following assets to the release:")
        print(f"   - {os.path.basename(args.installer)}")
        print("   - update_manifest.json")
        print(f"   - {os.path.basename(res['checksum_path'])}")
        print("3. Publish release. Stations will automatically detect and verify the update!")
        print("=" * 60)
    except Exception as e:
        print(f"Error generating manifest: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
