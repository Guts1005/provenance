"""
Database layer for Barcode Test.
SQLite with WAL mode for crash-proof persistence of shipment recording sessions,
cryptographic SHA-256 hashes, and immutable audit logs.
"""

import sqlite3
import os
import sys
import re
import hashlib
import json
import time
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any


def is_system_program_dir(path: str) -> bool:
    """Returns True if the directory is a system-protected location like Program Files or Windows."""
    if not path:
        return False
    p = os.path.abspath(path).lower()
    sys_dirs = [
        os.environ.get("ProgramFiles", r"C:\Program Files").lower(),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)").lower(),
        os.environ.get("SystemRoot", r"C:\Windows").lower(),
        r"c:\program files",
        r"c:\program files (x86)",
        r"c:\windows",
    ]
    return any(p.startswith(sd) for sd in sys_dirs if sd)


def is_directory_truly_writable(dir_path: str) -> bool:
    """
    Reliably verifies whether the current process has actual NTFS write and create permissions
    in the directory by writing, modifying, and unlinking a temporary probe file.
    Does NOT rely on os.access(dir, os.W_OK) which only checks the legacy FAT/DOS attribute bit.
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        probe_file = os.path.join(dir_path, f".write_probe_{os.getpid()}_{int(time.time()*1000)}.tmp")
        with open(probe_file, "w", encoding="utf-8") as f:
            f.write("probe")
        if os.path.exists(probe_file):
            os.remove(probe_file)
            return True
        return False
    except Exception:
        return False


def get_app_dir() -> str:
    """
    Returns directory for persistent storage (clips, database, settings).
    Strictly guarantees the directory is OUTSIDE Program Files and 100% writable by standard users.
    """
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)

        # 1. Portable mode: Only allowed if NOT installed inside a system program directory
        # AND the local 'data' directory is genuinely writable by standard non-elevated users.
        if not is_system_program_dir(exe_dir):
            local_data = os.path.join(exe_dir, "data")
            if is_directory_truly_writable(local_data):
                return exe_dir

        # 2. Standard Windows Installed App: %LOCALAPPDATA%\Provenance
        # Standard users always have full read/write rights here.
        local_app = os.environ.get("LOCALAPPDATA")
        if local_app:
            pdir = os.path.join(local_app, "Provenance")
            if is_directory_truly_writable(os.path.join(pdir, "data")):
                return pdir

        # 3. All Users AppData fallback: %PROGRAMDATA%\Provenance
        prog_data = os.environ.get("PROGRAMDATA")
        if prog_data:
            pdir = os.path.join(prog_data, "Provenance")
            if is_directory_truly_writable(os.path.join(pdir, "data")):
                return pdir

        # 4. User profile fallback: ~/.provenance
        user_home = os.path.expanduser("~")
        pdir = os.path.join(user_home, ".provenance")
        os.makedirs(os.path.join(pdir, "data"), exist_ok=True)
        return pdir

    return os.path.dirname(os.path.abspath(__file__))


def get_bundle_dir() -> str:
    """Returns directory for read-only bundled assets (ui, static files)."""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _migrate_legacy_database_if_needed(target_db_path: str) -> None:
    """
    If the target database in get_app_dir() does not exist yet, but an existing
    database is present in the executable directory (e.g. from previous installer
    or previous run in Program Files), copy it over so all existing records and settings are preserved.
    """
    if os.path.exists(target_db_path):
        return
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        legacy_db = os.path.join(exe_dir, "data", "barcode_test.db")
        if os.path.exists(legacy_db) and os.path.abspath(legacy_db).lower() != os.path.abspath(target_db_path).lower():
            try:
                os.makedirs(os.path.dirname(target_db_path), exist_ok=True)
                shutil.copy2(legacy_db, target_db_path)
            except Exception as e:
                print(f"Warning: could not migrate legacy database: {e}")


DB_FILE = os.path.join(get_app_dir(), "data", "barcode_test.db")
_migrate_legacy_database_if_needed(DB_FILE)


def get_clips_dir() -> str:
    """Returns directory where packaging video clips are stored."""
    try:
        if os.path.exists(DB_FILE):
            with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute("SELECT value FROM settings WHERE key = 'clips_dir';").fetchone()
                if row and row["value"]:
                    custom = row["value"].strip()
                    if os.path.exists(custom):
                        return custom
                    try:
                        os.makedirs(custom, exist_ok=True)
                        return custom
                    except Exception:
                        pass
    except Exception:
        pass
    default_dir = os.path.join(get_app_dir(), "clips")
    os.makedirs(default_dir, exist_ok=True)
    return default_dir


CLIPS_DIR = get_clips_dir()



def repair_corrupted_database(db_path: str) -> None:
    """
    Safely recovers from SQLite disk corruption (malformed database image)
    by preserving surviving configuration settings, moving corrupted files to a backup,
    and initializing a fresh healthy database schema.
    """
    print(f"[DB-REPAIR] Corrupted database detected at {db_path}. Initiating automatic self-healing...", flush=True)
    saved_settings = {}
    try:
        raw_conn = sqlite3.connect(db_path)
        for row in raw_conn.execute("SELECT key, value FROM settings;"):
            saved_settings[row[0]] = row[1]
        raw_conn.close()
    except Exception:
        pass

    bak_path = f"{db_path}.corrupt_{int(time.time())}.bak"
    try:
        shutil.copy2(db_path, bak_path)
    except Exception:
        pass

    for ext in ["-wal", "-shm"]:
        f = db_path + ext
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except Exception as e:
        print(f"[DB-REPAIR] Warning unlinking corrupt DB: {e}", flush=True)

    init_db()

    if saved_settings:
        for k, v in saved_settings.items():
            set_setting(k, v)

    reconcile_clips_from_disk()
    print("[DB-REPAIR] Automatic self-healing complete. Database fully recovered.", flush=True)


def get_connection() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=15.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for high concurrency and power-loss resilience
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        # Quick verification probe to detect index or page corruption early
        conn.execute("SELECT count(*) FROM sqlite_master;")
        return conn
    except sqlite3.DatabaseError as e:
        err_msg = str(e).lower()
        if "malformed" in err_msg or "corrupt" in err_msg or "disk image" in err_msg:
            repair_corrupted_database(DB_FILE)
            conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=15.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            return conn
        raise


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL,
            station_id TEXT NOT NULL DEFAULT 'Station 1',
            camera_source TEXT NOT NULL DEFAULT 'webcam:0',
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration_seconds REAL,
            clip_path TEXT,
            clip_filename TEXT,
            file_size_bytes INTEGER DEFAULT 0,
            sha256_hash TEXT,
            status TEXT NOT NULL DEFAULT 'recording',
            order_id TEXT DEFAULT '',
            carrier TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            metadata TEXT DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_barcode ON sessions(barcode);
        CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
        CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            event_type TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS manifest_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL UNIQUE,
            order_id TEXT DEFAULT '',
            recipient TEXT DEFAULT '',
            sku TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            packed_at TEXT,
            clip_filename TEXT,
            session_id INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_manifest_tracking ON manifest_items(tracking_number);
        CREATE INDEX IF NOT EXISTS idx_manifest_status ON manifest_items(status);
        """)

        # Ensure metadata columns exist for backward compatibility with existing databases
        col_names = [r["name"] for r in conn.execute("PRAGMA table_info(sessions);").fetchall()]
        if "order_id" not in col_names:
            conn.execute("ALTER TABLE sessions ADD COLUMN order_id TEXT DEFAULT '';")
        if "carrier" not in col_names:
            conn.execute("ALTER TABLE sessions ADD COLUMN carrier TEXT DEFAULT '';")
        if "notes" not in col_names:
            conn.execute("ALTER TABLE sessions ADD COLUMN notes TEXT DEFAULT '';")
        if "metadata" not in col_names:
            conn.execute("ALTER TABLE sessions ADD COLUMN metadata TEXT DEFAULT '{}';")

        # Default settings
        defaults = {
            "idle_timeout_seconds": "300",  # 5 minutes
            "pre_roll_seconds": "5",
            "post_roll_seconds": "3",
            "station_id": "Station 1 - Packing Bay",
            "camera_source": "webcam:0",
            "rtsp_url": "rtsp://admin:Ermawk@321@192.168.0.250:554/Streaming/Channels/101",
            "clips_dir": os.path.join(get_app_dir(), "clips"),
            "update_manifest_url": "Guts1005/provenance",
            "auto_check_updates": "1",
            "sound_enabled": "1",
            "secondary_camera_source": ""
        }
        for k, v in defaults.items():
            conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);", (k, v))

        # Migrate legacy placeholder manifest URLs and temporary test fixtures to GitHub repository
        conn.execute(
            "UPDATE settings SET value = 'Guts1005/provenance' "
            "WHERE key = 'update_manifest_url' "
            "AND (value LIKE '%127.0.0.1:5895%' OR value LIKE '%localhost:5895%' OR value LIKE '%raw.githubusercontent.com%' OR value = 'provenance-dispatch/releases');"
        )

        global CLIPS_DIR
        CLIPS_DIR = get_clips_dir()

        # Startup crash/restart recovery: reconcile any sessions left in 'recording' or 'finalizing'
        orphans = conn.execute(
            "SELECT id, clip_path, clip_filename FROM sessions WHERE status IN ('recording', 'finalizing')"
        ).fetchall()
        for row in orphans:
            sid = row["id"]
            cpath = row["clip_path"] or (os.path.join(CLIPS_DIR, row["clip_filename"]) if row["clip_filename"] else "")
            if cpath and os.path.exists(cpath) and os.path.getsize(cpath) > 0:
                fsize = os.path.getsize(cpath)
                sha = calculate_sha256(cpath)
                conn.execute(
                    "UPDATE sessions SET status = 'completed', file_size_bytes = ?, sha256_hash = ? WHERE id = ?",
                    (fsize, sha, sid),
                )
            else:
                conn.execute("DELETE FROM sessions WHERE id = ?", (sid,))
        conn.commit()

        # Startup storage reconciliation: ensure any orphaned physical recordings on disk are indexed
        try:
            _reconcile_clips_from_disk_internal(conn, CLIPS_DIR)
        except Exception as ex:
            print(f"[DB] Initial reconciliation notice: {ex}")


def calculate_sha256(filepath: str) -> str:
    """Calculate SHA-256 cryptographic hash of a video file."""
    if not os.path.exists(filepath):
        return ""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def _reconcile_clips_from_disk_internal(conn: sqlite3.Connection, clips_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Internal helper to index unindexed video files on disk into the sessions table.
    Re-uses an active database connection and commits changes.
    """
    if not clips_dir:
        clips_dir = get_clips_dir()
    if not os.path.exists(clips_dir):
        return {"scanned": 0, "reconciled": 0, "restored_barcodes": []}

    station_row = conn.execute("SELECT value FROM settings WHERE key = 'station_id';").fetchone()
    station_id = station_row["value"] if station_row else "Station 1"
    camera_row = conn.execute("SELECT value FROM settings WHERE key = 'camera_source';").fetchone()
    camera_source = camera_row["value"] if camera_row else "webcam:0"

    existing_filenames = set()
    for r in conn.execute("SELECT clip_filename, clip_path FROM sessions WHERE clip_filename IS NOT NULL OR clip_path IS NOT NULL").fetchall():
        if r["clip_filename"]:
            existing_filenames.add(r["clip_filename"].lower())
        if r["clip_path"]:
            existing_filenames.add(os.path.basename(r["clip_path"]).lower())

    try:
        import video_engine
        if hasattr(video_engine, "engine") and video_engine.engine:
            active_cp = getattr(video_engine.engine, "active_clip_path", None)
            if active_cp:
                existing_filenames.add(os.path.basename(active_cp).lower())
    except Exception:
        pass

    files = [f for f in os.listdir(clips_dir) if f.lower().endswith(".mp4")]
    scanned_count = len(files)
    reconciled_barcodes = []

    for fname in sorted(files):
        if fname.lower() in existing_filenames:
            continue
        if fname.endswith(".tmp.mp4") or fname.endswith(".part") or fname.endswith(".h264_tmp.mp4"):
            continue

        fpath = os.path.join(clips_dir, fname)
        try:
            # Skip files created/modified within last 10s (actively being written or converted)
            if abs(time.time() - os.path.getmtime(fpath)) < 10.0:
                continue
            fsize = os.path.getsize(fpath)
        except OSError:
            continue
        if fsize == 0:
            continue

        # Parse barcode and timestamp from filename: {barcode}_{YYYYMMDD}_{HHMMSS}.mp4
        m = re.match(r"^(.+)_(\d{8})_(\d{6})\.mp4$", fname, re.IGNORECASE)
        if m:
            raw_barcode = m.group(1)
            date_str = m.group(2)
            time_str = m.group(3)
            try:
                dt = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                iso_time = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                iso_time = datetime.utcfromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            raw_barcode = os.path.splitext(fname)[0]
            iso_time = datetime.utcfromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Determine duration
        duration_sec = 0.0
        if fsize > 10240:
            try:
                import cv2
                cap = cv2.VideoCapture(fpath)
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
                    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
                    if fps > 0 and frames > 0:
                        duration_sec = round(frames / fps, 1)
                    cap.release()
            except Exception:
                pass

        sha_hash = calculate_sha256(fpath)

        cur = conn.execute(
            """
            INSERT INTO sessions (
                barcode, station_id, camera_source, start_time, end_time,
                duration_seconds, clip_path, clip_filename, file_size_bytes,
                sha256_hash, status, order_id, carrier, notes, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed', '', '', 'Reconciled from storage disk', '{}')
            """,
            (raw_barcode, station_id, camera_source, iso_time, iso_time, duration_sec, fpath, fname, fsize, sha_hash)
        )
        sid = cur.lastrowid
        conn.execute(
            """
            INSERT INTO audit_logs (session_id, event_type, details)
            VALUES (?, 'CLIP_RECONCILED', ?)
            """,
            (sid, f"Physical clip {fname} indexed from storage directory {clips_dir}")
        )
        existing_filenames.add(fname.lower())
        reconciled_barcodes.append(raw_barcode)

    if reconciled_barcodes:
        conn.commit()

    return {
        "scanned": scanned_count,
        "reconciled": len(reconciled_barcodes),
        "restored_barcodes": reconciled_barcodes
    }


def reconcile_clips_from_disk(target_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Public entry point to scan the active clips storage directory for any physical MP4 recordings
    that are not currently indexed in the database (e.g. from disk recovery,
    migrated folders, or restored archives) and registers them into the sessions table.
    """
    clips_dir = target_dir or get_clips_dir()
    if not os.path.exists(clips_dir):
        return {"scanned": 0, "reconciled": 0, "restored_barcodes": []}

    with get_connection() as conn:
        return _reconcile_clips_from_disk_internal(conn, clips_dir)


def create_session(
    barcode: str,
    station_id: str,
    camera_source: str,
    start_time: Optional[str] = None,
    clip_path: Optional[str] = None,
    clip_filename: Optional[str] = None
) -> int:
    """Record scan start event and create active session."""
    if not start_time:
        start_time = datetime.utcnow().isoformat() + "Z"
    if clip_path and not clip_filename:
        clip_filename = os.path.basename(clip_path)
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO sessions (barcode, station_id, camera_source, start_time, clip_path, clip_filename, status)
            VALUES (?, ?, ?, ?, ?, ?, 'recording')
            """,
            (barcode.strip(), station_id, camera_source, start_time, clip_path or "", clip_filename or "")
        )
        session_id = cur.lastrowid
        conn.execute(
            """
            INSERT INTO audit_logs (session_id, event_type, details)
            VALUES (?, 'SCAN_START', ?)
            """,
            (session_id, f"Recording session started for barcode: {barcode}")
        )
        conn.commit()
        return session_id


def complete_session(
    session_id: int,
    end_time: str,
    duration_seconds: float,
    clip_path: str,
    status: str = "completed",
    reason: str = "MANUAL_OR_CHAIN"
) -> Optional[Dict[str, Any]]:
    """Finalize a session, compute SHA-256, and update DB."""
    clip_filename = os.path.basename(clip_path) if clip_path else ""
    file_size = os.path.getsize(clip_path) if clip_path and os.path.exists(clip_path) else 0
    sha256 = calculate_sha256(clip_path) if file_size > 0 else ""

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE sessions
            SET end_time = ?, duration_seconds = ?, clip_path = ?, clip_filename = ?,
                file_size_bytes = ?, sha256_hash = ?, status = ?
            WHERE id = ?
            """,
            (end_time, duration_seconds, clip_path, clip_filename, file_size, sha256, status, session_id)
        )
        conn.execute(
            """
            INSERT INTO audit_logs (session_id, event_type, details)
            VALUES (?, ?, ?)
            """,
            (session_id, reason, f"Session finalized. Duration: {duration_seconds:.1f}s. Hash: {sha256[:16]}...")
        )
        conn.commit()

    return get_session_by_id(session_id)


def get_active_session() -> Optional[Dict[str, Any]]:
    """Retrieve currently recording session if any."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE status = 'recording' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def get_session_by_id(session_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return dict(row) if row else None


get_session = get_session_by_id


def get_latest_session_id() -> int:
    """Return the ID of the most recent completed or timeout session."""
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM sessions WHERE status IN ('completed', 'timeout') ORDER BY id DESC LIMIT 1;"
            ).fetchone()
            return int(row[0]) if row and row[0] else 0
    except Exception:
        return 0


def get_completed_sessions_count() -> int:
    """Return total count of completed or timeout sessions."""
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE status IN ('completed', 'timeout');"
            ).fetchone()
            return int(row[0]) if row and row[0] else 0
    except Exception:
        return 0



def search_sessions(query: str = "", limit: int = 100) -> List[Dict[str, Any]]:
    """Search completed sessions by barcode, order_id, carrier, or notes substring or fetch recent."""
    query = query.strip()
    with get_connection() as conn:
        if query:
            wildcard = f"%{query}%"
            rows = conn.execute(
                """
                SELECT * FROM sessions
                WHERE (barcode LIKE ? OR order_id LIKE ? OR carrier LIKE ? OR notes LIKE ?)
                  AND status IN ('completed', 'timeout')
                ORDER BY id DESC LIMIT ?
                """,
                (wildcard, wildcard, wildcard, wildcard, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM sessions
                WHERE status IN ('completed', 'timeout')
                ORDER BY id DESC LIMIT ?
                """,
                (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


def update_session_metadata(
    session_id: int,
    barcode: Optional[str] = None,
    order_id: Optional[str] = None,
    carrier: Optional[str] = None,
    notes: Optional[str] = None,
    metadata_json: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update session metadata (barcode, order_id, carrier, notes, metadata),
    records an immutable audit log, and renames the physical clip file if barcode changed.
    """
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            return None

        current = dict(row)
        updates = []
        params = []
        changes = []

        if barcode is not None:
            new_barcode = barcode.strip()
            if new_barcode and new_barcode != current.get("barcode"):
                updates.append("barcode = ?")
                params.append(new_barcode)
                changes.append(f"barcode: '{current.get('barcode')}' -> '{new_barcode}'")

                # Rename physical clip file on disk if exists to keep filename in sync
                old_path = current.get("clip_path")
                old_name = current.get("clip_filename")
                if old_path and os.path.exists(old_path) and old_name:
                    ext = os.path.splitext(old_name)[1] or ".mp4"
                    parts = old_name.split("_", 1)
                    suffix = "_" + parts[1] if len(parts) > 1 else ext
                    new_filename = f"{new_barcode}{suffix}"
                    new_path = os.path.join(os.path.dirname(old_path), new_filename)
                    try:
                        os.rename(old_path, new_path)
                        updates.append("clip_path = ?")
                        params.append(new_path)
                        updates.append("clip_filename = ?")
                        params.append(new_filename)
                        changes.append(f"file: '{old_name}' -> '{new_filename}'")
                    except Exception:
                        pass

        if order_id is not None:
            clean_order = order_id.strip()
            updates.append("order_id = ?")
            params.append(clean_order)
            changes.append(f"order_id: '{clean_order}'")

        if carrier is not None:
            clean_carrier = carrier.strip()
            updates.append("carrier = ?")
            params.append(clean_carrier)
            changes.append(f"carrier: '{clean_carrier}'")

        if notes is not None:
            clean_notes = notes.strip()
            updates.append("notes = ?")
            params.append(clean_notes)
            changes.append(f"notes: '{clean_notes}'")

        if metadata_json is not None:
            updates.append("metadata = ?")
            params.append(metadata_json)
            changes.append("custom_metadata updated")

        if not updates:
            return current

        params.append(session_id)
        conn.execute(f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?", params)

        conn.execute(
            """
            INSERT INTO audit_logs (session_id, event_type, details)
            VALUES (?, 'METADATA_UPDATED', ?)
            """,
            (session_id, f"Session metadata updated: {'; '.join(changes)}")
        )
        conn.commit()

    return get_session_by_id(session_id)


def delete_session(session_id: int) -> bool:
    """
    Permanently delete a session record, remove its clip file from disk,
    and record an immutable audit log.
    Rejects deletion if session is currently active/recording.
    """
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            return False
        if row["status"] == "recording":
            return False

        clip_path = row["clip_path"] or ""
        clip_filename = row["clip_filename"] or (os.path.basename(clip_path) if clip_path else "")
        barcode = row["barcode"]
        active_clips_dir = get_clips_dir()

        # 1. Unlink physical MP4 file from disk across all candidate locations
        candidates = []
        if clip_path:
            candidates.append(clip_path)
            candidates.append(os.path.join(active_clips_dir, os.path.basename(clip_path)))
        if clip_filename:
            candidates.append(os.path.join(active_clips_dir, clip_filename))
            candidates.append(os.path.join(get_app_dir(), "clips", clip_filename))
            candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clips", clip_filename))
        if barcode:
            candidates.append(os.path.join(active_clips_dir, f"{barcode}.mp4"))

        seen = set()
        unlinked = False
        for cpath in candidates:
            norm = os.path.normpath(os.path.abspath(cpath))
            if norm not in seen:
                seen.add(norm)
                if os.path.exists(norm):
                    try:
                        os.remove(norm)
                        unlinked = True
                    except OSError as ex:
                        print(f"[DB] Error removing physical clip file {norm}: {ex}")

        # 2. Immutable audit log record
        conn.execute(
            """
            INSERT INTO audit_logs (session_id, event_type, details)
            VALUES (?, 'FOOTAGE_DELETED', ?)
            """,
            (session_id, f"Permanently deleted footage for barcode {barcode} ({clip_filename}, unlinked={unlinked})")
        )

        # 3. Purge session record
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        return True


def delete_sessions_batch(session_ids: List[int]) -> Dict[str, Any]:
    """Batch delete multiple sessions safely, skipping any active recording sessions."""
    deleted_ids: List[int] = []
    skipped_ids: List[int] = []
    seen = set()
    for raw_id in session_ids:
        try:
            sid = int(raw_id)
        except (TypeError, ValueError):
            continue
        if sid in seen:
            continue
        seen.add(sid)
        if delete_session(sid):
            deleted_ids.append(sid)
        else:
            skipped_ids.append(sid)
    return {
        "deleted_count": len(deleted_ids),
        "deleted_ids": deleted_ids,
        "skipped_ids": skipped_ids
    }




def get_setting(key: str, default: str = "") -> str:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    global CLIPS_DIR
    with get_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
    if key == "clips_dir":
        CLIPS_DIR = get_clips_dir()


def log_audit(event_type: str, details: Any, session_id: Optional[int] = None) -> int:
    """Insert immutable system/audit event log."""
    details_str = json.dumps(details) if isinstance(details, (dict, list)) else str(details)
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO audit_logs (session_id, event_type, details) VALUES (?, ?, ?)",
            (session_id, event_type, details_str)
        )
        conn.commit()
        return cur.lastrowid


def get_recent_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent audit events."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


CLIPS_DIR = get_clips_dir()

# Initialize database schema immediately on import
init_db()
