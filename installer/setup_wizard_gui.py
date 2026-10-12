"""
Provenance - Standalone GUI Setup Wizard.
Multi-step interactive installation wizard with custom video storage location selection,
desktop shortcut creation, Windows Firewall rule authorization, and hardware node licensing.
"""

import os
import sys
import time
import shutil
import sqlite3
import subprocess
import threading
import ctypes
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

INSTALLER_VERSION = "2.0.9"

# Resolve base directories
if getattr(sys, "frozen", False):
    EXE_DIR = os.path.dirname(sys.executable)
    meipass = getattr(sys, "_MEIPASS", "")
    if meipass and os.path.exists(os.path.join(meipass, "payload")):
        PAYLOAD_DIR = os.path.join(meipass, "payload")
    elif os.path.exists(os.path.join(EXE_DIR, "Provenance")):
        PAYLOAD_DIR = os.path.join(EXE_DIR, "Provenance")
    else:
        PAYLOAD_DIR = EXE_DIR
else:
    EXE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PAYLOAD_DIR = os.path.join(EXE_DIR, "dist", "Provenance")


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_default_install_dir() -> str:
    if is_admin():
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        return os.path.join(program_files, "Provenance")
    else:
        local_app = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(local_app, "Programs", "Provenance")


def get_default_clips_dir() -> str:
    # Check if C:\Provenance\Clips is writable or default to User Videos
    candidate = r"C:\Provenance\Clips"
    try:
        os.makedirs(candidate, exist_ok=True)
        return candidate
    except Exception:
        user_videos = os.path.join(os.path.expanduser("~"), "Videos", "Provenance Clips")
        return user_videos


def get_drive_free_gb(path: str) -> float:
    try:
        drive = os.path.splitdrive(os.path.abspath(path))[0] or "C:"
        total, used, free = shutil.disk_usage(drive + "\\")
        return round(free / (1024 ** 3), 1)
    except Exception:
        return 0.0


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


def detect_existing_installation():
    """
    Detect if Provenance is already installed on this machine.
    Checks:
    1. Windows Registry (HKLM and HKCU Uninstall keys)
    2. Standard installation paths (Program Files, LocalAppData/Programs)
    Returns dict with install details if found, or None if fresh install.
    """
    candidates = []

    # 1. Registry search
    if os.name == "nt":
        try:
            import winreg
            for root_h, root_name in [
                (winreg.HKEY_LOCAL_MACHINE, "HKLM"),
                (winreg.HKEY_CURRENT_USER, "HKCU")
            ]:
                for view in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY, 0]:
                    try:
                        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Provenance"
                        with winreg.OpenKey(root_h, key_path, 0, winreg.KEY_READ | view) as k:
                            try:
                                loc, _ = winreg.QueryValueEx(k, "InstallLocation")
                            except Exception:
                                loc = ""
                            try:
                                ver, _ = winreg.QueryValueEx(k, "DisplayVersion")
                            except Exception:
                                ver = "2.0.0"
                            if loc and os.path.exists(os.path.join(loc, "Provenance.exe")):
                                candidates.append({
                                    "install_dir": os.path.normpath(loc),
                                    "version": ver or "2.0.0",
                                    "source": f"registry ({root_name})"
                                })
                    except Exception:
                        pass
        except Exception:
            pass

    # 2. Standard file system paths
    std_dirs = [
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Provenance"),
        os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Provenance"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Provenance"),
        get_default_install_dir()
    ]
    for d in std_dirs:
        if d and os.path.exists(os.path.join(d, "Provenance.exe")):
            norm_d = os.path.normpath(d)
            if not any(c["install_dir"].lower() == norm_d.lower() for c in candidates):
                candidates.append({
                    "install_dir": norm_d,
                    "version": "2.0.0",
                    "source": "filesystem"
                })

    if not candidates:
        return None

    existing = candidates[0]

    # Try to detect configured clips directory from existing installation database
    existing_clips = None
    appdata_local = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    db_candidates = [
        os.path.join(appdata_local, "Provenance", "data", "barcode_test.db"),
        os.path.join(existing["install_dir"], "data", "barcode_test.db")
    ]
    for db_path in db_candidates:
        if os.path.exists(db_path):
            try:
                with sqlite3.connect(db_path) as conn:
                    row = conn.execute("SELECT value FROM settings WHERE key = 'clips_dir'").fetchone()
                    if row and row[0]:
                        existing_clips = str(row[0]).strip()
                        break
            except Exception:
                pass

    existing["clips_dir"] = existing_clips or get_default_clips_dir()
    return existing


class SetupWizardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Provenance - Workstation Setup Wizard")
        self.geometry("700x540")
        self.resizable(False, False)
        self.configure(bg="#0f172a")

        # Check for existing installation
        self.existing_install = detect_existing_installation()
        self.setup_mode = tk.StringVar(value="repair" if self.existing_install else "install")

        initial_install_dir = self.existing_install["install_dir"] if self.existing_install else get_default_install_dir()
        initial_clips_dir = self.existing_install.get("clips_dir") if self.existing_install else get_default_clips_dir()

        # Configuration state
        self.install_dir = tk.StringVar(value=initial_install_dir)
        self.default_clips_dir = get_default_clips_dir()
        self.custom_clips_dir = tk.StringVar(value=initial_clips_dir or self.default_clips_dir)
        self.clips_mode = tk.StringVar(value="custom" if (initial_clips_dir and initial_clips_dir != self.default_clips_dir) else "default")
        self.create_desktop_icon = tk.BooleanVar(value=True)
        self.create_start_menu = tk.BooleanVar(value=True)
        self.configure_firewall = tk.BooleanVar(value=is_admin())
        self.launch_after = tk.BooleanVar(value=True)

        self.current_step = 1
        self.total_steps = 5

        # Style configuration
        self._configure_styles()

        # Build Main Frames
        self.header_frame = tk.Frame(self, bg="#1e293b", height=70)
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        self.header_title = tk.Label(
            self.header_frame,
            text="Provenance Industrial Setup Wizard",
            font=("Segoe UI", 13, "bold"),
            fg="#f8fafc",
            bg="#1e293b"
        )
        self.header_title.pack(anchor="w", padx=24, pady=(14, 2))

        self.header_subtitle = tk.Label(
            self.header_frame,
            text="Step 1 of 5: Welcome & System Overview",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#1e293b"
        )
        self.header_subtitle.pack(anchor="w", padx=24)

        # Content container
        self.container = tk.Frame(self, bg="#0f172a")
        self.container.pack(fill="both", expand=True, padx=24, pady=16)

        # Footer control frame
        self.footer_frame = tk.Frame(self, bg="#0b0f19", height=60)
        self.footer_frame.pack(side="bottom", fill="x")
        self.footer_frame.pack_propagate(False)

        self.btn_cancel = tk.Button(
            self.footer_frame,
            text="Cancel",
            command=self.on_cancel,
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

        self.btn_next = tk.Button(
            self.footer_frame,
            text="Next >",
            command=self.on_next,
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=20,
            pady=6,
            cursor="hand2"
        )
        self.btn_next.pack(side="right", padx=24, pady=14)

        self.btn_back = tk.Button(
            self.footer_frame,
            text="< Back",
            command=self.on_back,
            bg="#334155",
            fg="#f8fafc",
            activebackground="#475569",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9),
            padx=16,
            pady=6,
            cursor="hand2"
        )
        self.btn_back.pack(side="right", padx=(0, 6), pady=14)

        # Render first step
        self.render_step()

        # Check for automated update request
        auto_flags = ("--auto-update", "/VERYSILENT", "--silent")
        if any(f in sys.argv for f in auto_flags) and self.existing_install:
            self.after(250, self.start_auto_update)

    def start_auto_update(self):
        """Immediately trigger repair and update without wizard prompts."""
        self.setup_mode.set("repair")
        self.current_step = 5
        self.render_step()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Horizontal.TProgressbar", foreground="#2563eb", background="#2563eb", troughcolor="#1e293b", borderwidth=0)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def render_step(self):
        self.clear_container()

        if self.current_step == 1:
            if self.existing_install:
                self.render_step_1_maintenance()
            else:
                self.render_step_1_welcome()
        elif self.current_step == 2:
            self.render_step_2_install_dir()
        elif self.current_step == 3:
            self.render_step_3_clips_dir()
        elif self.current_step == 4:
            self.render_step_4_options()
        elif self.current_step == 5:
            self.render_step_5_installing()
        elif self.current_step == 6:
            self.render_step_6_finished()

    # --- STEP 1 (EXISTING INSTALLATION): REPAIR / UPDATE OR MODIFY ---
    def render_step_1_maintenance(self):
        self.header_subtitle.config(text="Workstation Maintenance: Update / Repair or Reconfigure")
        self.btn_back.config(state="disabled")

        lbl_lead = tk.Label(
            self.container,
            text="Existing Provenance Installation Detected",
            font=("Segoe UI", 12, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        )
        lbl_lead.pack(anchor="w", pady=(6, 4))

        # Detected info card
        info_card = tk.Frame(self.container, bg="#1e293b", padx=14, pady=10)
        info_card.pack(fill="x", pady=(0, 12))

        inst_dir = self.existing_install.get("install_dir", "Unknown")
        ver = self.existing_install.get("version", "2.0.0")
        clips = self.existing_install.get("clips_dir") or self.default_clips_dir

        lbl_badge = tk.Label(
            info_card,
            text=f"• Provenance v{ver} is currently installed on this workstation",
            font=("Segoe UI", 9, "bold"),
            fg="#22c55e",
            bg="#1e293b"
        )
        lbl_badge.pack(anchor="w", pady=(0, 4))

        lbl_loc = tk.Label(
            info_card,
            text=f"  Install Location: {inst_dir}\n  Video Storage:   {clips}",
            font=("Consolas", 8),
            fg="#cbd5e1",
            bg="#1e293b",
            justify="left"
        )
        lbl_loc.pack(anchor="w", pady=(0, 4))

        lbl_notice = tk.Label(
            info_card,
            text="Existing video clips, barcode records, and database settings will be safely preserved.",
            font=("Segoe UI", 8, "italic"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        lbl_notice.pack(anchor="w")

        # Prompt
        tk.Label(
            self.container,
            text="Select an action to perform:",
            font=("Segoe UI", 10, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        ).pack(anchor="w", pady=(0, 8))

        # Option 1: Repair / Update
        opt1_frame = tk.Frame(self.container, bg="#0f172a")
        opt1_frame.pack(fill="x", pady=(0, 8))

        rad_repair = tk.Radiobutton(
            opt1_frame,
            text="Update / Repair Installation (Recommended)",
            variable=self.setup_mode,
            value="repair",
            command=self.on_setup_mode_changed,
            bg="#0f172a",
            fg="#f8fafc",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            font=("Segoe UI", 10, "bold")
        )
        rad_repair.pack(anchor="w")

        lbl_repair_desc = tk.Label(
            opt1_frame,
            text="Reinstalls and updates application binaries, offline engines, and UI files to the latest version.\n"
                 "Preserves all existing packing database records, barcode history, and video evidence.",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg="#0f172a",
            justify="left"
        )
        lbl_repair_desc.pack(anchor="w", padx=24, pady=(2, 0))

        # Option 2: Modify / Custom Reinstall
        opt2_frame = tk.Frame(self.container, bg="#0f172a")
        opt2_frame.pack(fill="x", pady=(0, 10))

        rad_modify = tk.Radiobutton(
            opt2_frame,
            text="Modify / Custom Reinstall",
            variable=self.setup_mode,
            value="modify",
            command=self.on_setup_mode_changed,
            bg="#0f172a",
            fg="#f8fafc",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            font=("Segoe UI", 10, "bold")
        )
        rad_modify.pack(anchor="w")

        lbl_modify_desc = tk.Label(
            opt2_frame,
            text="Change the application installation folder, assign a different video storage drive,\n"
                 "or reconfigure desktop shortcuts and Windows Firewall rules.",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg="#0f172a",
            justify="left"
        )
        lbl_modify_desc.pack(anchor="w", padx=24, pady=(2, 0))

        # Optional bottom bar with Uninstaller button
        bottom_bar = tk.Frame(self.container, bg="#0f172a")
        bottom_bar.pack(fill="x", pady=(8, 0))

        btn_uninst = tk.Button(
            bottom_bar,
            text="Launch Uninstaller...",
            command=self.launch_uninstaller,
            bg="#1e293b",
            fg="#ef4444",
            activebackground="#334155",
            activeforeground="#f87171",
            relief="flat",
            font=("Segoe UI", 8),
            padx=10,
            pady=3,
            cursor="hand2"
        )
        btn_uninst.pack(side="left")

        self.on_setup_mode_changed()

    def on_setup_mode_changed(self):
        if self.setup_mode.get() == "repair":
            self.btn_next.config(
                text="Update / Repair Now",
                state="normal",
                bg="#16a34a",
                activebackground="#15803d"
            )
        else:
            self.btn_next.config(
                text="Next >",
                state="normal",
                bg="#2563eb",
                activebackground="#1d4ed8"
            )

    def launch_uninstaller(self):
        if not self.existing_install:
            return
        uninst_exe = os.path.join(self.existing_install["install_dir"], "Uninstall.exe")
        if os.path.exists(uninst_exe):
            if messagebox.askyesno(
                "Uninstall Provenance",
                "Do you want to launch the Provenance Uninstaller to remove this application?",
                parent=self
            ):
                try:
                    subprocess.Popen([uninst_exe], cwd=self.existing_install["install_dir"])
                    self.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to launch uninstaller: {e}", parent=self)
        else:
            messagebox.showwarning(
                "Uninstaller Not Found",
                f"Could not locate Uninstall.exe in {self.existing_install['install_dir']}.",
                parent=self
            )

    # --- STEP 1: WELCOME & LICENSE ---
    def render_step_1_welcome(self):
        self.header_subtitle.config(text="Step 1 of 5: Welcome & System Overview")
        self.btn_back.config(state="disabled")
        self.btn_next.config(text="Next >", state="normal", bg="#2563eb")

        lbl_lead = tk.Label(
            self.container,
            text="Welcome to the Provenance Workstation Setup Wizard",
            font=("Segoe UI", 12, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        )
        lbl_lead.pack(anchor="w", pady=(8, 8))

        admin_badge = "Administrator Mode Active" if is_admin() else "Standard User Mode (Installing to LocalAppData)"
        badge_fg = "#22c55e" if is_admin() else "#38bdf8"
        tk.Label(
            self.container,
            text=f"• System Privilege: {admin_badge}",
            font=("Segoe UI", 9, "bold"),
            fg=badge_fg,
            bg="#0f172a"
        ).pack(anchor="w", pady=(0, 10))

        lbl_desc = tk.Label(
            self.container,
            text="Provenance provides real-time CCTV proof, barcode synchronization, and cryptographic SHA-256\n"
                 "evidence archiving for high-throughput warehouse packing benches.\n\n"
                 "This wizard will configure the application binaries, assign a dedicated video storage location,\n"
                 "authorize local firewall rules for streaming, and anchor workstation node licensing.",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0f172a",
            justify="left"
        )
        lbl_desc.pack(anchor="w", pady=(0, 14))

        box_eula = tk.Text(self.container, height=8, bg="#1e293b", fg="#94a3b8", font=("Consolas", 8), relief="flat", padx=10, pady=8)
        box_eula.insert("1.0", (
            "PROVENANCE END-USER LICENSE & INTEGRITY NOTICE:\n\n"
            "1. This software is node-locked to authorized workstation hardware.\n"
            "2. Cryptographic audit trails and SHA-256 hashes generated during packing sessions are\n"
            "   permanent and protected from local tampering.\n"
            "3. Packaging video clips are stored directly on the destination drive selected during setup.\n"
            "   Ensure sufficient disk capacity is maintained for shift retention requirements."
        ))
        box_eula.config(state="disabled")
        box_eula.pack(fill="x", pady=(0, 10))

    # --- STEP 2: INSTALLATION DIRECTORY ---
    def render_step_2_install_dir(self):
        self.header_subtitle.config(text="Step 2 of 5: Application Installation Directory")
        self.btn_back.config(state="normal")
        self.btn_next.config(text="Next >", state="normal")

        tk.Label(
            self.container,
            text="Select Destination Directory",
            font=("Segoe UI", 12, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        ).pack(anchor="w", pady=(8, 6))

        tk.Label(
            self.container,
            text="Setup will install the core Provenance executable and offline engine files to this folder:",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0f172a"
        ).pack(anchor="w", pady=(0, 12))

        entry_frame = tk.Frame(self.container, bg="#0f172a")
        entry_frame.pack(fill="x", pady=(0, 12))

        entry_path = tk.Entry(
            entry_frame,
            textvariable=self.install_dir,
            font=("Segoe UI", 10),
            bg="#1e293b",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat"
        )
        entry_path.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        btn_browse = tk.Button(
            entry_frame,
            text="Browse...",
            command=self.browse_install_dir,
            bg="#334155",
            fg="#f8fafc",
            font=("Segoe UI", 9),
            relief="flat",
            padx=14,
            pady=4,
            cursor="hand2"
        )
        btn_browse.pack(side="right")

        free_gb = get_drive_free_gb(self.install_dir.get())
        self.lbl_space = tk.Label(
            self.container,
            text=f"Drive free space: {free_gb} GB available. (Requires ~85 MB)",
            font=("Segoe UI", 9),
            fg="#38bdf8",
            bg="#0f172a"
        )
        self.lbl_space.pack(anchor="w", pady=(4, 0))

    def browse_install_dir(self):
        sel = filedialog.askdirectory(initialdir=self.install_dir.get(), title="Select Provenance Installation Folder")
        if sel:
            self.install_dir.set(os.path.normpath(sel))
            free_gb = get_drive_free_gb(sel)
            self.lbl_space.config(text=f"Drive free space: {free_gb} GB available. (Requires ~85 MB)")

    # --- STEP 3: VIDEO CLIPS STORAGE LOCATION ---
    def render_step_3_clips_dir(self):
        self.header_subtitle.config(text="Step 3 of 5: Video Evidence Storage Location")
        self.btn_back.config(state="normal")
        self.btn_next.config(text="Next >", state="normal")

        tk.Label(
            self.container,
            text="Choose Where to Store Packaging Video Clips",
            font=("Segoe UI", 12, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        ).pack(anchor="w", pady=(8, 4))

        tk.Label(
            self.container,
            text="Recorded 1080p MP4 packaging sessions and cryptographic dispute proofs are saved here.\n"
                 "You can select the default location or choose a secondary high-capacity drive / partition.",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0f172a",
            justify="left"
        ).pack(anchor="w", pady=(0, 14))

        # Option A: Default Location
        rad_default = tk.Radiobutton(
            self.container,
            text=f"Default Storage Location (Recommended for this PC)",
            variable=self.clips_mode,
            value="default",
            command=self.toggle_clips_mode,
            bg="#0f172a",
            fg="#f8fafc",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold")
        )
        rad_default.pack(anchor="w", pady=(0, 2))

        lbl_def_path = tk.Label(
            self.container,
            text=f"  Path: {self.default_clips_dir}\n  (Setup will create this directory automatically with full write permissions)",
            font=("Consolas", 8),
            fg="#94a3b8",
            bg="#0f172a",
            justify="left"
        )
        lbl_def_path.pack(anchor="w", padx=24, pady=(0, 14))

        # Option B: Custom Location
        rad_custom = tk.Radiobutton(
            self.container,
            text="Custom Storage Location (Secondary SSD, HDD, or Mapped NAS Drive)",
            variable=self.clips_mode,
            value="custom",
            command=self.toggle_clips_mode,
            bg="#0f172a",
            fg="#f8fafc",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            font=("Segoe UI", 10, "bold")
        )
        rad_custom.pack(anchor="w", pady=(0, 6))

        self.custom_frame = tk.Frame(self.container, bg="#0f172a")
        self.custom_frame.pack(fill="x", padx=24, pady=(0, 10))

        self.entry_custom_clips = tk.Entry(
            self.custom_frame,
            textvariable=self.custom_clips_dir,
            font=("Segoe UI", 10),
            bg="#1e293b",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat"
        )
        self.entry_custom_clips.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        self.btn_browse_clips = tk.Button(
            self.custom_frame,
            text="Browse...",
            command=self.browse_clips_dir,
            bg="#334155",
            fg="#f8fafc",
            font=("Segoe UI", 9),
            relief="flat",
            padx=14,
            pady=4,
            cursor="hand2"
        )
        self.btn_browse_clips.pack(side="right")

        chosen_path = self.get_active_clips_path()
        free_gb = get_drive_free_gb(chosen_path)
        self.lbl_clips_space = tk.Label(
            self.container,
            text=f"Selected video drive has {free_gb} GB free storage space.",
            font=("Segoe UI", 9),
            fg="#10b981",
            bg="#0f172a"
        )
        self.lbl_clips_space.pack(anchor="w", padx=24, pady=(2, 0))

        self.toggle_clips_mode()

    def toggle_clips_mode(self):
        if self.clips_mode.get() == "default":
            self.entry_custom_clips.config(state="disabled", fg="#64748b")
            self.btn_browse_clips.config(state="disabled")
            chosen_path = self.default_clips_dir
        else:
            self.entry_custom_clips.config(state="normal", fg="#f8fafc")
            self.btn_browse_clips.config(state="normal")
            chosen_path = self.custom_clips_dir.get()
        free_gb = get_drive_free_gb(chosen_path)
        self.lbl_clips_space.config(text=f"Selected video drive has {free_gb} GB free storage space.")

    def browse_clips_dir(self):
        sel = filedialog.askdirectory(initialdir=self.custom_clips_dir.get(), title="Select Video Clips Storage Folder")
        if sel:
            norm = os.path.normpath(sel)
            self.custom_clips_dir.set(norm)
            free_gb = get_drive_free_gb(norm)
            self.lbl_clips_space.config(text=f"Selected video drive has {free_gb} GB free storage space.")

    def get_active_clips_path(self) -> str:
        if self.clips_mode.get() == "default":
            return self.default_clips_dir
        return os.path.normpath(self.custom_clips_dir.get().strip() or self.default_clips_dir)

    # --- STEP 4: OPTIONS & INTEGRATION ---
    def render_step_4_options(self):
        self.header_subtitle.config(text="Step 4 of 5: System Shortcuts & Integration")
        self.btn_back.config(state="normal")
        btn_text = "Reinstall / Apply Changes" if self.existing_install else "Install Now"
        self.btn_next.config(text=btn_text, state="normal", bg="#16a34a")

        tk.Label(
            self.container,
            text="Workstation Integration Settings",
            font=("Segoe UI", 12, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        ).pack(anchor="w", pady=(8, 6))

        tk.Label(
            self.container,
            text="Select optional tasks for this workstation bench:",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0f172a"
        ).pack(anchor="w", pady=(0, 14))

        cb_desk = tk.Checkbutton(
            self.container,
            text="Create Desktop Shortcut (Provenance.lnk)",
            variable=self.create_desktop_icon,
            bg="#0f172a",
            fg="#f8fafc",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            font=("Segoe UI", 9, "bold")
        )
        cb_desk.pack(anchor="w", pady=(0, 8))

        cb_start = tk.Checkbutton(
            self.container,
            text="Create Start Menu Program Group",
            variable=self.create_start_menu,
            bg="#0f172a",
            fg="#f8fafc",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            font=("Segoe UI", 9, "bold")
        )
        cb_start.pack(anchor="w", pady=(0, 8))

        cb_firewall = tk.Checkbutton(
            self.container,
            text="Authorize Inbound Windows Firewall Rule (TCP Port 5892 for CCTV/API)",
            variable=self.configure_firewall,
            bg="#0f172a",
            fg="#f8fafc",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            font=("Segoe UI", 9, "bold")
        )
        cb_firewall.pack(anchor="w", pady=(0, 16))

        # Summary box
        sum_box = tk.Frame(self.container, bg="#1e293b", padx=12, pady=10)
        sum_box.pack(fill="x", pady=(8, 0))

        tk.Label(sum_box, text="Configuration Summary:", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#1e293b").pack(anchor="w")
        tk.Label(sum_box, text=f"• Target Install Dir: {self.install_dir.get()}", font=("Consolas", 8), fg="#cbd5e1", bg="#1e293b").pack(anchor="w")
        tk.Label(sum_box, text=f"• Video Storage Dir: {self.get_active_clips_path()}", font=("Consolas", 8), fg="#cbd5e1", bg="#1e293b").pack(anchor="w")

    # --- STEP 5: INSTALLATION PROGRESS ---
    def render_step_5_installing(self):
        is_repair = (self.existing_install and self.setup_mode.get() == "repair")
        if is_repair:
            self.header_subtitle.config(text="Updating & Repairing Provenance Suite...")
        else:
            self.header_subtitle.config(text="Step 5 of 5: Installing Provenance Suite...")
        self.btn_back.config(state="disabled")
        self.btn_next.config(state="disabled", text="Updating..." if is_repair else "Installing...")
        self.btn_cancel.config(state="disabled")

        step_title = "Updating Files & Refreshing Components..." if is_repair else "Installing Files & Configuring Storage..."
        tk.Label(
            self.container,
            text=step_title,
            font=("Segoe UI", 12, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        ).pack(anchor="w", pady=(12, 8))

        self.progress_bar = ttk.Progressbar(self.container, orient="horizontal", length=650, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(10, 12))

        self.lbl_status = tk.Label(
            self.container,
            text="Initializing setup...",
            font=("Consolas", 9),
            fg="#94a3b8",
            bg="#0f172a"
        )
        self.lbl_status.pack(anchor="w")

        # Run background installation worker thread
        threading.Thread(target=self.run_installation_worker, daemon=True).start()

    def run_installation_worker(self):
        try:
            target = os.path.normpath(self.install_dir.get())
            clips = os.path.normpath(self.get_active_clips_path())

            # 1. Gracefully terminate any running Provenance instance
            self.update_progress(5, "Terminating any running Provenance instances...")
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/IM", "Provenance.exe"],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                time.sleep(0.6)

            # 2. Destination directories
            self.update_progress(10, f"Creating destination directory: {target}...")
            os.makedirs(target, exist_ok=True)
            os.makedirs(clips, exist_ok=True)

            p_target = os.path.abspath(target).lower()
            is_in_sys = any(p_target.startswith(sd) for sd in [
                os.environ.get("ProgramFiles", r"C:\Program Files").lower(),
                os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)").lower(),
                r"c:\program files",
                r"c:\program files (x86)",
                r"c:\windows"
            ])
            if is_in_sys:
                local_app = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
                app_data_dir = os.path.join(local_app, "Provenance", "data")
            else:
                app_data_dir = os.path.join(target, "data")
            os.makedirs(app_data_dir, exist_ok=True)

            # 3. Gather files to copy for granular, visible progress
            self.update_progress(15, "Enumerating payload files...")
            files_to_copy = []
            if os.path.exists(PAYLOAD_DIR):
                for root, dirs, files in os.walk(PAYLOAD_DIR):
                    rel = os.path.relpath(root, PAYLOAD_DIR)
                    if rel != "." and any(rel.startswith(p) for p in ["clips", "data"]):
                        continue
                    for f in files:
                        src_f = os.path.join(root, f)
                        dst_f = os.path.join(target, rel, f) if rel != "." else os.path.join(target, f)
                        files_to_copy.append((src_f, dst_f, f))

            total_files = len(files_to_copy)
            for idx, (src_f, dst_f, fname) in enumerate(files_to_copy):
                os.makedirs(os.path.dirname(dst_f), exist_ok=True)
                for attempt in range(5):
                    try:
                        shutil.copy2(src_f, dst_f)
                        break
                    except PermissionError:
                        if attempt < 4:
                            time.sleep(0.3)
                        else:
                            raise
                pct = 15 + int((idx / max(1, total_files)) * 55)
                if idx % 5 == 0 or idx == total_files - 1:
                    self.update_progress(pct, f"Installing: {fname} ({idx+1}/{total_files})...")

            # 4. Configure storage database settings in writable app data directory
            self.update_progress(72, f"Saving video clips storage path ({clips})...")
            db_path = os.path.join(app_data_dir, "barcode_test.db")
            with sqlite3.connect(db_path) as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);")
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('clips_dir', ?);", (clips,))
                conn.commit()

            # Ensure Program Files does not retain an accidental read-only database
            if is_in_sys:
                legacy_prog_data = os.path.join(target, "data")
                if os.path.exists(legacy_prog_data):
                    try:
                        shutil.rmtree(legacy_prog_data, ignore_errors=True)
                    except Exception:
                        pass

            # 5. Create Windows Shortcuts
            self.update_progress(80, "Generating desktop & start menu shortcuts...")
            if os.name == "nt":
                exe_target = os.path.join(target, "Provenance.exe")
                if self.create_desktop_icon.get():
                    for desk_path in get_all_desktop_paths():
                        self.make_shortcut(exe_target, os.path.join(desk_path, "Provenance.lnk"), target, "Provenance - CCTV Packing Station")

                if self.create_start_menu.get():
                    progs_path = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs", "Provenance")
                    os.makedirs(progs_path, exist_ok=True)
                    self.make_shortcut(exe_target, os.path.join(progs_path, "Provenance.lnk"), target, "Provenance - CCTV Packing Station")
                    uninst_target = os.path.join(target, "Uninstall.exe")
                    if os.path.exists(uninst_target):
                        self.make_shortcut(uninst_target, os.path.join(progs_path, "Uninstall Provenance.lnk"), target, "Uninstall Provenance")

            # 6. Windows Firewall Rule
            if self.configure_firewall.get() and os.name == "nt":
                self.update_progress(90, "Configuring Windows Firewall rule (Port 5892)...")
                try:
                    subprocess.run(
                        ["netsh", "advfirewall", "firewall", "add", "rule",
                         'name=Provenance CCTV API', 'dir=in', 'action=allow',
                         'protocol=TCP', 'localport=5892', f'program={os.path.join(target, "Provenance.exe")}'],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                except Exception as e:
                    print(f"Firewall warning: {e}")

            # 7. License audit
            self.update_progress(95, "Anchoring workstation hardware licensing...")
            lic_src = os.path.join(EXE_DIR, "provenance.lic")
            if os.path.exists(lic_src):
                shutil.copy2(lic_src, os.path.join(target, "provenance.lic"))

            # 8. Register in Windows Control Panel (appwiz.cpl & Settings > Apps)
            self.update_progress(98, "Registering in Windows Control Panel...")
            self.register_control_panel_uninstaller(target)

            self.update_progress(100, "Setup complete!")
            self.after(400, self.finish_installation)

        except Exception as e:
            err_msg = str(e)
            print(f"Installation error: {err_msg}", flush=True)
            self.after(0, lambda: self.show_install_error(err_msg))

    def register_control_panel_uninstaller(self, target_dir: str):
        if os.name != "nt":
            return
        try:
            import winreg
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Provenance"
            root = winreg.HKEY_LOCAL_MACHINE if is_admin() else winreg.HKEY_CURRENT_USER
            with winreg.CreateKeyEx(root, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as k:
                winreg.SetValueEx(k, "DisplayName", 0, winreg.REG_SZ, "Provenance - Industrial CCTV Proof & Packing Station")
                winreg.SetValueEx(k, "DisplayVersion", 0, winreg.REG_SZ, INSTALLER_VERSION)
                winreg.SetValueEx(k, "Publisher", 0, winreg.REG_SZ, "Provenance Systems")
                winreg.SetValueEx(k, "DisplayIcon", 0, winreg.REG_SZ, f'"{os.path.join(target_dir, "Provenance.exe")}",0')
                winreg.SetValueEx(k, "UninstallString", 0, winreg.REG_SZ, f'"{os.path.join(target_dir, "Uninstall.exe")}"')
                winreg.SetValueEx(k, "QuietUninstallString", 0, winreg.REG_SZ, f'"{os.path.join(target_dir, "Uninstall.exe")}" /quiet')
                winreg.SetValueEx(k, "InstallLocation", 0, winreg.REG_SZ, target_dir)
                winreg.SetValueEx(k, "InstallDate", 0, winreg.REG_SZ, time.strftime("%Y%m%d"))
                winreg.SetValueEx(k, "URLInfoAbout", 0, winreg.REG_SZ, "http://127.0.0.1:5892")
                winreg.SetValueEx(k, "HelpLink", 0, winreg.REG_SZ, "http://127.0.0.1:5892")
                winreg.SetValueEx(k, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(k, "NoRepair", 0, winreg.REG_DWORD, 1)
                try:
                    total_bytes = sum(
                        os.path.getsize(os.path.join(r, f))
                        for r, _, files in os.walk(target_dir)
                        for f in files
                    )
                    winreg.SetValueEx(k, "EstimatedSize", 0, winreg.REG_DWORD, max(1, total_bytes // 1024))
                except Exception:
                    pass
        except Exception as e:
            print(f"Warning registering uninstaller: {e}")

    def make_shortcut(self, target_exe: str, shortcut_path: str, working_dir: str, description: str):
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            sc = shell.CreateShortCut(shortcut_path)
            sc.TargetPath = target_exe
            sc.WorkingDirectory = working_dir
            sc.Description = description
            sc.save()
            return
        except Exception:
            pass
        try:
            ps_code = f"$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('{shortcut_path}'); $s.TargetPath = '{target_exe}'; $s.WorkingDirectory = '{working_dir}'; $s.Description = '{description}'; $s.Save()"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_code], creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0, timeout=5)
        except Exception as e:
            print(f"Shortcut warning: {e}")

    def show_install_error(self, err_msg: str):
        self.lbl_status.config(text=f"ERROR: {err_msg}", fg="#ef4444")
        self.btn_cancel.config(state="normal")
        self.btn_back.config(state="normal")
        auto_flags = ("--auto-update", "/VERYSILENT", "--silent")
        if not any(f in sys.argv for f in auto_flags):
            messagebox.showerror(
                "Installation Failed",
                f"Provenance could not complete installation.\n\nError:\n{err_msg}\n\nTip: Run as Administrator or choose an installation directory with write access.",
                parent=self
            )
        else:
            self.after(3000, self.destroy)

    def update_progress(self, percent: int, text: str):
        self.after(0, lambda: (self.progress_bar.config(value=percent), self.lbl_status.config(text=text)))

    def finish_installation(self):
        self.current_step = 6
        self.render_step()
        auto_flags = ("--auto-update", "/VERYSILENT", "--silent")
        if any(f in sys.argv for f in auto_flags):
            self.after(1000, self.on_finish)

    # --- STEP 6: FINISHED ---
    def render_step_6_finished(self):
        is_repair = (self.existing_install and self.setup_mode.get() == "repair")
        self.header_subtitle.config(text="Update & Repair Complete" if is_repair else "Installation Complete")
        self.btn_back.pack_forget()
        self.btn_cancel.pack_forget()
        self.btn_next.config(text="Finish", state="normal", bg="#16a34a", command=self.on_finish)

        title_text = "✓ Provenance Successfully Updated & Repaired!" if is_repair else "✓ Provenance Successfully Installed!"
        tk.Label(
            self.container,
            text=title_text,
            font=("Segoe UI", 14, "bold"),
            fg="#22c55e",
            bg="#0f172a"
        ).pack(anchor="w", pady=(14, 8))

        if is_repair:
            desc_text = (
                "Provenance has been refreshed with the latest application files and UI.\n\n"
                f"• Application: {self.install_dir.get()}\\Provenance.exe\n"
                f"• Video Storage: {self.get_active_clips_path()}\n"
                "• Preserved Data: Existing packing database records and video proofs remain intact."
            )
        else:
            desc_text = (
                "Provenance is now configured and ready for packing bench operations.\n\n"
                f"• Application: {self.install_dir.get()}\\Provenance.exe\n"
                f"• Video Storage: {self.get_active_clips_path()}\n"
                "• Local CCTV Server: Port 5892 (Firewall Authorized)"
            )

        tk.Label(
            self.container,
            text=desc_text,
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0f172a",
            justify="left"
        ).pack(anchor="w", pady=(0, 20))

        cb_launch = tk.Checkbutton(
            self.container,
            text="Launch Provenance Now",
            variable=self.launch_after,
            bg="#0f172a",
            fg="#f8fafc",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            font=("Segoe UI", 10, "bold")
        )
        cb_launch.pack(anchor="w", pady=(0, 10))

    def on_next(self):
        if self.current_step == 1 and self.existing_install and self.setup_mode.get() == "repair":
            self.current_step = 5
            self.render_step()
            return

        if self.current_step < self.total_steps:
            self.current_step += 1
            self.render_step()

    def on_back(self):
        if self.current_step > 1:
            self.current_step -= 1
            self.render_step()

    def on_finish(self):
        if self.launch_after.get():
            target_exe = os.path.join(self.install_dir.get(), "Provenance.exe")
            if os.path.exists(target_exe):
                subprocess.Popen([target_exe], cwd=self.install_dir.get())
        self.destroy()

    def on_cancel(self):
        if messagebox.askyesno("Cancel Setup", "Are you sure you want to cancel the Provenance installation?", parent=self):
            self.destroy()


def main():
    # If not admin, attempt elevation once
    if os.name == "nt" and not is_admin() and "--no-elevate" not in sys.argv:
        try:
            from ctypes import wintypes
            args_str = " ".join(f'"{a}"' for a in sys.argv[1:])
            params = f'"{__file__}" {args_str}' if not getattr(sys, "frozen", False) else args_str
            hwnd = ctypes.windll.user32.GetForegroundWindow() or ctypes.windll.user32.GetDesktopWindow()
            ctypes.windll.shell32.ShellExecuteW.restype = wintypes.HINSTANCE
            ret = ctypes.windll.shell32.ShellExecuteW(
                hwnd, "runas", sys.executable, params.strip(), None, 1
            )
            val = ret if isinstance(ret, int) else (getattr(ret, "value", 0) or 0)
            if val > 32 or val == 0:
                os._exit(0)
        except Exception:
            pass

    app = SetupWizardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
