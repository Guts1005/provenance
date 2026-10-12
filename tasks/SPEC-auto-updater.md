# Spec: Provenance Enterprise Software Auto-Updater

## 1. Objective
Enable Provenance packing stations globally to automatically discover, download, verify, and apply software updates whenever connected to the internet, without disrupting existing packing operations, compromising air-gapped station security, or freezing running desktop processes.

### Core User Stories & Acceptance Criteria
- **User Story 1 (Manual Check)**: In the Settings view, an operator or supervisor can click "Check for Updates" to query the remote manifest. Within 2 seconds, the UI reports whether the station is up to date or a newer version exists, displaying release notes and download size.
- **User Story 2 (Air-Gapped / Offline Safety)**: When the station is completely offline or the network is unreachable, update checks fail immediately and silently without freezing the camera stream, throwing exceptions, or degrading UI performance.
- **User Story 3 (1-Click Download with Progress)**: The user can click "Download Update" to fetch the installer in the background. A live progress bar shows download percentage and size transferred. The video engine and live camera remain at 30 FPS with zero dropped frames.
- **User Story 4 (Integrity & Anti-Tamper)**: The downloaded installer is strictly validated against the remote SHA-256 cryptographic hash before it can be executed. Corrupt or partial downloads are rejected.
- **User Story 5 (Clean Windows Installation & Restart)**: When the user confirms "Install & Restart", the system checks that no active recording session is underway, spawns the Inno Setup installer detached, and cleanly closes Provenance so Windows file locks are released.
- **User Story 6 (Visual Theme & Ergonomics)**: The auto-updater UI conforms 100% to the Dispatch v2 industrial design system (obsidian dark mode, tactile buttons, Atkinson Hyperlegible typography, accessible contrast).

---

## 2. Tech Stack
- **Backend**: Python 3.11, Bottle HTTP framework, urllib with strict socket timeouts, hashlib for SHA-256 verification, subprocess with Windows creation flags.
- **Frontend**: Vanilla JavaScript (app.js), HTML5, CSS3 with Dispatch v2 design tokens (`--canvas`, `--surface`, `--pallet`, `--line`, `--ink`).
- **Packaging/Installer**: Inno Setup (`installer/setup_script.iss`), PyInstaller (`Provenance.spec`).

---

## 3. Commands
- **Run Tests**: `python -m pytest tests/test_updater.py tests/test_system.py`
- **Lint / Syntax Check**: `python -m py_compile updater.py server.py`
- **Run Development App**: `python main.py`
- **Build Installer**: `python build_exe.py`

---

## 4. Project Structure
```
barcode-test/
├── updater.py               # New: Core Auto-Updater logic (check, download, verify, apply)
├── server.py                # Updated: REST API endpoints for updater lifecycle
├── main.py                  # Updated: Version constant and safe updater hooks
├── database.py              # Updated: Settings persistence for auto-update preferences
├── ui/
│   ├── index.html           # Updated: Software & Updates card in Settings view
│   ├── app.js               # Updated: Client-side polling, progress rendering, actions
│   └── style.css            # Updated: Update progress bar and release notes badge styles
└── tests/
    └── test_updater.py      # New: Comprehensive unit and integration test suite
```

---

## 5. Code Style & Conventions
- Pure standard library networking (`urllib.request`) with explicit 2.5s connect timeouts.
- Thread-safe background downloading via Python `threading.Thread`.
- Atomic writes: Stream into `.part` file, verify SHA-256, then rename.
- Detached Windows process spawning using `subprocess.Popen` with `DETACHED_PROCESS` (0x00000008) or `CREATE_NEW_PROCESS_GROUP` (0x00000200).
- Strictly zero em-dashes across all code comments, docstrings, UI labels, and error messages.

---

## 6. Testing Strategy
- **Unit Tests (`tests/test_updater.py`)**:
  - Semantic version comparison (1.0.0 vs 1.0.1, 1.1.0 vs 1.0.9).
  - Manifest parsing and field validation.
  - Offline network failure handling and socket timeout non-blocking behavior.
  - Partial download handling and SHA-256 checksum verification (valid vs tampered).
  - Active session guard (blocks installer launch if `is_recording` is True).
- **Integration Tests**:
  - REST endpoints `/api/updates/status`, `/api/updates/check`, `/api/updates/download`, `/api/updates/apply`.
  - Mock HTTP server providing a test manifest and dummy installer.
- **Visual Verification**:
  - Browser/WebView inspection of the Settings view, testing update states: Idle, Checking, Available, Downloading, Ready.

---

## 7. Boundaries
- **Always do**:
  - Enforce timeout <= 3.0s on all network requests so offline stations never hang.
  - Verify SHA-256 before allowing any installer execution.
  - Check whether a shipment recording session is active before allowing an update restart.
  - Match Dispatch v2 CSS variables and theme tokens.
- **Ask first**:
  - Changing the default production update manifest repository URL.
- **Never do**:
  - Never execute unverified downloaded executables.
  - Never block the Bottle server request loop or the OpenCV video engine thread.
  - Never show blocking modal popups while an operator is on the Station view.
  - Never use em-dashes in UI text or logs.

---

## 8. Success Criteria
1. `tests/test_updater.py` passes 100% of unit and integration tests.
2. `tests/test_system.py` continues to pass 100% (zero regressions).
3. Update check against mock and live manifests correctly detects new versions vs up-to-date state.
4. Offline mode gracefully returns clean offline status within 2 seconds without errors or exceptions.
5. In Settings, the "Software & Automatic Updates" panel renders cleanly with live status, check button, and progress indicators.
6. A test update download successfully completes, verifies SHA-256, and indicates readiness to install.
