import ctypes
from ctypes import wintypes
import time
import os
import sys

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Attach to interactive desktop
hwinsta = user32.OpenWindowStationW("WinSta0", False, 0x037F)
if hwinsta:
    user32.SetProcessWindowStation(hwinsta)
hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
if hdesk:
    user32.SetThreadDesktop(hdesk)

from PIL import Image

def find_provenance_hwnd():
    found = []
    def enum_cb(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            if "Provenance" in title:
                found.append((hwnd, title))
        return True
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    return found

def capture_hwnd(hwnd, out_path):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    if w <= 0 or h <= 0:
        print("Invalid window size:", w, h)
        return False

    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)

    hwnd_dc = user32.GetWindowDC(hwnd)
    mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, w, h)
    old_bitmap = gdi32.SelectObject(mem_dc, bitmap)

    # 2 is PW_CLIENTONLY, 0 is full window
    ret = user32.PrintWindow(hwnd, mem_dc, 2)
    if not ret:
        ret = user32.PrintWindow(hwnd, mem_dc, 0)
    if not ret:
        gdi32.BitBlt(mem_dc, 0, 0, w, h, hwnd_dc, 0, 0, 0x00CC0020)

    # Extract bitmap bytes
    bmi = bytearray(40)
    import struct
    struct.pack_into("<IiiHHIIiiII", bmi, 0, 40, w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = bytearray(w * h * 4)
    gdi32.GetDIBits(mem_dc, bitmap, 0, h, (ctypes.c_char * len(buf)).from_buffer(buf), (ctypes.c_char * 40).from_buffer(bmi), 0)

    gdi32.SelectObject(mem_dc, old_bitmap)
    gdi32.DeleteObject(bitmap)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(hwnd, hwnd_dc)

    img = Image.frombuffer("RGBA", (w, h), bytes(buf), "raw", "BGRA", 0, 1)
    img.convert("RGB").save(out_path)
    print(f"Saved screenshot: {out_path} ({w}x{h})")
    return True

if __name__ == "__main__":
    wins = find_provenance_hwnd()
    print("Found windows:", wins)
    if not wins:
        print("No Provenance window found!")
        sys.exit(1)
    
    hwnd, title = wins[0]
    out_dir = r"C:\Users\sharv\.gemini\antigravity\brain\f5a0e924-79bb-495f-9aab-a17922b8c28c"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "provenance_current_state.png")
    capture_hwnd(hwnd, out_file)
