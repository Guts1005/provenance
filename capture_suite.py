import ctypes
from ctypes import wintypes
import time
import os
import sys
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

hwinsta = user32.OpenWindowStationW("WinSta0", False, 0x037F)
if hwinsta:
    user32.SetProcessWindowStation(hwinsta)
hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
if hdesk:
    user32.SetThreadDesktop(hdesk)

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
    if w <= 160 or h <= 28:
        print("Window is minimized or too small:", w, h)
        user32.ShowWindow(hwnd, 3)
        time.sleep(0.5)
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top

    user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)

    hwnd_dc = user32.GetWindowDC(hwnd)
    mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, w, h)
    old_bitmap = gdi32.SelectObject(mem_dc, bitmap)

    ret = user32.PrintWindow(hwnd, mem_dc, 2)
    if not ret:
        ret = user32.PrintWindow(hwnd, mem_dc, 0)
    if not ret:
        gdi32.BitBlt(mem_dc, 0, 0, w, h, hwnd_dc, 0, 0, 0x00CC0020)

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
    print(f"Captured: {out_path} ({w}x{h})")
    return True

def click_client(hwnd, x, y):
    pt = wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    target_x = pt.x + x
    target_y = pt.y + y
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.1)
    user32.SetCursorPos(target_x, target_y)
    time.sleep(0.05)
    user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.4)

def press_esc():
    user32.keybd_event(0x1B, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x1B, 0, 2, 0)
    time.sleep(0.4)

if __name__ == "__main__":
    wins = find_provenance_hwnd()
    if not wins:
        print("Provenance window not found")
        sys.exit(1)
    hwnd = wins[0][0]
    out_dir = r"C:\Users\sharv\.gemini\antigravity\brain\f5a0e924-79bb-495f-9aab-a17922b8c28c"

    # Ensure window is maximized and foreground
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    # 1. Ensure Station View (Press F1)
    user32.keybd_event(0x70, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x70, 0, 2, 0)
    time.sleep(0.6)
    capture_hwnd(hwnd, os.path.join(out_dir, "provenance_station_sans_clean.png"))

    # 2. Switch to Clips Archive tab (Press F2)
    user32.keybd_event(0x71, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x71, 0, 2, 0)
    time.sleep(0.8)
    capture_hwnd(hwnd, os.path.join(out_dir, "provenance_archive_order_carrier.png"))

    # 3. In Clips Archive, click the Edit button on row 1 (x ~ 1760, y ~ 200)
    click_client(hwnd, 1760, 200)
    time.sleep(0.6)
    capture_hwnd(hwnd, os.path.join(out_dir, "provenance_edit_metadata_modal.png"))

    # 4. Close Edit modal (press ESC)
    press_esc()
    time.sleep(0.5)

    # 5. Click View Proof on row 1 (x ~ 1680, y ~ 200)
    click_client(hwnd, 1680, 200)
    time.sleep(0.8)
    capture_hwnd(hwnd, os.path.join(out_dir, "provenance_proof_modal_metadata.png"))

    # 6. Close Proof modal and return to Station (Press ESC then F1)
    press_esc()
    time.sleep(0.3)
    user32.keybd_event(0x70, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x70, 0, 2, 0)
    time.sleep(0.3)
    print("All captures completed successfully.")
