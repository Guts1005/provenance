"""
Provenance Enterprise Auto-Updater Engine.
Handles update discovery, manifest validation, background streaming downloads,
SHA-256 cryptographic verification, and safe Windows process replacement.
Zero cloud vendor lock-in, zero em-dashes, 100% air-gapped resilient.
"""

import os
import sys
import re
import json
import time
import socket
import hashlib
import threading
import subprocess
import urllib.request
import urllib.error

import database

CURRENT_VERSION = "2.0.11"
DEFAULT_UPDATE_SOURCE = "Guts1005/provenance"
DEFAULT_MANIFEST_URL = DEFAULT_UPDATE_SOURCE

# Directory for staging updates
UPDATES_DIR = os.path.join(database.get_app_dir(), "updates")


def ensure_updates_dir() -> str:
    os.makedirs(UPDATES_DIR, exist_ok=True)
    return UPDATES_DIR


def is_loopback_target(target: str) -> bool:
    """Return True if target points to localhost or loopback interface."""
    t = (target or "").lower()
    return "127.0.0.1" in t or "localhost" in t or "::1" in t


def has_internet_connectivity(timeout: float = 0.8) -> bool:
    """
    Fast, non-blocking outbound socket test to check if workstation has general internet access.
    Tries Cloudflare DNS (1.1.1.1:53), Google DNS (8.8.8.8:53), or GitHub (443).
    """
    endpoints = [("1.1.1.1", 53), ("8.8.8.8", 53), ("github.com", 443)]
    for host, port in endpoints:
        try:
            s = socket.create_connection((host, port), timeout=timeout)
            s.close()
            return True
        except Exception:
            continue
    return False


def parse_version(v_str: str) -> tuple:
    """Parse version string into tuple of integers for reliable semantic comparison."""
    if not v_str:
        return (0, 0, 0)
    # Strip leading 'v' or 'V' and non-numeric suffixes
    clean = re.sub(r'^[vV]', '', str(v_str).strip())
    # Extract digit sequences
    parts = re.findall(r'\d+', clean)
    if not parts:
        return (0, 0, 0)
    return tuple(int(p) for p in parts[:3])


def is_newer_version(latest_str: str, current_str: str = CURRENT_VERSION) -> bool:
    """Return True if latest_str is strictly newer than current_str."""
    return parse_version(latest_str) > parse_version(current_str)


def resolve_update_source(source_str: str = None) -> dict:
    """
    Parse update source into structured target.
    Supports GitHub repositories (owner/repo or https://github.com/owner/repo)
    and direct JSON manifest URLs.
    """
    s = (source_str or "").strip()
    if not s:
        s = DEFAULT_UPDATE_SOURCE

    # If old placeholder URL was saved, normalize to default GitHub repo
    if s == "https://raw.githubusercontent.com/provenance-dispatch/releases/main/update_manifest.json":
        s = DEFAULT_UPDATE_SOURCE

    # Check if direct manifest file or raw github file
    if s.endswith(".json") or "raw.githubusercontent.com" in s or "gist.githubusercontent.com" in s:
        return {"type": "manifest", "url": s}

    # Match GitHub repository URLs: https://github.com/owner/repo[/releases/...]
    m_url = re.match(
        r'^(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:[/?#].*)?$',
        s,
        re.I
    )
    if m_url:
        owner = m_url.group(1).strip()
        repo = re.sub(r'\.git$', '', m_url.group(2)).strip()
        return {"type": "github_repo", "owner": owner, "repo": repo}

    # Match GitHub shorthand owner/repo with optional /releases suffix
    m_short_rel = re.match(r'^([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)/(?:releases(?:/latest)?)/?$', s, re.I)
    if m_short_rel:
        return {"type": "github_repo", "owner": m_short_rel.group(1), "repo": m_short_rel.group(2)}

    # Match GitHub shorthand owner/repo: e.g. "Guts1005/provenance" or "provenance-dispatch/releases"
    m_short = re.match(r'^([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)$', s)
    if m_short:
        return {"type": "github_repo", "owner": m_short.group(1), "repo": m_short.group(2)}

    # Fallback to direct manifest URL
    if not s.startswith("http://") and not s.startswith("https://"):
        s = "https://" + s
    return {"type": "manifest", "url": s}


def parse_manifest(manifest: dict, current_version: str = CURRENT_VERSION) -> dict:
    """Validate and normalize manifest payload."""
    latest_version = str(manifest.get("latest_version", "2.0.0")).strip()
    download_url = str(manifest.get("download_url", "")).strip()
    sha256_hash = str(manifest.get("sha256", "")).strip().lower()
    release_date = str(manifest.get("release_date", "")).strip()
    mandatory = bool(manifest.get("mandatory", False))
    size_bytes = int(manifest.get("download_size_bytes", 0))

    raw_notes = manifest.get("release_notes", [])
    if isinstance(raw_notes, str):
        notes = [n.strip() for n in raw_notes.split("\n") if n.strip()]
    elif isinstance(raw_notes, list):
        notes = [str(n).strip() for n in raw_notes if str(n).strip()]
    else:
        notes = []

    has_update = is_newer_version(latest_version, current_version) and bool(download_url)

    return {
        "status": "available" if has_update else "up_to_date",
        "update_available": has_update,
        "current_version": current_version,
        "latest_version": latest_version,
        "release_date": release_date,
        "download_url": download_url,
        "sha256": sha256_hash,
        "download_size_bytes": size_bytes,
        "mandatory": mandatory,
        "release_notes": notes,
        "error": None
    }


def _parse_github_release(release: dict, owner: str, repo: str, current_version: str = CURRENT_VERSION, timeout: float = 2.5) -> dict:
    """Parse GitHub Releases API payload into update metadata."""
    tag_name = str(release.get("tag_name", "")).strip()
    latest_version = re.sub(r'^[vV]', '', tag_name) or "2.0.0"
    published_at = str(release.get("published_at", ""))[:10]
    body = str(release.get("body", "") or "")
    assets = release.get("assets", [])

    # Check for update_manifest.json asset first
    for asset in assets:
        if asset.get("name") == "update_manifest.json":
            manifest_url = asset.get("browser_download_url")
            if manifest_url:
                try:
                    m_req = urllib.request.Request(
                        manifest_url,
                        headers={"User-Agent": f"Provenance-Station/{current_version}"}
                    )
                    with urllib.request.urlopen(m_req, timeout=timeout) as m_resp:
                        if m_resp.status == 200:
                            m_data = json.loads(m_resp.read().decode("utf-8"))
                            return parse_manifest(m_data, current_version=current_version)
                except Exception as ex:
                    print(f"[UPDATER] Could not read manifest asset: {ex}", flush=True)

    # Find the best Windows executable asset
    exe_asset = None
    for asset in assets:
        name = asset.get("name", "")
        if name.lower().endswith(".exe"):
            if "setup_provenance" in name.lower() or "provenance" in name.lower():
                exe_asset = asset
                break
            elif not exe_asset:
                exe_asset = asset

    if not exe_asset:
        return {
            "status": "error",
            "update_available": False,
            "current_version": current_version,
            "error": f"Release '{tag_name}' in repository '{owner}/{repo}' does not contain an installer executable (.exe)."
        }

    download_url = exe_asset.get("browser_download_url", "")
    download_size = int(exe_asset.get("size", 0))

    # Look for SHA-256 hash in checksum assets or release notes
    sha256_hash = ""
    for asset in assets:
        name = asset.get("name", "").lower()
        if name.endswith(".sha256") or name in ("checksums.txt", "sha256.txt"):
            cs_url = asset.get("browser_download_url")
            if cs_url:
                try:
                    cs_req = urllib.request.Request(
                        cs_url,
                        headers={"User-Agent": f"Provenance-Station/{current_version}"}
                    )
                    with urllib.request.urlopen(cs_req, timeout=timeout) as cs_resp:
                        cs_text = cs_resp.read().decode("utf-8", errors="ignore")
                        for line in cs_text.splitlines():
                            if exe_asset.get("name") in line:
                                m = re.search(r'[a-fA-F0-9]{64}', line)
                                if m:
                                    sha256_hash = m.group(0).lower()
                                    break
                        if not sha256_hash:
                            m = re.search(r'[a-fA-F0-9]{64}', cs_text)
                            if m:
                                sha256_hash = m.group(0).lower()
                except Exception:
                    pass
            if sha256_hash:
                break

    if not sha256_hash and body:
        m = re.search(r'(?:sha-?256|hash)\s*[:=]\s*([a-fA-F0-9]{64})', body, re.I)
        if m:
            sha256_hash = m.group(1).lower()

    # Extract clean release notes from markdown body
    notes = []
    if body:
        for line in body.splitlines():
            clean_line = line.strip()
            if not clean_line or clean_line.startswith("#"):
                continue
            clean_line = re.sub(r'^[\*\-\+\s]+', '', clean_line).strip()
            if clean_line:
                notes.append(clean_line)

    has_update = is_newer_version(latest_version, current_version) and bool(download_url)

    return {
        "status": "available" if has_update else "up_to_date",
        "update_available": has_update,
        "current_version": current_version,
        "latest_version": latest_version,
        "release_date": published_at,
        "download_url": download_url,
        "sha256": sha256_hash,
        "download_size_bytes": download_size,
        "mandatory": False,
        "release_notes": notes[:10],
        "error": None
    }


def check_github_releases(owner: str, repo: str, current_version: str = CURRENT_VERSION, timeout: float = 2.5) -> dict:
    """Query GitHub Releases API with graceful error categorization."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    req = urllib.request.Request(
        api_url,
        headers={
            "User-Agent": f"Provenance-Station/{current_version}",
            "Accept": "application/vnd.github.v3+json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                release_data = json.loads(resp.read().decode("utf-8"))
                return _parse_github_release(release_data, owner=owner, repo=repo, current_version=current_version, timeout=timeout)
            else:
                return {
                    "status": "error",
                    "update_available": False,
                    "current_version": current_version,
                    "error": f"GitHub returned HTTP status {resp.status}"
                }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Fallback check: see if a raw manifest exists in repo main or master branch
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/update_manifest.json"
            try:
                raw_req = urllib.request.Request(
                    raw_url,
                    headers={"User-Agent": f"Provenance-Station/{current_version}"}
                )
                with urllib.request.urlopen(raw_req, timeout=timeout) as raw_resp:
                    if raw_resp.status == 200:
                        manifest_data = json.loads(raw_resp.read().decode("utf-8"))
                        return parse_manifest(manifest_data, current_version=current_version)
            except Exception:
                pass

            return {
                "status": "error",
                "update_available": False,
                "current_version": current_version,
                "error": f"No published releases or update_manifest.json found in repository '{owner}/{repo}'. (HTTP 404)"
            }
        elif e.code in (403, 429):
            return {
                "status": "error",
                "update_available": False,
                "current_version": current_version,
                "error": "GitHub API rate limit exceeded. Please wait a few moments before retrying."
            }
        elif e.code == 401:
            return {
                "status": "error",
                "update_available": False,
                "current_version": current_version,
                "error": f"Repository '{owner}/{repo}' is private or requires authentication."
            }
        else:
            return {
                "status": "error",
                "update_available": False,
                "current_version": current_version,
                "error": f"GitHub service returned HTTP {e.code}"
            }
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionRefusedError, OSError) as e:
        if has_internet_connectivity():
            err_msg = f"Could not reach GitHub Releases API for '{owner}/{repo}': {str(e)}"
        else:
            err_msg = "Workstation is offline or air-gapped. Network is unreachable."
        return {
            "status": "offline",
            "update_available": False,
            "current_version": current_version,
            "error": err_msg
        }
    except Exception as e:
        return {
            "status": "error",
            "update_available": False,
            "current_version": current_version,
            "error": str(e)
        }


def check_manifest_url(url: str, current_version: str = CURRENT_VERSION, timeout: float = 2.5) -> dict:
    """Fetch and parse direct JSON update manifest."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Provenance-Station/{current_version}"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return parse_manifest(data, current_version=current_version)
            else:
                return {
                    "status": "error",
                    "update_available": False,
                    "current_version": current_version,
                    "error": f"Server returned HTTP {resp.status}"
                }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {
                "status": "error",
                "update_available": False,
                "current_version": current_version,
                "error": "Update manifest not found at target URL (HTTP 404)."
            }
        elif e.code in (403, 401):
            return {
                "status": "error",
                "update_available": False,
                "current_version": current_version,
                "error": f"Access denied to update manifest (HTTP {e.code})."
            }
        else:
            return {
                "status": "error",
                "update_available": False,
                "current_version": current_version,
                "error": f"Update server returned HTTP {e.code}"
            }
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionRefusedError, OSError) as e:
        if is_loopback_target(url):
            err_msg = f"Local update server is not running or connection was refused on specified port ({str(e)})."
        elif has_internet_connectivity():
            err_msg = f"Could not reach update server at '{url}'. Server may be offline or unreachable ({str(e)})."
        else:
            err_msg = "Workstation is offline or air-gapped. Network is unreachable."
        return {
            "status": "offline",
            "update_available": False,
            "current_version": current_version,
            "error": err_msg
        }
    except Exception as e:
        return {
            "status": "error",
            "update_available": False,
            "current_version": current_version,
            "error": str(e)
        }


def check_for_updates(source: str = None, timeout: float = 2.5, manifest_url: str = None) -> dict:
    """
    Check for software updates against configured update source.
    Automatically resolves GitHub repositories or direct manifest URLs.
    Resilient against offline conditions and air-gapped workstations.
    """
    target = (source or manifest_url or "").strip()
    if not target:
        target = database.get_setting("update_manifest_url", DEFAULT_UPDATE_SOURCE)

    parsed = resolve_update_source(target)
    if parsed["type"] == "github_repo":
        return check_github_releases(parsed["owner"], parsed["repo"], current_version=CURRENT_VERSION, timeout=timeout)
    else:
        return check_manifest_url(parsed["url"], current_version=CURRENT_VERSION, timeout=timeout)


def verify_file_hash(filepath: str, expected_hash: str) -> bool:
    """Verify SHA-256 hash of a file. Deletes corrupt file if hash fails."""
    if not os.path.exists(filepath):
        return False
    if not expected_hash:
        return True

    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        calc = hasher.hexdigest().lower()
        match = (calc == expected_hash.lower())
        if not match:
            print(f"[UPDATER] Hash mismatch: calc={calc} vs expected={expected_hash}", flush=True)
            try:
                os.remove(filepath)
            except Exception:
                pass
            return False
        return True
    except Exception as e:
        print(f"[UPDATER] Hash verification error: {e}", flush=True)
        try:
            os.remove(filepath)
        except Exception:
            pass
        return False


def is_session_recording() -> bool:
    """Check if an active packing/recording session is underway."""
    try:
        import video_engine
        if getattr(video_engine.engine, "is_recording", False):
            return True
    except Exception:
        pass

    try:
        active = database.get_active_session()
        if active and active.get("status") == "recording":
            return True
    except Exception:
        pass

    return False


def can_apply_update() -> tuple:
    """Verify prerequisites before launching installer."""
    if is_session_recording():
        return False, "Cannot apply update while a recording session is active. Finish or cancel current carton first."
    return True, ""


class UpdaterManager:
    """Thread-safe singleton managing update lifecycle and background workers."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(UpdaterManager, cls).__new__(cls)
                cls._instance._init_state()
            return cls._instance

    def _init_state(self):
        self.state_lock = threading.Lock()
        self.status = "idle"  # idle, checking, available, up_to_date, downloading, ready_to_install, error, offline
        self.current_version = CURRENT_VERSION
        self.latest_version = CURRENT_VERSION
        self.release_date = ""
        self.release_notes = []
        self.download_url = ""
        self.sha256 = ""
        self.total_bytes = 0
        self.downloaded_bytes = 0
        self.download_percent = 0
        self.downloaded_file = ""
        self.last_checked_at = None
        self.last_error = None
        self.is_checking = False
        self.is_downloading = False

    def get_status_dict(self) -> dict:
        with self.state_lock:
            ready = False
            if self.downloaded_file and os.path.exists(self.downloaded_file):
                if is_newer_version(self.latest_version, self.current_version):
                    ready = True

            effective_status = self.status
            if ready and self.status not in ("error", "offline"):
                effective_status = "ready_to_install"

            return {
                "status": effective_status,
                "current_version": self.current_version,
                "latest_version": self.latest_version,
                "update_available": is_newer_version(self.latest_version, self.current_version),
                "release_date": self.release_date,
                "release_notes": self.release_notes,
                "download_url": self.download_url,
                "download_size_bytes": self.total_bytes,
                "downloaded_bytes": self.downloaded_bytes,
                "download_percent": self.download_percent,
                "downloaded_file": self.downloaded_file,
                "is_checking": self.is_checking,
                "is_downloading": self.is_downloading,
                "last_checked_at": self.last_checked_at,
                "last_error": self.last_error
            }

    def check_for_updates_async(self, manifest_url: str = None):
        """Trigger background check without blocking caller."""
        with self.state_lock:
            if self.is_checking:
                return
            self.is_checking = True
            self.status = "checking"
            self.last_error = None

        thread = threading.Thread(target=self._check_worker, args=(manifest_url,), daemon=True)
        thread.start()

    def _check_worker(self, manifest_url: str = None):
        result = check_for_updates(source=manifest_url)
        with self.state_lock:
            self.is_checking = False
            self.last_checked_at = datetime_now_iso()
            self.status = result.get("status", "idle")
            self.last_error = result.get("error")
            if result.get("update_available"):
                self.latest_version = result.get("latest_version")
                self.release_date = result.get("release_date")
                self.release_notes = result.get("release_notes", [])
                self.download_url = result.get("download_url")
                self.sha256 = result.get("sha256")
                self.total_bytes = result.get("download_size_bytes", 0)
            elif result.get("status") == "up_to_date":
                self.latest_version = result.get("latest_version", self.current_version)

    def download_update_async(self):
        """Trigger background download thread."""
        with self.state_lock:
            if self.is_downloading:
                return
            if not self.download_url:
                self.last_error = "No download URL available. Please check for updates first."
                self.status = "error"
                return
            self.is_downloading = True
            self.status = "downloading"
            self.download_percent = 0
            self.downloaded_bytes = 0
            self.last_error = None

        thread = threading.Thread(target=self._download_worker, daemon=True)
        thread.start()

    def _download_worker(self):
        ensure_updates_dir()
        url = self.download_url
        expected_hash = self.sha256
        filename = f"Setup_Provenance_{self.latest_version}.exe"
        target_path = os.path.join(UPDATES_DIR, filename)
        part_path = target_path + ".part"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": f"Provenance-Updater/{CURRENT_VERSION}"}
            )
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                total_size = int(resp.headers.get("Content-Length", 0))
                with self.state_lock:
                    if total_size > 0:
                        self.total_bytes = total_size
                    elif self.total_bytes > 0:
                        total_size = self.total_bytes

                hasher = hashlib.sha256()
                downloaded = 0

                with open(part_path, "wb") as f:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                        hasher.update(chunk)
                        downloaded += len(chunk)
                        pct = int((downloaded / total_size) * 100) if total_size > 0 else 50
                        with self.state_lock:
                            self.downloaded_bytes = downloaded
                            self.download_percent = pct

                calc_hash = hasher.hexdigest().lower()
                if expected_hash and calc_hash != expected_hash.lower():
                    if os.path.exists(part_path):
                        os.remove(part_path)
                    raise ValueError("Security validation failed: SHA-256 hash mismatch.")

                # Move part file to final installer target
                if os.path.exists(target_path):
                    try:
                        os.remove(target_path)
                    except Exception:
                        pass
                os.replace(part_path, target_path)

                with self.state_lock:
                    self.is_downloading = False
                    self.status = "ready_to_install"
                    self.downloaded_file = target_path
                    self.download_percent = 100
                    print(f"[UPDATER] Update downloaded and validated: {target_path}", flush=True)

        except Exception as e:
            if os.path.exists(part_path):
                try:
                    os.remove(part_path)
                except Exception:
                    pass
            with self.state_lock:
                self.is_downloading = False
                self.status = "error"
                self.last_error = str(e)
                print(f"[UPDATER] Download failed: {e}", flush=True)


def datetime_now_iso() -> str:
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


manager = UpdaterManager()


def apply_update(installer_path: str = None, silent: bool = True) -> tuple:
    """
    Launch the downloaded installer in a detached Windows process and exit Provenance cleanly.
    """
    can_apply, reason = can_apply_update()
    if not can_apply:
        return False, reason

    if not installer_path:
        status_info = manager.get_status_dict()
        installer_path = status_info.get("downloaded_file")

    if not installer_path or not os.path.exists(installer_path):
        return False, "Installer file not found on disk. Please download update first."

    # Validate hash once more before execution
    expected_hash = manager.sha256
    if expected_hash and not verify_file_hash(installer_path, expected_hash):
        return False, "Installer security hash check failed. File purged."

    print(f"[UPDATER] Launching installer: {installer_path}", flush=True)

    args = [installer_path]
    if silent:
        args.extend(["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "--auto-update"])

    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            param_str = " ".join(args[1:]) if len(args) > 1 else ""
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                hwnd = ctypes.windll.user32.GetDesktopWindow()

            class SHELLEXECUTEINFOW(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("fMask", wintypes.ULONG),
                    ("hwnd", wintypes.HWND),
                    ("lpVerb", wintypes.LPCWSTR),
                    ("lpFile", wintypes.LPCWSTR),
                    ("lpParameters", wintypes.LPCWSTR),
                    ("lpDirectory", wintypes.LPCWSTR),
                    ("nShow", ctypes.c_int),
                    ("hInstApp", wintypes.HINSTANCE),
                    ("lpIDList", ctypes.c_void_p),
                    ("lpClass", wintypes.LPCWSTR),
                    ("hkeyClass", wintypes.HKEY),
                    ("dwHotKey", wintypes.DWORD),
                    ("hIcon", wintypes.HANDLE),
                    ("hProcess", wintypes.HANDLE),
                ]

            sei = SHELLEXECUTEINFOW()
            sei.cbSize = ctypes.sizeof(sei)
            sei.fMask = 0x00000040  # SEE_MASK_NOCLOSEPROCESS
            sei.hwnd = hwnd
            sei.lpVerb = "runas"
            sei.lpFile = installer_path
            sei.lpParameters = param_str
            sei.nShow = 1

            success = ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei))
            if not success:
                err = ctypes.GetLastError()
                if err == 1223:  # ERROR_CANCELLED by user
                    return False, "Update was cancelled at the Windows security prompt."
                # Fallback to standard open
                sei.lpVerb = "open"
                success = ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei))
                if not success:
                    err2 = ctypes.GetLastError()
                    return False, f"Could not launch update installer: Windows error code {err2}"
        else:
            subprocess.Popen(
                args,
                close_fds=True,
                shell=False
            )

        # Trigger clean exit of main application after 0.8s so Windows file lock is released
        def delayed_exit():
            time.sleep(0.8)
            os._exit(0)

        threading.Thread(target=delayed_exit, daemon=True).start()
        return True, "Update installer launched. Application restarting..."
    except Exception as e:
        print(f"[UPDATER] Failed to execute installer: {e}", flush=True)
        return False, f"Failed to execute installer: {str(e)}"
