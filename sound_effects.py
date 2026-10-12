"""
Provenance Enterprise Acoustic Feedback Engine.
Provides non-blocking audio chimes (success ding, error buzz, recording alert)
for eyes-free warehouse packing floor operations via native Windows multimedia.
Zero third-party audio dependencies, zero em-dashes.
"""

import sys
import time
import threading

# Sound configuration state
_SOUND_ENABLED = True
_LOCK = threading.Lock()


def is_sound_enabled() -> bool:
    global _SOUND_ENABLED
    with _LOCK:
        return _SOUND_ENABLED


def set_sound_enabled(enabled: bool) -> None:
    global _SOUND_ENABLED
    with _LOCK:
        _SOUND_ENABLED = bool(enabled)


def _safe_beep(frequency: int, duration_ms: int) -> None:
    if not is_sound_enabled():
        return
    if sys.platform != "win32":
        return
    try:
        import winsound
        winsound.Beep(frequency, duration_ms)
    except Exception:
        pass


def _play_pattern_async(pattern: list) -> None:
    """Run a sequence of (frequency, duration_ms, delay_ms) in a background thread."""
    def worker():
        for item in pattern:
            if not is_sound_enabled():
                break
            freq, dur, delay = item
            _safe_beep(freq, dur)
            if delay > 0:
                time.sleep(delay / 1000.0)

    t = threading.Thread(target=worker, daemon=True)
    t.start()


def play_success_ding() -> None:
    """Bright double chime for valid barcode scan."""
    # Pattern: (freq_hz, duration_ms, pause_ms_after)
    pattern = [
        (1200, 70, 25),
        (1750, 110, 0)
    ]
    _play_pattern_async(pattern)


def play_error_buzz() -> None:
    """Firm low buzz for unknown barcode, duplicate scan, or error."""
    pattern = [
        (320, 260, 0)
    ]
    _play_pattern_async(pattern)


def play_record_start() -> None:
    """Acknowledge clip recording initiation."""
    pattern = [
        (850, 80, 0)
    ]
    _play_pattern_async(pattern)


def play_record_finish() -> None:
    """Subtle confirmation when video write finishes."""
    pattern = [
        (1100, 60, 20),
        (1400, 80, 0)
    ]
    _play_pattern_async(pattern)


if __name__ == "__main__":
    print("Testing sound effects...")
    print("1. Success ding")
    play_success_ding()
    time.sleep(0.5)
    print("2. Error buzz")
    play_error_buzz()
    time.sleep(0.5)
    print("3. Record start")
    play_record_start()
    time.sleep(0.5)
    print("4. Record finish")
    play_record_finish()
    time.sleep(0.5)
    print("Sound test complete.")
