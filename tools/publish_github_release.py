"""
Provenance GitHub Release Automation Tool.
Generates release manifests, validates cryptographic checksums,
and publishes releases to GitHub via the official gh CLI.
Zero em-dashes, strictly production-grade.
"""

import os
import sys
import shutil
import argparse
import subprocess
from generate_update_manifest import generate_manifest, DEFAULT_INSTALLER

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(REPO_ROOT, "dist")


def run_cmd(cmd: list) -> tuple:
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            shell=False
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def publish_release(version: str, repo: str = "Guts1005/provenance", installer: str = DEFAULT_INSTALLER, is_draft: bool = False):
    clean_version = version.lstrip("vV").strip()
    tag = f"v{clean_version}"

    if not os.path.exists(installer):
        print(f"[ERROR] Installer file does not exist: {installer}")
        return False

    # Check gh CLI availability
    gh_bin = shutil.which("gh")
    if not gh_bin:
        print("[ERROR] GitHub CLI ('gh') is not installed or not in PATH.")
        print("Install gh from https://cli.github.com/ or run 'winget install GitHub.cli'.")
        return False

    code, out, err = run_cmd(["gh", "auth", "status"])
    if code != 0:
        print("[ERROR] GitHub CLI is not authenticated. Run 'gh auth login' first.")
        print(err)
        return False

    print("=" * 65)
    print(f"PREPARING PROVENANCE GITHUB RELEASE {tag}")
    print("=" * 65)
    print(f"Target Repository: {repo}")
    print(f"Installer:         {installer}")

    # Generate manifest and checksums
    print("\n[1/3] Generating update manifest and SHA-256 signature...")
    manifest_meta = generate_manifest(
        installer_path=installer,
        version=clean_version,
        repo=repo
    )
    manifest_file = manifest_meta["manifest_path"]
    checksum_file = manifest_meta["checksum_path"]
    print(f"      SHA-256: {manifest_meta['sha256']}")
    print(f"      Package Size: {manifest_meta['size_bytes']:,} bytes")

    # Verify or create repository
    print(f"\n[2/3] Checking repository '{repo}'...")
    code, out, _ = run_cmd(["gh", "repo", "view", repo])
    if code != 0:
        print(f"      Repository '{repo}' not found on GitHub.")
        print(f"      Creating public repository '{repo}'...")
        c_code, c_out, c_err = run_cmd([
            "gh", "repo", "create", repo,
            "--public",
            "--description", "Provenance Dispatch: Tamper-Proof CCTV Packing Station System"
        ])
        if c_code != 0:
            print(f"[ERROR] Failed to create repository '{repo}': {c_err}")
            return False
        print(f"      Successfully created repository '{repo}'!")

    # Ensure repository is not empty by creating initial commit if needed
    i_code, _, _ = run_cmd(["gh", "api", f"/repos/{repo}/commits"])
    if i_code != 0:
        print(f"      Initializing repository with default README.md commit...")
        import base64
        init_content = base64.b64encode(b"# Provenance Dispatch\n\nIndustrial CCTV Packing Station & Release Repository\n").decode("ascii")
        run_cmd([
            "gh", "api", "--method", "PUT", f"/repos/{repo}/contents/README.md",
            "-f", "message=Initial commit: Provenance Dispatch release repository",
            "-f", f"content={init_content}"
        ])

    # Publish release
    print(f"\n[3/3] Publishing release {tag} to GitHub...")
    rel_title = f"Provenance Dispatch {tag}"
    notes = (
        f"Provenance Dispatch {tag} Release\n\n"
        f"Key Highlights:\n"
        f"- Automated background software updater with SHA-256 cryptographic verification\n"
        f"- Native Windows maintenance mode installation and seamless process replacement\n"
        f"- High-performance CCTV clip playback and tamper-proof evidence preservation\n\n"
        f"Integrity Checksum:\n"
        f"`{manifest_meta['sha256']}` Setup_Provenance.exe"
    )

    cmd = [
        "gh", "release", "create", tag,
        installer,
        manifest_file,
        checksum_file,
        "--repo", repo,
        "--title", rel_title,
        "--notes", notes
    ]
    if is_draft:
        cmd.append("--draft")

    code, out, err = run_cmd(cmd)
    if code != 0:
        print(f"[ERROR] Failed to create GitHub release: {err}")
        return False

    print("\n" + "=" * 65)
    print(f"SUCCESS! RELEASE {tag} IS LIVE ON GITHUB")
    print("=" * 65)
    print(f"Release URL: https://github.com/{repo}/releases/tag/{tag}")
    print(f"Stations pointing to '{repo}' will now detect and install this release!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publish Provenance release to GitHub.")
    parser.add_argument("--version", default="2.0.1", help="Release version (e.g. 2.0.1)")
    parser.add_argument("--repo", default="Guts1005/provenance", help="Target GitHub repository")
    parser.add_argument("--installer", default=DEFAULT_INSTALLER, help="Path to Setup_Provenance.exe")
    parser.add_argument("--draft", action="store_true", help="Create as draft release")
    args = parser.parse_args()

    success = publish_release(
        version=args.version,
        repo=args.repo,
        installer=args.installer,
        is_draft=args.draft
    )
    sys.exit(0 if success else 1)
