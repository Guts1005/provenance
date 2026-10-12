"""
Provenance Daily Manifest Reconciliation Manager.
Handles CSV import of scheduled dispatch orders, tracking number matching,
real-time packed vs pending progress calculation, and warehouse fulfillment metrics.
Zero third-party dependencies, zero em-dashes.
"""

import csv
import io
from datetime import datetime
from typing import Dict, Any, List, Optional
import database


def _clean_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def parse_and_import_manifest_csv(csv_text: str, replace_existing: bool = False) -> Dict[str, Any]:
    """
    Parses a CSV string and inserts records into manifest_items.
    Supports flexible column names:
      - tracking: tracking_number, tracking_no, tracking, barcode, awb, waybill
      - order: order_id, order_no, order_number, order
      - recipient: recipient, customer, name, ship_to, consignee
      - sku: sku, item, product, skus, description
    """
    if not csv_text or not csv_text.strip():
        return {"success": False, "error": "CSV content is empty", "imported": 0}

    f = io.StringIO(csv_text.strip())
    reader = csv.reader(f)

    try:
        header_row = next(reader)
    except StopIteration:
        return {"success": False, "error": "No header row found in CSV", "imported": 0}

    # Normalize headers
    headers = [_clean_str(h).lower().replace(" ", "_").replace("-", "_") for h in header_row]

    def find_col_idx(candidates: List[str]) -> Optional[int]:
        for cand in candidates:
            for idx, h in enumerate(headers):
                if h == cand or cand in h:
                    return idx
        return None

    tracking_idx = find_col_idx(["tracking_number", "tracking_no", "barcode", "tracking", "awb", "waybill"])
    order_idx = find_col_idx(["order_id", "order_no", "order_number", "order"])
    recipient_idx = find_col_idx(["recipient", "customer", "customer_name", "ship_to", "name", "consignee"])
    sku_idx = find_col_idx(["sku", "item", "product", "skus", "items", "description"])

    if tracking_idx is None:
        return {
            "success": False,
            "error": "CSV must contain a Tracking Number or Barcode column (e.g. tracking_number, barcode, tracking).",
            "imported": 0
        }

    imported_count = 0
    skipped_count = 0

    with database.get_connection() as conn:
        if replace_existing:
            conn.execute("DELETE FROM manifest_items;")

        for row in reader:
            if not row or len(row) <= tracking_idx:
                continue
            tracking = _clean_str(row[tracking_idx])
            if not tracking:
                continue

            order_id = _clean_str(row[order_idx]) if order_idx is not None and len(row) > order_idx else ""
            recipient = _clean_str(row[recipient_idx]) if recipient_idx is not None and len(row) > recipient_idx else ""
            sku = _clean_str(row[sku_idx]) if sku_idx is not None and len(row) > sku_idx else ""

            try:
                conn.execute("""
                    INSERT INTO manifest_items (tracking_number, order_id, recipient, sku, status)
                    VALUES (?, ?, ?, ?, 'pending')
                    ON CONFLICT(tracking_number) DO UPDATE SET
                        order_id = excluded.order_id,
                        recipient = excluded.recipient,
                        sku = excluded.sku;
                """, (tracking, order_id, recipient, sku))
                imported_count += 1
            except Exception:
                skipped_count += 1

    return {
        "success": True,
        "imported": imported_count,
        "skipped": skipped_count,
        "progress": get_manifest_progress()
    }


def get_manifest_progress() -> Dict[str, Any]:
    """Returns total, packed, pending counts and completion percentage."""
    database.init_db()
    with database.get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM manifest_items;").fetchone()["c"]
        packed = conn.execute("SELECT COUNT(*) as c FROM manifest_items WHERE status = 'packed';").fetchone()["c"]
        pending = total - packed
        pct = round((packed / total) * 100.0, 1) if total > 0 else 0.0

        return {
            "total": total,
            "packed": packed,
            "pending": pending,
            "percentage": pct
        }


def check_and_mark_packed(tracking_number: str, clip_filename: str = "", session_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Checks if a tracking number exists in the manifest.
    If found, marks it as 'packed' with current timestamp and associates the clip.
    """
    tn = _clean_str(tracking_number)
    if not tn:
        return {"found": False, "already_packed": False, "item": None}

    now_iso = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with database.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM manifest_items WHERE tracking_number = ?;",
            (tn,)
        ).fetchone()

        if not row:
            # Also try matching case-insensitively or partial if needed
            row = conn.execute(
                "SELECT * FROM manifest_items WHERE LOWER(tracking_number) = LOWER(?);",
                (tn,)
            ).fetchone()

        if not row:
            return {"found": False, "already_packed": False, "item": None}

        already_packed = (row["status"] == "packed")

        conn.execute("""
            UPDATE manifest_items
            SET status = 'packed',
                packed_at = ?,
                clip_filename = COALESCE(NULLIF(?, ''), clip_filename),
                session_id = COALESCE(?, session_id)
            WHERE id = ?;
        """, (now_iso, clip_filename, session_id, row["id"]))

        updated = conn.execute("SELECT * FROM manifest_items WHERE id = ?;", (row["id"],)).fetchone()
        return {
            "found": True,
            "already_packed": already_packed,
            "item": dict(updated)
        }


def get_manifest_items(status: Optional[str] = None, limit: int = 200) -> List[Dict[str, Any]]:
    """Retrieves manifest items with optional status filtering ('pending' or 'packed')."""
    with database.get_connection() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM manifest_items WHERE status = ? ORDER BY id DESC LIMIT ?;",
                (status, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM manifest_items ORDER BY id DESC LIMIT ?;",
                (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


def clear_manifest() -> Dict[str, Any]:
    """Clears all manifest records."""
    with database.get_connection() as conn:
        conn.execute("DELETE FROM manifest_items;")
    return {"success": True, "progress": get_manifest_progress()}
