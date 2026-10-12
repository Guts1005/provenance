# Implementation Plan: Provenance Auto-Updater

## Overview
Implement an air-gapped-safe, enterprise auto-updater for Provenance packing stations that allows 1-click updates when connected to internet, with zero disturbance to active packing sessions, zero freezes, and strict SHA-256 integrity validation.

---

## Task Breakdown

- [ ] **Task 1: Core Auto-Updater Engine (`updater.py`)**
  - Implement version comparison (`compare_versions(v1, v2)`).
  - Implement manifest fetching (`check_for_updates()`) with 2.5s connect timeout and offline resilience.
  - Implement chunked background downloading with `.part` staging and progress tracking (`download_update()`).
  - Implement cryptographic SHA-256 verification (`verify_download()`).
  - Implement safe Windows detached launcher (`apply_update()`) with active session lock check.
  - **Acceptance**: Module passes all edge cases without blocking or raising unhandled exceptions.
  - **Files**: `updater.py`

- [ ] **Task 2: Test-Driven Development Suite (`tests/test_updater.py`)**
  - Write unit tests for semantic version comparisons (e.g. 1.0.0 vs 1.1.0, 1.0.1 vs 1.0.0, invalid strings).
  - Write tests for offline simulation (unreachable host returns clean offline status within 2.5s).
  - Write tests for SHA-256 verification (valid file passes, corrupted/tampered file is rejected and purged).
  - Write tests for active recording guard (update apply blocked when recording).
  - **Acceptance**: `pytest tests/test_updater.py` passes 100%.
  - **Files**: `tests/test_updater.py`

- [ ] **Task 3: Server API Integration (`server.py`)**
  - Expose `/api/updates/status` (GET)
  - Expose `/api/updates/check` (POST)
  - Expose `/api/updates/download` (POST)
  - Expose `/api/updates/apply` (POST)
  - Expose `/api/updates/settings` (GET/POST for update check URL and auto-check preference).
  - **Acceptance**: Endpoints return standard JSON envelopes with correct HTTP headers.
  - **Files**: `server.py`

- [ ] **Task 4: UI Implementation & Dispatch v2 Design Alignment (`ui/`)**
  - Add "Software & Automatic Updates" card in Settings (`ui/index.html`).
  - Style update badge, version indicator, release notes card, and live progress bar (`ui/style.css`).
  - Wire up frontend polling, download progress animation, and update buttons (`ui/app.js`).
  - **Acceptance**: Matches dark Dispatch theme tokens, displays live progress, handles all states.
  - **Files**: `ui/index.html`, `ui/style.css`, `ui/app.js`

- [ ] **Task 5: End-to-End Verification & Visual Inspection**
  - Run existing `tests/test_system.py` to confirm zero regression on database/video pipeline.
  - Run `tests/test_updater.py` to confirm auto-updater passes.
  - Capture and verify screenshots of the updated Settings UI.
  - **Acceptance**: Clean visual and test verification report.
