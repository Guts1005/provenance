"""
Automated PyInstaller Build Script for Barcode Test.
Compiles the application into a standalone Windows executable (BarcodeTest.exe).
"""

import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build():
    print("=== Building Standalone BarcodeTest.exe ===")
    
    # 1. Check / Install PyInstaller if missing
    try:
        import PyInstaller
        print(f"PyInstaller version {PyInstaller.__version__} detected.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Prepare PyInstaller command
    ui_sep = ";" if os.name == "nt" else ":"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=BarcodeTest",
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--add-data=ui{ui_sep}ui",
        f"--add-data=data{ui_sep}data",
        "main.py"
    ]

    dll_path = os.path.join(BASE_DIR, "openh264-2.5.0-win64.dll")
    if os.path.exists(dll_path):
        cmd.insert(-1, f"--add-data=openh264-2.5.0-win64.dll{ui_sep}.")

    print("Running PyInstaller command:")
    print(" ".join(cmd))

    res = subprocess.run(cmd, cwd=BASE_DIR)
    if res.returncode == 0:
        exe_path = os.path.join(BASE_DIR, "dist", "BarcodeTest", "BarcodeTest.exe")
        print("\n=============================================")
        print("BUILD SUCCESSFUL!")
        print(f"Executable output: {exe_path}")
        print("=============================================\n")
    else:
        print("Build failed with exit code:", res.returncode)


if __name__ == "__main__":
    build()
