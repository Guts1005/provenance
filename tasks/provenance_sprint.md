# Provenance — Production-Grade Industrial UI Architecture & Sprints

## Sprint 1: Brand Migration to "Provenance" & High-Contrast Industrial Token System
- [x] Task 1.1: Rename application title, branding, and headers across `main.py`, `ui/index.html`, and `ui/app.js` to **Provenance**
- [x] Task 1.2: Eliminate all AI-slop animations (spring modals, sliding tab pills, backdrop blur, pulsing timers)
- [x] Task 1.3: Enforce the 3 purposeful motions: instant scan flash (<60ms), steady red recording lamp, and sub-120ms state fades
- [x] Task 1.4: Refactor color palette to strict "one-meaning-per-color" (Solid Red for Recording & Error, Green for Success & Verified, Neutrals for surfaces; eliminate Cyan and Amber recording)
- [x] Task 1.5: Fix contrast ratios for cheap 1080p warehouse panels (Surface `#151921` / `#1c222d`, Borders `#2d3646`, Text `#f8fafc` / `#cbd5e1` / `#94a3b8` > 5.5:1 contrast)
- [x] Task 1.6: Self-host and standardize on local system monospace stack (`Consolas`, `monospace`) with `tabular-nums`

## Sprint 2: Full-Width Status Band & Signature Packing Timeline Strip
- [x] Task 2.1: Build the full-width high-visibility status band (`READY TO SCAN`, `● RECORDING [BARCODE]`, `✓ SAVED`) legible from 3–5 meters
- [x] Task 2.2: Implement the **Signature Product Element**: Continuous Packing Timeline Strip displaying chronological shift scans, 5s pre-roll bounds, and live expanding recording block
- [x] Task 2.3: Redesign the bench input with large high-contrast tabular monospace barcode display and direct Enter-to-Finish ergonomics

## Sprint 3: Dispute Archive, Forensic Player & Error State Architecture
- [x] Task 3.1: Clean up Dispute Archive table: replace SHA-256 badge clutter with clean `✓ VERIFIED` status and a dedicated 1-click copy / details drawer
- [x] Task 3.2: Rebuild clip reviewer modal with timeline bounds, frame-stepping, and zero-latency playback controls
- [x] Task 3.3: Implement concrete error states:
  - Camera Offline banner across viewport with reconnect trigger
  - Duplicate scan warning (if scanned within 60 seconds)
  - Storage space gauge / disk full protection via `shutil.disk_usage`

## Sprint 4: Rigorous Testing & Live Runtime Verification
- [x] Task 4.1: Run full unit & REST API test suite (`python -m unittest discover -s tests -v`) — **21 of 21 tests passed (0 failures, 0 errors)**
- [x] Task 4.2: Restart desktop application on `WinSta0\Default` under Provenance (HWND active and visible)
- [x] Task 4.3: Perform live barcode scan and CCTV recording cycle to verify the full-width status band, timeline strip, and instant feedback

---
### Runtime Verification Verdict:
1. **Status Band**: High-contrast, full-width status band toggles instantly across `READY TO SCAN` (idle), `✓ SCAN ACCEPTED` (60ms green flash), `● RECORDING [BARCODE]` (solid red), and `✓ SAVED` (green confirmation).
2. **Signature Shift Packing Timeline**: Pinned directly below the CCTV viewport; renders chronological completed parcel blocks and live red expanding block while recording.
3. **Ergonomics & Performance**: No cmd prompt popups, silent FFmpeg transcoding, instant Web Audio chimes, zero animation delays, and complete offline capability.
