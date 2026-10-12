# Implementation Plan: Barcode Test Demo Overhaul (Scrum Sprints 1–3)

## Overview
Eliminate camera connection failures, UI/API sluggishness, and demo workflow gaps in the **Barcode Test — Shipment CCTV Proof** desktop application through three vertical Scrum Sprints grounded in empirical profiling of the live runtime (`data/app.log`, `video_engine.py`, `server.py`, and `ui/app.js`).

---

## Root Causes Identified (Forensic Triage)

### 1. Why the Camera Failed to Connect (`192.168.0.250:554`)
- **Password `@` Symbol Unescaped in Raw RTSP URL**: The password `Ermawk@321` contains `@`, producing `rtsp://admin:Ermawk@321@192.168.0.250:554/Streaming/Channels/101` (two `@` delimiters), which breaks URL parsing and causes `CAP_IMAGES` / `FFmpeg` errors.
- **Prama `PT-NC320P1-N(D2)` Enforces `SHA-256` RTSP Digest Auth**: Direct socket probing of `192.168.0.250:554` revealed `WWW-Authenticate: Digest realm="IP Camera(LA085)", nonce="...", algorithm="SHA-256"`. OpenCV's bundled FFmpeg only supports MD5 Digest Auth, failing with `401 Unauthorized`.
- **1-Second Retry Storm Locks Out Camera IP**: When `_open_camera()` fails in `video_engine.py:189-192`, `_capture_loop()` retries `cv2.VideoCapture(source)` every `1.0s` indefinitely (78 consecutive `401` attempts logged in `data/app.log`), triggering the camera's brute-force IP lockout and leaving the viewport black.

### 2. Why the App Feels Sluggish
- **HTTP/1.1 Connection Pool Exhaustion by Zombie MJPEG Streams (`server.py:57-75`)**: When `get_latest_jpeg()` returns `None` (while camera is connecting or failed), `/api/camera/stream` loops `while True: time.sleep(0.045)` without yielding any bytes. Disconnected `<img src="/api/camera/stream">` requests never raise `BrokenPipeError` and pile up, starving Edge WebView2's 6-connection HTTP/1.1 pool and stalling `/api/camera/status`, `/api/sessions`, and `/api/settings`.
- **`self.lock` Contention & Blocking Camera I/O (`video_engine.py:146, 291`)**:
  - `set_camera_source()` calls `self.cap.release()` inside `self.lock` while `_capture_loop` is blocked inside OpenCV's C++ `cap.read()` / `cap.open()`, freezing the HTTP thread for 5–15 seconds.
  - `start_session()` synchronously stamps and writes 100 pre-roll frames while holding `self.lock`, stuttering the live video stream for 300–600ms right when a barcode is scanned.
- **Redundant SQLite Queries on 500ms Status Poll (`server.py:81`)**: `/api/camera/status` opens a new SQLite connection (`database.get_active_session()`) every 500ms even though `video_engine` already holds the active session state in memory.

### 3. Why the Demo Feels Incomplete
- **Raw RTSP String vs. Guided Camera Setup**: Users must manually construct `rtsp://user:pass@ip:port/path` in Settings with no **"Test Connection"** diagnostic button, no auto-encoding of special characters (`@`), and no quick switcher on the main Station header.
- **No Live "Recent Scans" Feed on the Station Screen**: When a user finishes a recording on the Packing Station tab, the clip disappears into the Archive tab—forcing demo viewers to switch tabs after every scan just to see or play the recorded proof.

---

## Architecture Decisions
1. **Built-in Local RTSP SHA-256 Auth Proxy + Exponential Backoff (`video_engine.py`)**:
   - Implement a lightweight loopback RTSP proxy (`127.0.0.1:0`) that transparently signs `OPTIONS`, `DESCRIBE`, `SETUP`, `PLAY`, `GET_PARAMETER`, and `TEARDOWN` with RFC 7616 `SHA-256` (or `MD5`) Digest Auth and auto-encodes special password characters (`@`), plus circuit-breaker backoff on `401 Unauthorized` so we never lock out the camera IP.
2. **Lock-Free Frame Handoff & Diagnostic Placeholder Frames (`video_engine.py`, `server.py`)**:
   - Never hold `self.lock` during `cv2.VideoCapture` open/read/release or pre-roll disk writes.
   - Always yield a rendered diagnostic JPEG frame (`CONNECTING TO CAMERA...` / `RTSP 401 AUTH FAILED — CHECK PASSWORD`) when no camera frame is available so `/api/camera/stream` never blocks or leaks HTTP connections.
3. **Structured Camera Onboarding + Station Live Recent Clips Strip (`ui/index.html`, `ui/app.js`)**:
   - Replace raw RTSP URL guesswork with structured fields (IP, Port, Username, Password, Channel `101 Main` / `102 Sub`), a **Test Camera Connection** diagnostic button, a quick camera toggle (`Webcam 0` / `Prama IP Cam` / `Demo Simulator`) in the Station HUD, and a live **Recent Clips** mini-drawer right on the Station tab for one-click instant playback during demos.

---

## Scrum Roadmap & Checkpoints

### Scrum Sprint 1: Camera Connectivity, SHA-256 RTSP Auth & Zero-Lockout Recovery
- [ ] **Task 1**: Build RFC 7616 SHA-256 / MD5 RTSP Auth Proxy & URL credential sanitizer in `video_engine.py`, with immediate `401` circuit-breaker (stops retry storms from locking the Prama camera).
- [ ] **Task 2**: Add `/api/camera/test` diagnostic endpoint in `server.py` and structured IP Camera form (IP, Port, User, Password, Stream `101`/`102` + "Test Connection" button) in `ui/index.html` & `ui/app.js`.
- [ ] **Checkpoint 1**: Verify `webcam:0`, simulated stream, and Prama `192.168.0.250:554` diagnostic test respond in `< 2.0s` with zero `401` retry storms.

### Scrum Sprint 2: Performance & Responsiveness (Eliminating Sluggishness)
- [ ] **Task 3**: Eliminate `self.lock` blocking in `video_engine.py` (move camera open/release and pre-roll frame stamping off the lock; render instant diagnostic status frames when disconnected).
- [ ] **Task 4**: Fix zombie MJPEG generator connections in `server.py` and eliminate the 500ms SQLite query in `/api/camera/status` (serve in-memory state in `< 2ms`).
- [ ] **Checkpoint 2**: Benchmark `/api/camera/status`, `/api/camera/source`, and `/api/session/start` latency before/after (`p95 < 15ms`), and verify zero stalled HTTP connections in WebView2.

### Scrum Sprint 3: Complete Demo Experience & Station Workflow Polish
- [ ] **Task 5**: Add a **Recent Clips / Instant Proof** panel directly on the Packing Station tab (`ui/index.html`, `ui/app.js`, `ui/style.css`) so newly recorded clips appear immediately with a one-click `▶ Play Proof` button without leaving the station.
- [ ] **Task 6**: Add a quick **Camera Source Switcher** (`Webcam 0` | `Prama CCTV` | `Demo Simulator`) directly in the Station top bar so live demos work seamlessly even if hardware is unplugged.
- [ ] **Checkpoint 3**: Run full automated test suite (`tests/test_system.py`, `tests/test_api.py`) and end-to-end verification in the native desktop app.

---

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Prama camera IP (`192.168.0.250`) currently in temporary brute-force lockout from earlier retries | High | Stop automatic `401` retries immediately (1 attempt per credential change) and surface exact `401 Unauthorized / Camera Locked` status in UI; power-cycling camera clears RAM lockout immediately. |
| Switching camera sources while a recording is active | Med | Auto-finalize or guard active session before switching capture backend. |
| MJPEG stream connection buildup on tab switches | High | Always yield frames (live or diagnostic HUD frame) every 250ms when disconnected so closed sockets raise `BrokenPipeError` immediately and release threads. |
