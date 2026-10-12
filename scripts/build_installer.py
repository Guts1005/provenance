"""
Provenance - Production Build & Installer Generation Pipeline.
Compiles the application into a standalone Windows binary (Provenance.exe)
with virtualized UI assets, embedded codecs, and hardware-locking guards.
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_binary():
    print("==================================================")
    print("   PROVENANCE INDUSTRIAL PACKING SUITE BUILDER    ")
    print("==================================================")

    # 1. Clean previous build caches
    dist_dir = os.path.join(BASE_DIR, "dist")
    build_dir = os.path.join(BASE_DIR, "build")
    for d in [dist_dir, build_dir]:
        if os.path.exists(d):
            print(f"Cleaning {d}...")
            shutil.rmtree(d, ignore_errors=True)

    # 2. Check PyInstaller availability
    try:
        import PyInstaller
        print(f"Detected PyInstaller v{PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 3. Assemble PyInstaller build arguments
    ui_sep = ";" if os.name == "nt" else ":"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=Provenance",
        "--onedir",
        "--windowed",
        "--noconsole",
        "--clean",
        "--noconfirm",
        f"--add-data=ui{ui_sep}ui",
        "--hidden-import=engineio.async_drivers.threading",
        "--hidden-import=cv2",
        "--hidden-import=bottle",
        "--hidden-import=sqlite3",
        "--hidden-import=numpy",
        "main.py"
    ]

    dll_path = os.path.join(BASE_DIR, "openh264-2.5.0-win64.dll")
    if os.path.exists(dll_path):
        cmd.insert(-1, f"--add-data=openh264-2.5.0-win64.dll{ui_sep}.")

    bin_dir = os.path.join(BASE_DIR, "bin")
    if os.path.exists(bin_dir):
        cmd.insert(-1, f"--add-data=bin{ui_sep}bin")

    print("\nExecuting PyInstaller compilation:")
    print(" ".join(cmd))
    print("--------------------------------------------------")

    res = subprocess.run(cmd, cwd=BASE_DIR)
    if res.returncode != 0:
        print("\nERROR: Compilation failed with return code:", res.returncode)
        sys.exit(res.returncode)

    target_app_dir = os.path.join(dist_dir, "Provenance")
    print(f"\nExecutable compiled successfully at: {target_app_dir}")

    # Copy license file if present
    lic_src = os.path.join(BASE_DIR, "provenance.lic")
    if os.path.exists(lic_src):
        shutil.copy2(lic_src, os.path.join(target_app_dir, "provenance.lic"))

    # Create empty clips and data directories in dist
    os.makedirs(os.path.join(target_app_dir, "clips"), exist_ok=True)
    os.makedirs(os.path.join(target_app_dir, "data"), exist_ok=True)

    # 3b. Compile Standalone Uninstaller if present
    uninst_script = os.path.join(BASE_DIR, "installer", "uninstaller_gui.py")
    if os.path.exists(uninst_script):
        print("\n--------------------------------------------------")
        print("Compiling Standalone Uninstaller (Uninstall.exe)...")
        print("--------------------------------------------------")
        uninst_cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--name=Uninstall",
            "--onefile",
            "--windowed",
            "--noconsole",
            "--clean",
            "--noconfirm",
            "--uac-admin",
            uninst_script
        ]
        res_uninst = subprocess.run(uninst_cmd, cwd=BASE_DIR)
        uninst_exe = os.path.join(dist_dir, "Uninstall.exe")
        if res_uninst.returncode == 0 and os.path.exists(uninst_exe):
            shutil.copy2(uninst_exe, os.path.join(target_app_dir, "Uninstall.exe"))
            print(f"Bundled Uninstall.exe into: {target_app_dir}")

    # 4. Compile Standalone GUI Setup Wizard (Setup_Provenance.exe)
    print("\n--------------------------------------------------")
    print("Compiling Standalone Setup Wizard (Setup_Provenance.exe)...")
    print("--------------------------------------------------")
    wizard_script = os.path.join(BASE_DIR, "installer", "setup_wizard_gui.py")
    wizard_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=Setup_Provenance",
        "--onefile",
        "--windowed",
        "--noconsole",
        "--noconfirm",
        "--uac-admin",
        f"--add-data={target_app_dir}{ui_sep}payload",
        wizard_script
    ]
    res_wiz = subprocess.run(wizard_cmd, cwd=BASE_DIR)
    setup_exe = os.path.join(dist_dir, "Setup_Provenance.exe")
    if res_wiz.returncode == 0 and os.path.exists(setup_exe):
        print(f"\nStandalone Setup Wizard created successfully: {setup_exe}")

    print("\n==================================================")
    print("BUILD COMPLETE: Provenance standalone package & Setup Wizard ready.")
    print(f"App Directory   : {target_app_dir}")
    if os.path.exists(setup_exe):
        print(f"Installer Wizard: {setup_exe}")
    print("==================================================\n")


if __name__ == "__main__":
    build_binary()
