import ctypes
from ctypes import wintypes
import time
import os
import sys
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Attach to interactive desktop
hwinsta = user32.OpenWindowStationW("WinSta0", False, 0x037F)
if hwinsta:
    user32.SetProcessWindowStation(hwinsta)
hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
if hdesk:
    user32.SetThreadDesktop(hdesk)

VK_F1 = 0x70
VK_F2 = 0x71
VK_F3 = 0x72
VK_ESCAPE = 0x1B
KEYEVENTF_KEYUP = 0x0002

def send_key(vk):
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

def click_relative(hwnd, rel_x, rel_y):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    target_x = rect.left + rel_x
    target_y = rect.top + rel_y
    user32.SetCursorPos(target_x, target_y)
    time.sleep(0.05)
    user32.mouse_event(0x0002, 0, 0, 0, 0) # MOUSEEVENTF_LEFTDOWN
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0) # MOUSEEVENTF_LEFTUP
    time.sleep(0.3)

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
        return False

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
    print(f"Captured: {out_path}")
    return True

if __name__ == "__main__":
    wins = find_provenance_hwnd()
    if not wins:
        print("No Provenance window found!")
        sys.exit(1)
    
    hwnd, _ = wins[0]
    out_dir = r"C:\Users\sharv\.gemini\antigravity\brain\f5a0e924-79bb-495f-9aab-a17922b8c28c"

    # 1. Station view
    user32.SetForegroundWindow(hwnd)
    send_key(VK_F1)
    time.sleep(0.5)
    capture_hwnd(hwnd, os.path.join(out_dir, "provenance_station_sans_clean.png"))

    # 2. Clips Archive view
    send_key(VK_F2)
    time.sleep(0.6)
    capture_hwnd(hwnd, os.path.join(out_dir, "provenance_archive_order_carrier.png"))

    # 3. Click first "Edit" button in Archive Table (around rel_x=1690, rel_y=165)
    click_relative(hwnd, 1690, 165)
    time.sleep(0.5)
    capture_hwnd(hwnd, os.path.join(out_dir, "provenance_edit_metadata_modal.png"))

    # 4. Close Edit modal (press ESC) and click View Proof (rel_x=1620, rel_y=165)
    send_key(VK_ESCAPE)
    time.sleep(0.4)
    click_relative(hwnd, 1620, 165)
    time.sleep(0.8)
    capture_hwnd(hwnd, os.path.join(out_dir, "provenance_proof_modal_metadata.png"))

    # Return to Station
    send_key(VK_ESCAPE)
    time.sleep(0.3)
    send_key(VK_F1)
