"""
Provenance - Standalone GUI Uninstaller.
Provides clean removal of application binaries, shortcuts, Windows Firewall rules,
and Control Panel registration, with optional retention of warehouse video clips.
"""

import os
import sys
import time
import shutil
import sqlite3
import subprocess
import threading
import ctypes
import winreg
import tkinter as tk
from tkinter import ttk, messagebox


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    """Relaunches the current uninstaller executable with administrative privileges."""
    if is_admin():
        return True
    try:
        exe = sys.executable if getattr(sys, "frozen", False) else sys.executable
        args = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        if not getattr(sys, "frozen", False):
            args = f'"{os.path.abspath(__file__)}" {args}'
        res = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, args, None, 1)
        if res > 32:
            sys.exit(0)
    except Exception:
        pass
    return False


def get_install_dir() -> str:
    # 1. Attempt to query recorded installation location from registry
    try:
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Provenance"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Provenance"),
        ]
        for root, subkey in reg_paths:
            try:
                with winreg.OpenKey(root, subkey) as k:
                    val, _ = winreg.QueryValueEx(k, "InstallLocation")
                    if val and os.path.exists(val):
                        return os.path.normpath(val)
            except Exception:
                pass
    except Exception:
        pass

    # 2. Check if running directly from installed application directory
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(exe_dir, "Provenance.exe")):
        return exe_dir

    # 3. Check standard Program Files installation directory
    prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    default_prog = os.path.join(prog_files, "Provenance")
    if os.path.exists(default_prog):
        return default_prog

    return exe_dir


def get_configured_clips_dir() -> str:
    """Attempt to discover the configured clips directory from the database."""
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Provenance", "data", "barcode_test.db"),
        os.path.join(os.environ.get("PROGRAMDATA", ""), "Provenance", "data", "barcode_test.db"),
        os.path.join(get_install_dir(), "data", "barcode_test.db"),
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                with sqlite3.connect(c) as conn:
                    conn.row_factory = sqlite3.Row
                    row = conn.execute("SELECT value FROM settings WHERE key = 'clips_dir';").fetchone()
                    if row and row["value"]:
                        return row["value"].strip()
            except Exception:
                pass
    return r"C:\Provenance\Clips"


def get_all_desktop_paths() -> list:
    """Retrieve all valid desktop paths including redirected drives (e.g. E:\\Users\\...), OneDrive, and Public."""
    paths = []
    try:
        import winreg
        for subkey in (
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        ):
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey) as k:
                    val, _ = winreg.QueryValueEx(k, "Desktop")
                    if val:
                        norm = os.path.normpath(os.path.expandvars(val))
                        if os.path.exists(norm) and norm not in paths:
                            paths.append(norm)
            except Exception:
                pass
    except Exception:
        pass

    up_desk = os.path.normpath(os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"))
    if os.path.exists(up_desk) and up_desk not in paths:
        paths.append(up_desk)

    pub_desk = os.path.normpath(os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), "Desktop"))
    if os.path.exists(pub_desk) and pub_desk not in paths:
        paths.append(pub_desk)

    return paths


def unregister_from_control_panel():
    """Removes the Uninstall registration from Windows Registry."""
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Provenance"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Provenance"),
    ]
    for root, subkey in reg_paths:
        try:
            winreg.DeleteKey(root, subkey)
        except FileNotFoundError:
            pass
        except PermissionError:
            pass
        except Exception:
            pass


def execute_silent_uninstall(remove_clips=False, remove_data=True):
    """Executes silent uninstallation without UI."""
    target = get_install_dir()
    clips = get_configured_clips_dir()

    # 1. Kill running instances
    subprocess.run(["taskkill", "/F", "/IM", "Provenance.exe"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    time.sleep(0.3)

    # 2. Firewall rule
    try:
        subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", 'name=Provenance CCTV API'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    except Exception:
        pass

    # 3. Shortcuts
    start_menu = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs", "Provenance")
    if os.path.exists(start_menu):
        shutil.rmtree(start_menu, ignore_errors=True)

    for desk in get_all_desktop_paths():
        sc = os.path.join(desk, "Provenance.lnk")
        if os.path.exists(sc):
            try:
                os.remove(sc)
            except Exception:
                pass

    # 4. Registry
    unregister_from_control_panel()

    # 5. Data & Clips
    if remove_data:
        for appdata_p in [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Provenance"),
            os.path.join(os.environ.get("PROGRAMDATA", ""), "Provenance"),
        ]:
            if os.path.exists(appdata_p):
                shutil.rmtree(appdata_p, ignore_errors=True)

    if remove_clips and os.path.exists(clips):
        shutil.rmtree(clips, ignore_errors=True)

    # 6. Delete install folder via detached command
    cleanup_cmd = f'ping 127.0.0.1 -n 2 > nul & rmdir /s /q "{target}"'
    subprocess.Popen(cleanup_cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


class UninstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Provenance - Uninstall Workstation")
        self.geometry("620x460")
        self.resizable(False, False)
        self.configure(bg="#0f172a")

        self.install_dir = get_install_dir()
        self.clips_dir = get_configured_clips_dir()

        self.delete_clips_var = tk.BooleanVar(value=False)
        self.delete_data_var = tk.BooleanVar(value=True)

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Horizontal.TProgressbar", foreground="#ef4444", background="#ef4444", troughcolor="#1e293b", borderwidth=0)

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg="#1e293b", height=70)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="Uninstall Provenance Workstation", font=("Segoe UI", 13, "bold"), fg="#f8fafc", bg="#1e293b").pack(anchor="w", padx=24, pady=(14, 2))
        self.lbl_subtitle = tk.Label(hdr, text="Remove application files, shortcuts, and workstation registration", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b")
        self.lbl_subtitle.pack(anchor="w", padx=24)

        # Content
        self.container = tk.Frame(self, bg="#0f172a")
        self.container.pack(fill="both", expand=True, padx=24, pady=16)

        # Warning Card
        card = tk.Frame(self.container, bg="#1e293b", padx=16, pady=14)
        card.pack(fill="x", pady=(0, 16))

        tk.Label(
            card,
            text="Are you sure you want to completely remove Provenance?",
            font=("Segoe UI", 10, "bold"),
            fg="#f8fafc",
            bg="#1e293b"
        ).pack(anchor="w")

        tk.Label(
            card,
            text=f"Installation Location: {self.install_dir}",
            font=("Consolas", 8),
            fg="#94a3b8",
            bg="#1e293b"
        ).pack(anchor="w", pady=(4, 0))

        # Checkboxes
        opts_box = tk.Frame(self.container, bg="#0f172a")
        opts_box.pack(fill="x", pady=(0, 12))

        cb_data = tk.Checkbutton(
            opts_box,
            text="Delete local configuration, settings, and database",
            variable=self.delete_data_var,
            bg="#0f172a",
            fg="#f8fafc",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            activeforeground="#ffffff",
            font=("Segoe UI", 9)
        )
        cb_data.pack(anchor="w", pady=4)

        cb_clips = tk.Checkbutton(
            opts_box,
            text=f"Delete recorded CCTV packaging clips ({self.clips_dir})",
            variable=self.delete_clips_var,
            bg="#0f172a",
            fg="#fca5a5",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            activeforeground="#ef4444",
            font=("Segoe UI", 9, "bold")
        )
        cb_clips.pack(anchor="w", pady=4)

        tk.Label(
            opts_box,
            text="⚠ Note: Leave video clips unchecked to preserve warehouse shipping proof footage.",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg="#0f172a"
        ).pack(anchor="w", padx=24)

        # Progress elements (hidden initially)
        self.progress_frame = tk.Frame(self.container, bg="#0f172a")
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=570, mode="determinate")
        self.lbl_progress = tk.Label(self.progress_frame, text="Preparing to uninstall...", font=("Consolas", 9), fg="#94a3b8", bg="#0f172a")

        # Footer
        self.footer = tk.Frame(self, bg="#0b0f19", height=60)
        self.footer.pack(side="bottom", fill="x")
        self.footer.pack_propagate(False)

        self.btn_cancel = tk.Button(
            self.footer,
            text="Cancel",
            command=self.destroy,
            bg="#334155",
            fg="#f8fafc",
            activebackground="#475569",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=16,
            pady=6,
            cursor="hand2"
        )
        self.btn_cancel.pack(side="left", padx=24, pady=14)

        self.btn_uninstall = tk.Button(
            self.footer,
            text="Uninstall Provenance",
            command=self.start_uninstall,
            bg="#dc2626",
            fg="#ffffff",
            activebackground="#b91c1c",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=20,
            pady=6,
            cursor="hand2"
        )
        self.btn_uninstall.pack(side="right", padx=24, pady=14)

    def start_uninstall(self):
        self.btn_cancel.config(state="disabled")
        self.btn_uninstall.config(state="disabled")

        self.progress_frame.pack(fill="x", pady=(12, 0))
        self.progress_bar.pack(fill="x", pady=(4, 6))
        self.lbl_progress.pack(anchor="w")

        threading.Thread(target=self._worker, daemon=True).start()

    def update_progress(self, pct: int, text: str):
        self.after(0, lambda: (self.progress_bar.config(value=pct), self.lbl_progress.config(text=text)))

    def _worker(self):
        target = self.install_dir
        clips = self.clips_dir
        del_clips = self.delete_clips_var.get()
        del_data = self.delete_data_var.get()

        try:
            # 1. Terminate running instances
            self.update_progress(15, "Terminating active Provenance processes...")
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/IM", "Provenance.exe"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(0.4)

            # 2. Delete Firewall rule
            self.update_progress(30, "Removing Windows Firewall rule...")
            if os.name == "nt":
                try:
                    subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", 'name=Provenance CCTV API'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                except Exception:
                    pass

            # 3. Remove Shortcuts
            self.update_progress(50, "Removing Start Menu and Desktop shortcuts...")
            start_menu = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs", "Provenance")
            if os.path.exists(start_menu):
                shutil.rmtree(start_menu, ignore_errors=True)

            for desk in get_all_desktop_paths():
                sc = os.path.join(desk, "Provenance.lnk")
                if os.path.exists(sc):
                    try:
                        os.remove(sc)
                    except Exception:
                        pass

            # 4. Remove Control Panel Registration
            self.update_progress(65, "Removing Windows Control Panel registration...")
            unregister_from_control_panel()

            # 5. Database & Settings
            if del_data:
                self.update_progress(78, "Cleaning database and workstation cache...")
                for appdata_p in [
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Provenance"),
                    os.path.join(os.environ.get("PROGRAMDATA", ""), "Provenance"),
                ]:
                    if os.path.exists(appdata_p):
                        shutil.rmtree(appdata_p, ignore_errors=True)

            # 6. Video Clips (if opted in)
            if del_clips:
                self.update_progress(88, f"Removing video footage ({clips})...")
                if os.path.exists(clips):
                    shutil.rmtree(clips, ignore_errors=True)

            # 7. Remove files in install directory
            self.update_progress(95, "Removing application binaries and assets...")
            if os.path.exists(target):
                for root, dirs, files in os.walk(target, topdown=False):
                    for f in files:
                        p = os.path.join(root, f)
                        # Skip self executable while running
                        if getattr(sys, "frozen", False) and os.path.abspath(p).lower() == os.path.abspath(sys.executable).lower():
                            continue
                        try:
                            os.remove(p)
                        except Exception:
                            pass
                    for d in dirs:
                        try:
                            os.rmdir(os.path.join(root, d))
                        except Exception:
                            pass

            self.update_progress(100, "Uninstall complete!")
            self.after(500, self.finish_screen)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Uninstall Error", f"An error occurred: {e}", parent=self))

    def finish_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        self.lbl_subtitle.config(text="Uninstallation Complete")
        self.btn_cancel.pack_forget()
        self.btn_uninstall.config(text="Close", state="normal", bg="#16a34a", command=self.on_close_and_cleanup)

        tk.Label(
            self.container,
            text="✓ Provenance Successfully Removed",
            font=("Segoe UI", 14, "bold"),
            fg="#22c55e",
            bg="#0f172a"
        ).pack(anchor="w", pady=(24, 10))

        summary_msg = (
            "The application files, shortcuts, and system registrations have been uninstalled.\n\n"
        )
        if not self.delete_clips_var.get() and os.path.exists(self.clips_dir):
            summary_msg += f"• Your CCTV video archive has been preserved at:\n  {self.clips_dir}\n"

        tk.Label(
            self.container,
            text=summary_msg,
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0f172a",
            justify="left"
        ).pack(anchor="w")

    def on_close_and_cleanup(self):
        target = self.install_dir
        # Launch delayed self-cleanup
        cleanup_cmd = f'ping 127.0.0.1 -n 2 > nul & rmdir /s /q "{target}"'
        subprocess.Popen(cleanup_cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        self.destroy()


def main():
    if "/quiet" in sys.argv or "/S" in sys.argv or "--quiet" in sys.argv:
        execute_silent_uninstall(remove_clips=False, remove_data=True)
        sys.exit(0)

    # Require Admin to delete from Program Files
    if not is_admin():
        if run_as_admin():
            sys.exit(0)

    app = UninstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
