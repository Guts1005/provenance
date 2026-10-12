"""
Main Desktop Executable Entry Point for Barcode Test.
Launches the native desktop application window via PyWebView and Edge WebView2.
"""

import sys
import os
import time
import subprocess
import threading
import urllib.request
import ctypes
import ctypes.wintypes as wt

# Always run relative to project root even when double-clicked in Explorer
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def get_current_desktop_name() -> str:
    try:
        u32 = ctypes.windll.user32
        k32 = ctypes.windll.kernel32
        hdesk = u32.GetThreadDesktop(k32.GetCurrentThreadId())
        buf = ctypes.create_unicode_buffer(256)
        u32.GetUserObjectInformationW(hdesk, 2, buf, 512, None)
        return buf.value
    except Exception:
        return "Default"


def ensure_interactive_desktop() -> None:
    """If launched inside an isolated non-Default desktop (e.g. exebox-*), re-spawn on WinSta0\\Default."""
    if os.name != "nt":
        return
    desk = get_current_desktop_name()
    if desk.lower() != "default" and os.environ.get("BARCODE_DEFAULT_DESK") != "1":
        os.environ["BARCODE_DEFAULT_DESK"] = "1"

        class STARTUPINFOW(ctypes.Structure):
            _fields_ = [
                ("cb", wt.DWORD), ("lpReserved", wt.LPWSTR), ("lpDesktop", wt.LPWSTR),
                ("lpTitle", wt.LPWSTR), ("dwX", wt.DWORD), ("dwY", wt.DWORD),
                ("dwXSize", wt.DWORD), ("dwYSize", wt.DWORD), ("dwXCountChars", wt.DWORD),
                ("dwYCountChars", wt.DWORD), ("dwFillAttribute", wt.DWORD), ("dwFlags", wt.DWORD),
                ("wShowWindow", wt.WORD), ("cbReserved2", wt.WORD), ("lpReserved2", ctypes.c_void_p),
                ("hStdInput", wt.HANDLE), ("hStdOutput", wt.HANDLE), ("hStdError", wt.HANDLE),
            ]

        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("hProcess", wt.HANDLE), ("hThread", wt.HANDLE),
                ("dwProcessId", wt.DWORD), ("dwThreadId", wt.DWORD),
            ]

        si = STARTUPINFOW()
        si.cb = ctypes.sizeof(si)
        si.lpDesktop = "WinSta0\\Default"
        si.dwFlags = 1  # STARTF_USESHOWWINDOW
        si.wShowWindow = 1  # SW_SHOWNORMAL
        pi = PROCESS_INFORMATION()

        # When frozen, use sys.executable directly without passing script path
        if getattr(sys, "frozen", False):
            cmd_str = f'"{sys.executable}"'
        else:
            py_exe = sys.executable
            pyw_exe = os.path.join(os.path.dirname(py_exe), "pythonw.exe")
            exe_to_use = pyw_exe if os.path.exists(pyw_exe) else py_exe
            cmd_str = f'"{exe_to_use}" "{os.path.abspath(__file__)}"'
        cmd_buf = ctypes.create_unicode_buffer(cmd_str)

        flags = 0x01000000 | 0x00000200  # CREATE_BREAKAWAY_FROM_JOB | CREATE_NEW_PROCESS_GROUP
        ok = ctypes.windll.kernel32.CreateProcessW(
            None, cmd_buf, None, None, False, flags, None, BASE_DIR, ctypes.byref(si), ctypes.byref(pi)
        )
        if not ok:
            # Fallback if job object restricts breakaway
            flags = 0x00000200  # CREATE_NEW_PROCESS_GROUP
            ok = ctypes.windll.kernel32.CreateProcessW(
                None, cmd_buf, None, None, False, flags, None, BASE_DIR, ctypes.byref(si), ctypes.byref(pi)
            )
        if ok:
            print(f"Spawned GUI on WinSta0\\Default (PID={pi.dwProcessId}) from {desk}.", flush=True)
            ctypes.windll.kernel32.CloseHandle(pi.hThread)
            ctypes.windll.kernel32.CloseHandle(pi.hProcess)
            os._exit(0)


ensure_interactive_desktop()

import database

# Guard against broken pipes or None stdout/stderr from C++ DLLs (OpenCV / DirectShow)
_log_dir = os.path.join(database.get_app_dir(), "data")
try:
    os.makedirs(_log_dir, exist_ok=True)
    _log_path = os.path.join(_log_dir, "app.log")
    _log_file = open(_log_path, "a", encoding="utf-8", buffering=1)
    os.dup2(_log_file.fileno(), 1)
    os.dup2(_log_file.fileno(), 2)
    sys.stdout = _log_file
    sys.stderr = _log_file
except Exception:
    pass

import webview
import video_engine
import server

PORT = 5892
APP_URL = f"http://127.0.0.1:{PORT}"


def cleanup_stale_port(port: int = PORT) -> None:
    """Ensure no orphaned background server is holding the application port."""
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        out = subprocess.check_output(
            "netstat -ano", shell=True, stderr=subprocess.DEVNULL, creationflags=flags
        ).decode(errors="ignore")
        my_pid = str(os.getpid())
        killed = False
        for line in out.splitlines():
            if f"127.0.0.1:{port}" in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                if pid.isdigit() and pid != my_pid and pid != "0":
                    subprocess.call(
                        f"taskkill /PID {pid} /T /F", shell=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=flags
                    )
                    killed = True
        if killed:
            time.sleep(0.6)
    except Exception:
        pass


def start_background_server():
    server.start_server(port=PORT, start_video=True)


def wait_for_server(timeout=8.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(APP_URL, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.15)
    return False


def on_closed():
    """Clean up video engine and terminate process completely on window close."""
    print("Shutting down Provenance...", flush=True)
    try:
        video_engine.engine.stop()
    except Exception:
        pass
    os._exit(0)


def on_window_ready(win):
    """Bring the native window to front and maximize once ready."""
    hwnd = 0
    try:
        hwnd = ctypes.windll.user32.FindWindowW(None, "Provenance - Shipment CCTV Proof & Packing Station")
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        print(f"Native desktop window active (HWND={hwnd}).", flush=True)
    except Exception as e:
        print(f"Window activation warning: {e}", flush=True)

    # Ensure video engine is running if not already started by server
    if not video_engine.engine.running:
        source = database.get_setting("camera_source", "webcam:0")
        video_engine.engine.camera_source = source
        video_engine.engine.start()

    time.sleep(1.5)
    is_w = ctypes.windll.user32.IsWindow(hwnd) if hwnd else 0
    is_v = ctypes.windll.user32.IsWindowVisible(hwnd) if hwnd else 0
    print(f"[WIN-CHECK] Desktop={get_current_desktop_name()} HWND={hwnd} IsWindow={is_w} IsVisible={is_v}", flush=True)


import license_guard


def main():
    print(f"Initializing Provenance Desktop App (Desktop={get_current_desktop_name()})...", flush=True)
    
    # Verify hardware node licensing and anti-tamper signature
    is_valid, msg, meta = license_guard.verify_license_file()
    print(f"[LICENSE] Hardware Node Status: {'AUTHORIZED' if is_valid else 'LOCKED'} - {msg}", flush=True)
    if not is_valid:
        print(f"CRITICAL: License check failed ({msg}). Terminating.", flush=True)
        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Provenance Hardware Node Locked!\n\nReason: {msg}\n\nStation Hardware ID: {meta.get('machine_id', 'UNKNOWN')}\n\nPlease contact your system administrator to authorize this workstation.",
                "Provenance - Workstation Security",
                0x10 | 0x0
            )
        except Exception:
            pass
        sys.exit(1)

    cleanup_stale_port(PORT)

    # 1. Start background Bottle server in daemon thread
    server_thread = threading.Thread(target=start_background_server, daemon=True)
    server_thread.start()

    # 2. Wait until local server is serving
    if not wait_for_server():
        print("Error: Background server failed to start within timeout.", flush=True)
        os._exit(1)

    print(f"Server online at {APP_URL}. Launching native desktop window...", flush=True)

    # 3. Create native desktop window via Edge WebView2
    window = webview.create_window(
        title="Provenance - Shipment CCTV Proof & Packing Station",
        url=APP_URL,
        width=1220,
        height=820,
        min_size=(960, 620),
        background_color="#090a0d",
        text_select=True
    )
    window.events.closed += on_closed

    # 4. Start PyWebView GUI event loop and run on_window_ready once window is shown
    webview.start(on_window_ready, args=[window], debug=False)


if __name__ == "__main__":
    main()


