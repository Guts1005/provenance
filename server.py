"""
Bottle HTTP Server & IPC API for Barcode Test Desktop App.
Serves static UI, live camera MJPEG stream, video range requests, and session endpoints.
"""

import os
import sys
import json
import time
import subprocess
import csv
import io
import zipfile
from datetime import datetime
from bottle import Bottle, request, response, static_file
import database
import video_engine
import updater
import sound_effects
import manifest_manager

# Initialize sound configuration from database
sound_effects.set_sound_enabled(database.get_setting("sound_enabled", "1") == "1")

BASE_DIR = database.get_app_dir()
BUNDLE_DIR = database.get_bundle_dir()
UI_DIR = os.path.join(BUNDLE_DIR, "ui")
CLIPS_DIR = database.CLIPS_DIR

app = Bottle()


@app.hook('after_request')
def apply_security_headers():
    # ponytail: zero-overhead defense-in-depth security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'no-referrer'


@app.route("/")
def index():
    return static_file("index.html", root=UI_DIR)


@app.route("/static/<filepath:path>")
def serve_static(filepath):
    return static_file(filepath, root=UI_DIR)


@app.route("/clips/<filepath:path>")
def serve_clip(filepath):
    # Support ?download=1 to force Content-Disposition attachment header
    is_download = request.query.get("download") in ("1", "true", "yes")
    return static_file(
        filepath,
        root=database.get_clips_dir(),
        mimetype="video/mp4",
        download=os.path.basename(filepath) if is_download else False
    )


@app.route("/api/clips/download/<filepath:path>")
def download_clip(filepath):
    """Direct forced attachment download endpoint for MP4 evidence clips."""
    # ponytail: sanitize basename to prevent path traversal
    filename = os.path.basename(filepath)
    return static_file(
        filename,
        root=database.get_clips_dir(),
        mimetype="video/mp4",
        download=filename
    )


@app.route("/api/camera/stream")
def camera_stream():
    """Multipart MJPEG video stream with event-driven wire-speed delivery."""
    if not video_engine.engine.running:
        source = database.get_setting("camera_source", "webcam:0")
        video_engine.engine.set_camera_source(source)
        video_engine.engine.start()

    response.content_type = "multipart/x-mixed-replace; boundary=frame"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    def frame_generator():
        try:
            while True:
                with video_engine.engine.frame_condition:
                    video_engine.engine.frame_condition.wait(timeout=0.04)
                    frame_bytes = video_engine.engine.cached_jpeg_bytes
                if frame_bytes:
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n" +
                        frame_bytes + b"\r\n"
                    )
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError, GeneratorExit):
            return

    return frame_generator()


@app.route("/api/camera/status", method="GET")
def camera_status():
    response.content_type = "application/json"
    status = video_engine.engine.get_status()
    return json.dumps(status)


@app.route("/api/camera/source", method="POST")
def change_camera_source():
    response.content_type = "application/json"
    try:
        data = request.json or {}
        source = data.get("source", "webcam:0")
        success = video_engine.engine.set_camera_source(source)
        return json.dumps({"success": success, "camera_source": source})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/camera/devices", method="GET")
@app.route("/api/camera/scan", method="GET")
def camera_devices_endpoint():
    """Enumerate connected USB webcams and probe configured RTSP streams."""
    response.content_type = "application/json"
    try:
        devices = video_engine.scan_available_cameras()
        return json.dumps({
            "success": True,
            "devices": devices,
            "current_source": video_engine.engine.camera_source
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "devices": []})


@app.route("/api/camera/test", method="POST")
def test_camera_endpoint():
    """Diagnostic endpoint to test RTSP / Webcam / Simulator connectivity before or during use."""
    response.content_type = "application/json"
    try:
        data = request.json or {}
        source = (data.get("source") or "").strip()
        if not source or source.lower() == "rtsp":
            source = database.get_setting("rtsp_url", "").strip()
        if not source:
            return json.dumps({"success": False, "stage": "VALIDATION", "message": "Missing camera source", "error": "Missing camera source"})

        if source.startswith("simulator"):
            return json.dumps({
                "success": True,
                "stage": "SIMULATOR_READY",
                "reachable": True,
                "auth_ok": True,
                "message": "Built-in Demo Simulator ready (640x480 @ 20 FPS)",
                "latency_ms": 0.5,
            })

        if source.startswith("webcam:"):
            return json.dumps({
                "success": True,
                "stage": "WEBCAM_READY",
                "reachable": True,
                "auth_ok": True,
                "message": f"Local {source} capture device configured",
                "latency_ms": 1.0,
            })

        diag = video_engine.test_rtsp_connection(source, timeout=2.5)
        if "stage" not in diag:
            diag["stage"] = "RTSP_OK" if diag.get("success") else ("RTSP_AUTH" if diag.get("reachable") else "TCP_CONNECT")
        if not diag.get("success") and "error" not in diag:
            diag["error"] = diag.get("message", "RTSP diagnostic failed")
        return json.dumps(diag)
    except Exception as e:
        return json.dumps({"success": False, "stage": "ERROR", "message": str(e), "error": str(e)})


@app.route("/api/session/start", method="POST")
@app.route("/api/start", method="POST")
def session_start():
    response.content_type = "application/json"
    try:
        data = request.json or {}
        barcode = data.get("barcode", "").strip()
        if not barcode:
            sound_effects.play_error_buzz()
            return json.dumps({"success": False, "error": "Barcode cannot be empty"})

        result = video_engine.engine.start_session(barcode)
        if result.get("success"):
            sid = result.get("session_id")
            manifest_res = manifest_manager.check_and_mark_packed(barcode, session_id=sid)
            result["manifest_match"] = manifest_res.get("found", False)
            result["manifest_already_packed"] = manifest_res.get("already_packed", False)
            if manifest_res.get("item"):
                result["manifest_item"] = manifest_res["item"]

            if manifest_res.get("already_packed"):
                sound_effects.play_error_buzz()
            elif manifest_res.get("found"):
                sound_effects.play_success_ding()
            else:
                sound_effects.play_record_start()

            result["session"] = {
                "id": sid,
                "barcode": result.get("barcode"),
                "start_time": result.get("start_time"),
                "clip_path": result.get("clip_path")
            }
        else:
            sound_effects.play_error_buzz()
        return json.dumps(result)
    except Exception as e:
        sound_effects.play_error_buzz()
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/session/finish", method="POST")
@app.route("/api/stop", method="POST")
def session_finish():
    response.content_type = "application/json"
    try:
        data = request.json or {}
        reason = data.get("reason", "MANUAL_FINISH")
        result = video_engine.engine.finish_session(reason=reason)
        if result.get("success"):
            sound_effects.play_record_finish()
            result["session"] = {
                "id": result.get("session_id"),
                "barcode": result.get("barcode"),
                "duration_seconds": result.get("duration_seconds"),
                "clip_path": result.get("clip_path"),
                "status": result.get("status")
            }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/status", method="GET")
def get_status_overview():
    response.content_type = "application/json"
    st = video_engine.engine.get_status()
    fps = st.get("actual_fps", 0)
    st["fps"] = fps
    st["camera"] = dict(st)
    st["camera"]["fps"] = fps
    is_rec = bool(st.get("is_recording") or st.get("recording"))
    st["recording"] = is_rec
    if is_rec:
        st["active_session"] = {
            "id": st.get("session_id"),
            "barcode": st.get("barcode"),
            "start_time": st.get("session_start_time")
        }
    st["latest_session_id"] = database.get_latest_session_id()
    st["completed_sessions_count"] = database.get_completed_sessions_count()
    try:
        upd = updater.manager.get_status_dict()
        st["update"] = upd
        st["update_available"] = bool(upd.get("update_available"))
        st["latest_version"] = upd.get("latest_version")
    except Exception:
        pass
    return json.dumps(st)


@app.route("/api/open_folder", method="POST")
def open_folder_alias():
    return open_clips_folder()


@app.route("/api/config", method=["GET", "POST"])
def config_alias():
    return handle_settings()


@app.route("/api/sessions", method="GET")
def list_sessions():
    response.content_type = "application/json"
    query = request.query.get("q", "").strip()
    sessions = database.search_sessions(query=query, limit=100)
    if not sessions and not query:
        # Auto-reconcile on initial empty load if physical clips exist on disk
        rec = database.reconcile_clips_from_disk()
        if rec.get("reconciled", 0) > 0:
            sessions = database.search_sessions(query=query, limit=100)
    return json.dumps({"sessions": sessions, "count": len(sessions)})


@app.route("/api/sessions/reconcile", method=["GET", "POST"])
@app.route("/api/sessions/sync", method=["GET", "POST"])
def reconcile_sessions_endpoint():
    response.content_type = "application/json"
    try:
        res = database.reconcile_clips_from_disk()
        return json.dumps({"success": True, **res})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/session/delete", method="POST")
def delete_session():
    response.content_type = "application/json"
    try:
        data = request.json or {}
        session_id = data.get("id")
        if not session_id:
            return json.dumps({"success": False, "error": "Missing session ID"})

        session_id = int(session_id)
        success = database.delete_session(session_id)
        if success:
            return json.dumps({"success": True, "deleted_id": session_id})
        else:
            return json.dumps({"success": False, "error": "Session not found or currently active"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/session/delete-batch", method="POST")
def delete_sessions_batch():
    response.content_type = "application/json"
    try:
        data = request.json or {}
        ids = data.get("ids")
        if not ids or not isinstance(ids, list):
            return json.dumps({"success": False, "error": "Missing or invalid session IDs list"})

        result = database.delete_sessions_batch(ids)
        if result["deleted_count"] > 0:
            return json.dumps({"success": True, **result})
        else:
            return json.dumps({
                "success": False,
                "error": "No removable sessions found (active sessions cannot be deleted)",
                **result
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})



@app.route("/api/session/<session_id:int>/delete", method=["POST", "DELETE"])
@app.route("/api/sessions/<session_id:int>/delete", method=["POST", "DELETE"])
def delete_session_by_id_endpoint(session_id: int):
    # ponytail: unified direct path parameter deletion endpoint
    response.content_type = "application/json"
    try:
        success = database.delete_session(session_id)
        return json.dumps({"success": success, "deleted_id": session_id})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/session/<session_id:int>/video", method="GET")
@app.route("/api/sessions/<session_id:int>/video", method="GET")
def stream_session_video(session_id: int):
    # ponytail: serve proof clip with range-request video support
    session = database.get_session_by_id(session_id)
    if not session:
        response.status = 404
        return "Session not found"
    clip_path = session.get("clip_path") or ""
    clip_name = session.get("clip_filename") or os.path.basename(clip_path)
    if not clip_name:
        response.status = 404
        return "Video filename missing"
    clips_dir = database.get_clips_dir()
    if not os.path.exists(os.path.join(clips_dir, clip_name)) and os.path.exists(clip_path):
        clips_dir = os.path.dirname(clip_path)
    return static_file(clip_name, root=clips_dir, mimetype="video/mp4")


@app.route("/api/session/<session_id:int>/metadata", method=["POST", "PUT"])
@app.route("/api/sessions/<session_id:int>/metadata", method=["POST", "PUT"])
def update_session_metadata_endpoint(session_id: int):
    """Update shipment/clip metadata: barcode, order ID, carrier, customer notes."""
    response.content_type = "application/json"
    try:
        data = request.json or {}
        barcode = data.get("barcode")
        order_id = data.get("order_id")
        carrier = data.get("carrier")
        notes = data.get("notes")
        meta = data.get("metadata")
        meta_str = json.dumps(meta) if isinstance(meta, dict) else (meta if isinstance(meta, str) else None)

        updated = database.update_session_metadata(
            session_id=session_id,
            barcode=barcode,
            order_id=order_id,
            carrier=carrier,
            notes=notes,
            metadata_json=meta_str
        )
        if updated:
            return json.dumps({"success": True, "session": updated})
        else:
            return json.dumps({"success": False, "error": f"Session {session_id} not found"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/export/csv", method="GET")
@app.route("/api/sessions/export/csv", method="GET")
def export_dispute_csv():
    """
    Generalized Dispute Evidence Manifest Export.
    Outputs standard RFC 4180 CSV containing dispute and tracking fields:
    Barcode, Order ID, Carrier, Notes, Status, Timestamp (UTC), Duration, File Size, SHA-256 Hash, Filename, Station ID.
    """
    query = request.query.get("q", "").strip()
    sessions = database.search_sessions(query=query, limit=1000)

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Standard dispute manifest headers with customer metadata fields
    writer.writerow([
        "Barcode",
        "Order_ID",
        "Carrier",
        "Notes",
        "Status",
        "Recorded_At_UTC",
        "Duration_Seconds",
        "File_Size_Readable",
        "File_Size_Bytes",
        "SHA256_Hash",
        "Clip_Filename",
        "Station_ID"
    ])

    for s in sessions:
        size_bytes = s.get("file_size_bytes") or 0
        size_kb = round(size_bytes / 1024)
        size_str = f"{size_kb / 1024:.2f} MB" if size_kb > 1024 else f"{size_kb} KB"
        duration = round(float(s.get("duration_seconds") or 0), 2)

        writer.writerow([
            s.get("barcode", ""),
            s.get("order_id", ""),
            s.get("carrier", ""),
            s.get("notes", ""),
            s.get("status", "").upper(),
            s.get("start_time", ""),
            duration,
            size_str,
            size_bytes,
            s.get("sha256_hash", ""),
            s.get("clip_filename", ""),
            s.get("station_id", "")
        ])

    csv_data = output.getvalue()
    now_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"shipment_dispute_manifest_{now_str}.csv"

    response.content_type = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return csv_data


def get_user_downloads_dir() -> str:
    """Return the user's Downloads or Desktop directory."""
    home = os.path.expanduser("~")
    dl = os.path.join(home, "Downloads")
    if os.path.exists(dl) and os.path.isdir(dl):
        return dl
    dt = os.path.join(home, "Desktop")
    if os.path.exists(dt) and os.path.isdir(dt):
        return dt
    return database.get_clips_dir()


@app.route("/api/sessions/export/csv/save", method="POST")
@app.route("/api/export/csv/save", method="POST")
def export_dispute_csv_save():
    """Save dispute manifest CSV directly into user's Downloads and reveal in Explorer."""
    response.content_type = "application/json"
    try:
        data = request.json or {}
        query = (data.get("q") or "").strip()
        sessions = database.search_sessions(query=query, limit=5000)

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
            "Barcode",
            "Order_ID",
            "Carrier",
            "Notes",
            "Status",
            "Recorded_At_UTC",
            "Duration_Seconds",
            "File_Size_Readable",
            "File_Size_Bytes",
            "SHA256_Hash",
            "Clip_Filename",
            "Station_ID"
        ])
        for s in sessions:
            size_bytes = s.get("file_size_bytes") or 0
            size_kb = round(size_bytes / 1024)
            size_str = f"{size_kb / 1024:.2f} MB" if size_kb > 1024 else f"{size_kb} KB"
            duration = round(float(s.get("duration_seconds") or 0), 2)
            writer.writerow([
                s.get("barcode", ""),
                s.get("order_id", ""),
                s.get("carrier", ""),
                s.get("notes", ""),
                s.get("status", "").upper(),
                s.get("start_time", ""),
                duration,
                size_str,
                size_bytes,
                s.get("sha256_hash", ""),
                s.get("clip_filename", ""),
                s.get("station_id", "")
            ])

        csv_data = output.getvalue()
        now_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"shipment_dispute_manifest_{now_str}.csv"
        target_dir = get_user_downloads_dir()
        out_path = os.path.join(target_dir, filename)

        with open(out_path, "w", encoding="utf-8", newline="") as f:
            f.write(csv_data)

        if sys.platform == "win32":
            subprocess.Popen(["explorer.exe", f"/select,{os.path.abspath(out_path)}"])

        return json.dumps({
            "success": True,
            "path": out_path,
            "filename": filename,
            "count": len(sessions)
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/sessions/export/package/save", method="POST")
@app.route("/api/export/package/save", method="POST")
def export_evidence_package_save():
    """Bundle selected recordings, metadata CSV, and SHA-256 certificate into a ZIP and reveal."""
    response.content_type = "application/json"
    try:
        data = request.json or {}
        session_ids = data.get("session_ids") or []
        query = (data.get("q") or "").strip()

        if session_ids:
            sessions = [database.get_session_by_id(sid) for sid in session_ids]
            sessions = [s for s in sessions if s]
        else:
            sessions = database.search_sessions(query=query, limit=100)

        if not sessions:
            return json.dumps({"success": False, "error": "No recordings found to export in evidence package."})

        now_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"Provenance_Dispute_Package_{now_str}.zip"
        target_dir = get_user_downloads_dir()
        zip_path = os.path.join(target_dir, zip_filename)

        clips_dir = os.path.abspath(database.get_clips_dir())

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            csv_buf = io.StringIO()
            csv_writer = csv.writer(csv_buf, quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([
                "Barcode", "Order_ID", "Carrier", "Notes", "Status",
                "Recorded_At_UTC", "Duration_Seconds", "SHA256_Hash", "Clip_Filename"
            ])

            cert_lines = [
                "PROVENANCE CRYPTOGRAPHIC CHAIN OF CUSTODY CERTIFICATE",
                f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                f"Total Bundled Evidence Clips: {len(sessions)}",
                "=" * 70,
                ""
            ]

            for s in sessions:
                csv_writer.writerow([
                    s.get("barcode", ""),
                    s.get("order_id", ""),
                    s.get("carrier", ""),
                    s.get("notes", ""),
                    s.get("status", "").upper(),
                    s.get("start_time", ""),
                    round(float(s.get("duration_seconds") or 0), 2),
                    s.get("sha256_hash", ""),
                    s.get("clip_filename", "")
                ])
                cert_lines.append(f"Barcode:     {s.get('barcode', '')}")
                cert_lines.append(f"Order ID:    {s.get('order_id', '')}")
                cert_lines.append(f"Recorded:    {s.get('start_time', '')} UTC")
                cert_lines.append(f"SHA-256:     {s.get('sha256_hash', 'N/A')}")
                cert_lines.append(f"Filename:    {s.get('clip_filename', '')}")
                cert_lines.append("-" * 50)

                cpath = s.get("clip_path")
                if not (cpath and os.path.exists(cpath)):
                    if s.get("clip_filename"):
                        candidate = os.path.join(clips_dir, s["clip_filename"])
                        if os.path.exists(candidate):
                            cpath = candidate
                if cpath and os.path.exists(cpath):
                    arcname = os.path.join("video_clips", os.path.basename(cpath))
                    zf.write(cpath, arcname=arcname)

            zf.writestr("dispute_manifest.csv", csv_buf.getvalue())
            zf.writestr("tamper_evidence_certificate.txt", "\n".join(cert_lines))

        if sys.platform == "win32":
            subprocess.Popen(["explorer.exe", f"/select,{os.path.abspath(zip_path)}"])

        return json.dumps({
            "success": True,
            "path": zip_path,
            "filename": zip_filename,
            "count": len(sessions)
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/manifest/progress", method="GET")
def api_manifest_progress():
    response.content_type = "application/json"
    return json.dumps(manifest_manager.get_manifest_progress())


@app.route("/api/manifest/import", method="POST")
def api_manifest_import():
    response.content_type = "application/json"
    try:
        data = request.json or {}
        csv_text = data.get("csv_text", "")
        replace = data.get("replace", False)
        res = manifest_manager.parse_and_import_manifest_csv(csv_text, replace_existing=replace)
        return json.dumps(res)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/manifest/items", method="GET")
def api_manifest_items():
    response.content_type = "application/json"
    status = request.query.get("status")
    return json.dumps(manifest_manager.get_manifest_items(status=status))


@app.route("/api/manifest/clear", method="POST")
def api_manifest_clear():
    response.content_type = "application/json"
    return json.dumps(manifest_manager.clear_manifest())


@app.route("/api/sound/status", method="GET")
def api_sound_status():
    response.content_type = "application/json"
    return json.dumps({"enabled": sound_effects.is_sound_enabled()})


@app.route("/api/sound/toggle", method="POST")
def api_sound_toggle():
    response.content_type = "application/json"
    data = request.json or {}
    new_state = data.get("enabled", not sound_effects.is_sound_enabled())
    sound_effects.set_sound_enabled(new_state)
    database.set_setting("sound_enabled", "1" if new_state else "0")
    return json.dumps({"success": True, "enabled": sound_effects.is_sound_enabled()})


@app.route("/api/sound/test", method="POST")
def api_sound_test():
    response.content_type = "application/json"
    data = request.json or {}
    stype = data.get("type", "success")
    if stype == "success":
        sound_effects.play_success_ding()
    elif stype == "error":
        sound_effects.play_error_buzz()
    elif stype == "record_start":
        sound_effects.play_record_start()
    elif stype == "record_finish":
        sound_effects.play_record_finish()
    return json.dumps({"success": True, "type": stype})



@app.route("/api/open-clips-folder", method="POST")
def open_clips_folder():
    response.content_type = "application/json"
    clips_dir = database.get_clips_dir()
    abs_path = os.path.abspath(clips_dir)
    try:
        os.makedirs(abs_path, exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer.exe", abs_path])
        else:
            os.startfile(abs_path)
        return json.dumps({"success": True, "path": abs_path})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "path": abs_path})


@app.route("/api/sessions/<session_id:int>/reveal", method="POST")
@app.route("/api/clips/<session_id:int>/reveal", method="POST")
def reveal_session_in_explorer(session_id: int):
    """Open Windows File Explorer and select the specific clip file."""
    response.content_type = "application/json"
    session = database.get_session_by_id(session_id)
    if not session:
        return json.dumps({"success": False, "error": "Session not found"})

    clips_dir = os.path.abspath(database.get_clips_dir())
    clip_path = session.get("clip_path")
    target_file = None

    if clip_path and os.path.exists(clip_path):
        target_file = os.path.abspath(clip_path)
    elif session.get("clip_filename"):
        candidate = os.path.join(clips_dir, session["clip_filename"])
        if os.path.exists(candidate):
            target_file = candidate
    elif session.get("barcode"):
        candidate = os.path.join(clips_dir, f"{session['barcode']}.mp4")
        if os.path.exists(candidate):
            target_file = candidate

    try:
        if target_file and os.path.exists(target_file):
            if sys.platform == "win32":
                subprocess.Popen(["explorer.exe", f"/select,{target_file}"])
            else:
                os.startfile(os.path.dirname(target_file))
            return json.dumps({"success": True, "revealed": True, "path": target_file})
        else:
            os.makedirs(clips_dir, exist_ok=True)
            if sys.platform == "win32":
                subprocess.Popen(["explorer.exe", clips_dir])
            else:
                os.startfile(clips_dir)
            return json.dumps({"success": True, "revealed": False, "path": clips_dir})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/clips/reveal", method="POST")
def reveal_clip_file():
    """Open Windows File Explorer and select the clip file by filename."""
    response.content_type = "application/json"
    try:
        data = request.json or {}
        filename = (data.get("filename") or "").strip()
        clips_dir = os.path.abspath(database.get_clips_dir())
        target = os.path.join(clips_dir, os.path.basename(filename)) if filename else clips_dir
        if sys.platform == "win32":
            if os.path.isfile(target):
                subprocess.Popen(["explorer.exe", f"/select,{target}"])
            else:
                subprocess.Popen(["explorer.exe", clips_dir])
        else:
            os.startfile(clips_dir)
        return json.dumps({"success": True, "path": target})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@app.route("/api/settings", method=["GET", "POST"])
def handle_settings():
    response.content_type = "application/json"
    if request.method == "POST":
        data = request.json or {}
        for k, v in data.items():
            database.set_setting(k, str(v))
        if "camera_source" in data:
            new_source = data["camera_source"]
            if new_source == "rtsp" and "rtsp_url" in data and data["rtsp_url"]:
                video_engine.engine.set_camera_source(data["rtsp_url"])
            else:
                video_engine.engine.set_camera_source(new_source)
        elif "rtsp_url" in data and data["rtsp_url"]:
            current_src = database.get_setting("camera_source", "")
            if current_src == "rtsp" or current_src.startswith("rtsp://"):
                video_engine.engine.set_camera_source(data["rtsp_url"])
        return json.dumps({"success": True, "settings": data})
    else:
        keys = ["idle_timeout_seconds", "pre_roll_seconds", "station_id", "camera_source", "rtsp_url", "clips_dir", "update_manifest_url", "auto_check_updates"]
        res = {k: database.get_setting(k) for k in keys}
        if not res.get("clips_dir"):
            res["clips_dir"] = database.get_clips_dir()
        if not res.get("update_manifest_url"):
            res["update_manifest_url"] = updater.DEFAULT_MANIFEST_URL
        if res.get("auto_check_updates") is None:
            res["auto_check_updates"] = "1"
        return json.dumps(res)


# ==========================================
# AUTO-UPDATER ENDPOINTS
# ==========================================

@app.route("/api/updates/status", method="GET")
def get_update_status():
    response.content_type = "application/json"
    return json.dumps(updater.manager.get_status_dict())


@app.route("/api/updates/check", method=["GET", "POST"])
def check_updates_endpoint():
    response.content_type = "application/json"
    data = request.json or {} if request.method == "POST" else {}
    manifest_url = data.get("manifest_url") or request.query.get("manifest_url") or None
    is_sync = request.query.get("sync") in ("1", "true", "yes")

    if is_sync:
        updater.manager._check_worker(manifest_url=manifest_url)
        return json.dumps(updater.manager.get_status_dict())
    else:
        updater.manager.check_for_updates_async(manifest_url=manifest_url)
        return json.dumps(updater.manager.get_status_dict())


@app.route("/api/updates/download", method="POST")
def download_updates_endpoint():
    response.content_type = "application/json"
    updater.manager.download_update_async()
    return json.dumps(updater.manager.get_status_dict())


@app.route("/api/updates/apply", method="POST")
def apply_update_endpoint():
    response.content_type = "application/json"
    data = request.json or {}
    silent = data.get("silent", True)
    can_apply, reason = updater.can_apply_update()
    if not can_apply:
        return json.dumps({"success": False, "error": reason})

    success, message = updater.apply_update(silent=silent)
    return json.dumps({"success": success, "message": message})


from socketserver import ThreadingMixIn
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler
import bottle


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True
    allow_reuse_address = (os.name != "nt")


class ThreadedServer(bottle.ServerAdapter):
    def run(self, handler):
        class QuietHandler(WSGIRequestHandler):
            def log_message(self, format, *args):
                pass

        server = make_server(self.host, self.port, handler, server_class=ThreadingWSGIServer, handler_class=QuietHandler)
        server.serve_forever()


def start_server(port: int = 5892, start_video: bool = True) -> None:
    if start_video:
        source = database.get_setting("camera_source", "webcam:0")
        video_engine.engine.set_camera_source(source)
        video_engine.engine.start()

    # Trigger background update check on startup if enabled
    try:
        auto_check = database.get_setting("auto_check_updates", "1")
        if auto_check != "0":
            feed_source = database.get_setting("update_manifest_url", updater.DEFAULT_MANIFEST_URL)
            updater.manager.check_for_updates_async(manifest_url=feed_source)
    except Exception as e:
        print(f"Startup update check note: {e}", flush=True)

    # Run multi-threaded bottle app
    app.run(server=ThreadedServer, host="127.0.0.1", port=port, quiet=True)



if __name__ == "__main__":
    start_server()

