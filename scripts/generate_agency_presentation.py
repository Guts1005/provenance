"""
Provenance Industrial CCTV Proof & Packing Station
B2B Client Presentation Generator (.pptx)
Aesthetic Direction: Dark Industrial HUD & Terminal Precision
Synthesizes: Claude's Dark HUD aesthetic + Comprehensive Enterprise Technical Content.

PALETTE TOKENS:
- Canvas: #0F1117 (Deep Industrial Charcoal / Obsidian)
- Card Surfaces: #181B22 / #1A1D26 (Dark Graphite Slate)
- Table Well / Sub-surface: #12141B
- Border Hairlines: #262B35 / #2E3442 (1px uniform dark graphite)
- Primary Text: #FFFFFF (Crisp White)
- Secondary Text: #9CA3AF (Light Slate)
- Muted Metadata: #6B7280 (Cool Slate)
- Signal Mint: #10B981 (Camera Viewfinder Corners, Verified Proof)
- Signal Red: #EF4444 (REC dot, Loss Indicator)
- Signal Blue: #3B82F6 (Technical Schematics, Active Tracker)

RULES:
- Zero colored border stripes (Catalog K4). All borders uniform 1px #262B35.
- Zero floating candy pill badges (Catalog K5).
- Strictly ZERO em-dashes across all code, slides, speaker notes, and comments.
- 100% native editable PowerPoint shapes, text boxes, and tables.
- Content-tailored transitions preserved.
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

# --- ASSET PATHS ---
BRAIN_DIR = r"C:\Users\sharv\.gemini\antigravity\brain\f5a0e924-79bb-495f-9aab-a17922b8c28c"
IMG_STATION = os.path.join(BRAIN_DIR, "realtime_station_updated.png")
IMG_PLACARD = r"C:\Users\sharv\barcode-test\ui\finish_bench_placard.png"
IMG_LOGO = r"C:\Users\sharv\barcode-test\ui\provenance_logo.png"

# --- DESIGN TOKENS (DARK INDUSTRIAL HUD PALETTE) ---
COLOR_BG = RGBColor(15, 17, 23)               # #0F1117 (Deep Obsidian Canvas)
COLOR_CARD = RGBColor(24, 27, 34)             # #181B22 (Card Surface)
COLOR_CARD_SUBTLE = RGBColor(18, 20, 27)      # #12141B (Recessed Well)
COLOR_BORDER = RGBColor(38, 43, 53)           # #262B35 (1px Uniform Dark Hairline)
COLOR_BORDER_STRONG = RGBColor(55, 65, 81)    # #374151 (Accent Line)

# Typography Tokens
COLOR_TEXT_WHITE = RGBColor(255, 255, 255)    # #FFFFFF (High Contrast Header)
COLOR_TEXT_SLATE = RGBColor(156, 163, 175)    # #9CA3AF (Readable Body Text)
COLOR_TEXT_MUTED = RGBColor(107, 114, 128)    # #6B7280 (Monospace Metadata)

# Industrial HUD Signal Accents (Text & Indicators only, NEVER border stripes)
COLOR_MINT = RGBColor(16, 185, 129)           # #10B981 (HUD Reticles, Verified Proof)
COLOR_RED = RGBColor(239, 68, 68)             # #EF4444 (Live REC Dot, Loss Stat)
COLOR_BLUE = RGBColor(59, 130, 246)           # #3B82F6 (Technical Schematic Blue)

FONT_PRIMARY = "Segoe UI"
FONT_MONO = "Consolas"

PHASE_NAMES = ["01 PROBLEM", "02 SOLUTION", "03 OPERATIONS", "04 DEPLOYMENT"]


def set_bg(slide):
    """Fill slide with deep obsidian industrial canvas."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG
    bg.line.fill.background()
    return bg


def add_dark_card(slide, left, top, width, height, bg_color=COLOR_CARD, border_color=COLOR_BORDER):
    """Add a dark graphite card with a crisp 1px neutral dark border."""
    card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card


def add_hud_header(slide, subtitle_label, title_text, active_phase_idx=0):
    """
    Claude HUD Style Header:
    Left: Brand + Kicker Subtitle
    Center/Right: 4-Phase Horizontal Flow Tracker
    Divider: Dark graphite hairline
    """
    # Top Left: Brand Identification + Eyebrow Subtitle
    tb_b = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(4.5), Inches(0.28))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = False
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    pb = tf_b.paragraphs[0]
    pb.text = "PROVENANCE   •   " + subtitle_label.upper()
    pb.font.name = FONT_MONO
    pb.font.size = Pt(9.5)
    pb.font.bold = True
    pb.font.color.rgb = COLOR_TEXT_MUTED

    # Top Right: 4-Phase Flow Tracker Block
    flow_start_x = Inches(5.8)
    flow_w = Inches(1.6)
    flow_h = Inches(0.26)
    flow_gap = Inches(0.08)

    for i, phase_name in enumerate(PHASE_NAMES):
        px = flow_start_x + i * (flow_w + flow_gap)
        is_active = (i == active_phase_idx)
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, Inches(0.38), flow_w, flow_h)
        card.fill.solid()
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)
        if is_active:
            card.fill.fore_color.rgb = RGBColor(30, 41, 59)
        else:
            card.fill.fore_color.rgb = COLOR_CARD_SUBTLE

        tf_p = card.text_frame
        tf_p.word_wrap = False
        tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0
        pp = tf_p.paragraphs[0]
        pp.text = phase_name
        pp.font.name = FONT_MONO
        pp.font.size = Pt(8)
        pp.font.bold = is_active
        pp.font.color.rgb = COLOR_BLUE if is_active else COLOR_TEXT_MUTED
        pp.alignment = PP_ALIGN.CENTER

    # Slide Title
    tb_t = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.733), Inches(0.6))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_PRIMARY
    p_t.font.size = Pt(26)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TEXT_WHITE

    # Divider Line
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.733), Pt(1))
    div.fill.solid()
    div.fill.fore_color.rgb = COLOR_BORDER
    div.line.fill.background()


def add_hud_footer(slide, slide_num_str):
    """Clean technical status footer."""
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "PROVENANCE STATION SUITE"
    p.font.name = FONT_MONO
    p.font.size = Pt(9)
    p.font.color.rgb = COLOR_TEXT_MUTED

    # Right aligned slide number
    tb_r = slide.shapes.add_textbox(Inches(11.0), Inches(7.05), Inches(1.533), Inches(0.3))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = False
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0
    pr = tf_r.paragraphs[0]
    clean_num = slide_num_str.replace(" / ", " of ").replace("/", " of ")
    pr.text = clean_num
    pr.font.name = FONT_MONO
    pr.font.size = Pt(9)
    pr.font.color.rgb = COLOR_TEXT_MUTED
    pr.alignment = PP_ALIGN.RIGHT


def set_speaker_notes(slide, notes_text):
    """Attach executive talking points to the slide's notes slide."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


def build_presentation(output_path):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 01: HERO OPENING & PACKING STATION CAMERA HUD
    # High-Contrast Dark Canvas + Provenance Logo + 1080p Adaptive Camera HUD
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    # Top Brand / Status with Logo
    if os.path.exists(IMG_LOGO):
        s1.shapes.add_picture(IMG_LOGO, Inches(0.8), Inches(0.52), width=Inches(0.44), height=Inches(0.44))

    tb_brand = s1.shapes.add_textbox(Inches(1.36), Inches(0.55), Inches(6.0), Inches(0.38))
    tf_brand = tb_brand.text_frame
    tf_brand.word_wrap = False
    tf_brand.margin_left = tf_brand.margin_top = tf_brand.margin_right = tf_brand.margin_bottom = 0
    p_brand = tf_brand.paragraphs[0]
    
    r_name = p_brand.add_run()
    r_name.text = "PROVENANCE"
    r_name.font.name = FONT_PRIMARY
    r_name.font.size = Pt(13)
    r_name.font.bold = True
    r_name.font.color.rgb = COLOR_TEXT_WHITE
    
    r_sep = p_brand.add_run()
    r_sep.text = "   •   "
    r_sep.font.name = FONT_MONO
    r_sep.font.size = Pt(10)
    r_sep.font.color.rgb = COLOR_TEXT_MUTED
    
    r_tag = p_brand.add_run()
    r_tag.text = "AUTOMATED PACKING SURVEILLANCE"
    r_tag.font.name = FONT_MONO
    r_tag.font.size = Pt(9.5)
    r_tag.font.bold = True
    r_tag.font.color.rgb = COLOR_MINT

    # Big Statement Headline (Option A)
    tb_h = s1.shapes.add_textbox(Inches(0.8), Inches(1.18), Inches(6.8), Inches(2.3))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True
    tf_h.margin_left = tf_h.margin_top = tf_h.margin_right = tf_h.margin_bottom = 0
    ph1 = tf_h.paragraphs[0]
    ph1.text = "Automated CCTV Evidence &\nPacking Station Verification"
    ph1.font.name = FONT_PRIMARY
    ph1.font.size = Pt(32)
    ph1.font.bold = True
    ph1.font.color.rgb = COLOR_TEXT_WHITE

    ph2 = tf_h.add_paragraph()
    ph2.text = "Instant camera proof for every parcel leaving your facility. Records automatically from your existing barcode scan with zero worker delay."
    ph2.font.name = FONT_PRIMARY
    ph2.font.size = Pt(13)
    ph2.font.color.rgb = COLOR_TEXT_SLATE
    ph2.space_before = Pt(12)

    # Left Bottom: 3 Large Stat Metrics (Client Value Oriented)
    stat_y = Inches(3.9)
    stat_w = Inches(2.05)
    stat_h = Inches(2.55)
    stat_gap = Inches(0.25)

    stats = [
        ("1080p FHD", "ADAPTIVE VISION", "Overhead camera optimized for changing warehouse lighting and glare from packing tape.", COLOR_MINT),
        ("0 Clicks", "ZERO WORKER FRICTION", "Triggers automatically on barcode scan. Packers never touch a keyboard or mouse.", COLOR_BLUE),
        ("< 2s", "INSTANT EVIDENCE", "Search by tracking number to pull packing video proof and resolve claims immediately.", COLOR_MINT)
    ]

    for i, (val, tag, desc, tag_color) in enumerate(stats):
        sx = Inches(0.8) + i * (stat_w + stat_gap)
        add_dark_card(s1, sx, stat_y, stat_w, stat_h)

        tb_s = s1.shapes.add_textbox(sx + Inches(0.18), stat_y + Inches(0.18), stat_w - Inches(0.36), stat_h - Inches(0.36))
        tf_s = tb_s.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0

        p1 = tf_s.paragraphs[0]
        p1.text = val
        p1.font.name = FONT_MONO
        p1.font.size = Pt(26)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_WHITE

        p2 = tf_s.add_paragraph()
        p2.text = tag
        p2.font.name = FONT_MONO
        p2.font.size = Pt(9)
        p2.font.bold = True
        p2.font.color.rgb = tag_color
        p2.space_before = Pt(5)

        p3 = tf_s.add_paragraph()
        p3.text = desc
        p3.font.name = FONT_PRIMARY
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = COLOR_TEXT_SLATE
        p3.space_before = Pt(12)

    # Right: Camera Viewfinder HUD Panel
    hud_x = Inches(7.8)
    hud_y = Inches(1.0)
    hud_w = Inches(4.733)
    hud_h = Inches(5.45)
    add_dark_card(s1, hud_x, hud_y, hud_w, hud_h, bg_color=COLOR_CARD_SUBTLE)

    # Live REC Indicator & Header
    rec_dot = s1.shapes.add_shape(MSO_SHAPE.OVAL, hud_x + Inches(0.25), hud_y + Inches(0.24), Inches(0.11), Inches(0.11))
    rec_dot.fill.solid(); rec_dot.fill.fore_color.rgb = COLOR_RED; rec_dot.line.fill.background()

    tb_rec = s1.shapes.add_textbox(hud_x + Inches(0.45), hud_y + Inches(0.18), Inches(2.2), Inches(0.25))
    tf_rec = tb_rec.text_frame
    tf_rec.word_wrap = False
    tf_rec.margin_left = tf_rec.margin_top = tf_rec.margin_right = tf_rec.margin_bottom = 0
    p_rec = tf_rec.paragraphs[0]
    p_rec.text = "REC   STATION FEED"
    p_rec.font.name = FONT_MONO
    p_rec.font.size = Pt(10)
    p_rec.font.bold = True
    p_rec.font.color.rgb = COLOR_RED

    tb_feed_status = s1.shapes.add_textbox(hud_x + Inches(2.7), hud_y + Inches(0.18), Inches(1.8), Inches(0.25))
    tf_feed_status = tb_feed_status.text_frame
    tf_feed_status.word_wrap = False
    tf_feed_status.margin_left = tf_feed_status.margin_top = tf_feed_status.margin_right = tf_feed_status.margin_bottom = 0
    p_fs = tf_feed_status.paragraphs[0]
    p_fs.text = "LIVE OVERHEAD VIEW"
    p_fs.font.name = FONT_MONO
    p_fs.font.size = Pt(9)
    p_fs.font.color.rgb = COLOR_TEXT_MUTED
    p_fs.alignment = PP_ALIGN.RIGHT

    # Viewfinder Box with Mint Corner Reticles
    ret_y = hud_y + Inches(0.58)
    ret_w = hud_w - Inches(0.5)
    ret_h = Inches(2.5)
    add_dark_card(s1, hud_x + Inches(0.25), ret_y, ret_w, ret_h, bg_color=RGBColor(12, 14, 19), border_color=COLOR_BORDER)

    # Mint Reticle Corners
    for rx, ry, dx, dy in [
        (hud_x + Inches(0.35), ret_y + Inches(0.1), Inches(0.32), Pt(2)),
        (hud_x + Inches(0.35), ret_y + Inches(0.1), Pt(2), Inches(0.32)),
        (hud_x + Inches(0.25) + ret_w - Inches(0.42), ret_y + Inches(0.1), Inches(0.32), Pt(2)),
        (hud_x + Inches(0.25) + ret_w - Inches(0.1), ret_y + Inches(0.1), Pt(2), Inches(0.32)),
        (hud_x + Inches(0.35), ret_y + ret_h - Inches(0.1), Inches(0.32), Pt(2)),
        (hud_x + Inches(0.35), ret_y + ret_h - Inches(0.42), Pt(2), Inches(0.32)),
        (hud_x + Inches(0.25) + ret_w - Inches(0.42), ret_y + ret_h - Inches(0.1), Inches(0.32), Pt(2)),
        (hud_x + Inches(0.25) + ret_w - Inches(0.1), ret_y + ret_h - Inches(0.42), Pt(2), Inches(0.32)),
    ]:
        s_r = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, rx, ry, dx, dy)
        s_r.fill.solid(); s_r.fill.fore_color.rgb = COLOR_MINT; s_r.line.fill.background()

    # Bench and Parcel Schematic in Viewfinder
    add_dark_card(s1, hud_x + Inches(0.6), ret_y + Inches(0.75), ret_w - Inches(0.7), Inches(1.3), bg_color=RGBColor(20, 24, 33), border_color=COLOR_BORDER)
    add_dark_card(s1, hud_x + Inches(1.6), ret_y + Inches(0.45), Inches(1.8), Inches(1.15), bg_color=RGBColor(26, 31, 44), border_color=RGBColor(59, 130, 246))

    # Subtle Station Tag inside Reticle
    tb_ret_lbl = s1.shapes.add_textbox(hud_x + Inches(0.45), ret_y + Inches(0.18), Inches(2.5), Inches(0.22))
    tf_ret_lbl = tb_ret_lbl.text_frame
    tf_ret_lbl.word_wrap = False
    tf_ret_lbl.margin_left = tf_ret_lbl.margin_top = tf_ret_lbl.margin_right = tf_ret_lbl.margin_bottom = 0
    p_rl = tf_ret_lbl.paragraphs[0]
    p_rl.text = "BENCH 01 ACTIVE"
    p_rl.font.name = FONT_MONO
    p_rl.font.size = Pt(8.5)
    p_rl.font.bold = True
    p_rl.font.color.rgb = COLOR_MINT

    # Camera & Station Technical Specifications below Viewfinder
    tb_hspec = s1.shapes.add_textbox(hud_x + Inches(0.25), ret_y + ret_h + Inches(0.2), ret_w, Inches(1.9))
    tf_hspec = tb_hspec.text_frame
    tf_hspec.word_wrap = True
    tf_hspec.margin_left = tf_hspec.margin_top = tf_hspec.margin_right = tf_hspec.margin_bottom = 0

    hspecs = [
        ("Camera Sensor", "1080p Full HD Industrial"),
        ("Lighting Control", "Dynamic anti-glare optimization"),
        ("Pre-Roll Buffer", "5-second continuous buffer"),
        ("Capture Trigger", "Standard barcode scan"),
        ("Data Storage", "Secure local station database")
    ]

    for i, (lbl, val) in enumerate(hspecs):
        p_row = tf_hspec.add_paragraph() if i > 0 else tf_hspec.paragraphs[0]
        p_row.text = f"{lbl.ljust(18)}: {val}"
        p_row.font.name = FONT_MONO
        p_row.font.size = Pt(9.5)
        p_row.font.color.rgb = COLOR_TEXT_SLATE
        if i > 0:
            p_row.space_before = Pt(4)

    add_hud_footer(s1, "01 of 10")
    set_speaker_notes(s1, "Presenter Goal: Introduce Provenance with clarity. Provenance turns ordinary warehouse packing tables into automatic video verification stations. By tapping into existing barcode scans, overhead 1080p cameras capture tamper-proof packing proof without asking packers to touch a keyboard or mouse. Adaptive vision balances harsh lighting and tape glare so every item is visibly clear.")

    # =========================================================================
    # SLIDE 02: THE SURVEILLANCE GAP (WHY CEILING CCTV FAILS PACKING LINES)
    # High-Contrast Dark Canvas + Top Failure Metrics (Rs) + 4 Failure Modes
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_hud_header(s2, "Surveillance Gap", "Why Traditional Warehouse CCTV Fails to Protect Packaging Lines", active_phase_idx=0)

    # Subtitle Text
    tb_sub2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.58), Inches(11.733), Inches(0.35))
    tf_sub2 = tb_sub2.text_frame
    tf_sub2.word_wrap = True
    tf_sub2.margin_left = tf_sub2.margin_top = tf_sub2.margin_right = tf_sub2.margin_bottom = 0
    p_s2 = tf_sub2.paragraphs[0]
    p_s2.text = "Ceiling security cameras monitor facility safety, not individual orders. When customer or courier claims arise, finding conclusive proof is nearly impossible."
    p_s2.font.name = FONT_PRIMARY
    p_s2.font.size = Pt(13)
    p_s2.font.color.rgb = COLOR_TEXT_SLATE

    # Top 2 Big Numbers (Option B, Indian Currency Rs)
    top_stat_y = Inches(2.05)
    top_w = Inches(5.7)
    top_h = Inches(1.1)

    # Card 1: 28 Mins Manual Scrub Time
    add_dark_card(s2, Inches(0.8), top_stat_y, top_w, top_h)
    tb_ts1 = s2.shapes.add_textbox(Inches(1.05), top_stat_y + Inches(0.18), top_w - Inches(0.5), top_h - Inches(0.36))
    tf_ts1 = tb_ts1.text_frame
    tf_ts1.word_wrap = True
    tf_ts1.margin_left = tf_ts1.margin_top = tf_ts1.margin_right = tf_ts1.margin_bottom = 0
    pt1 = tf_ts1.paragraphs[0]
    pt1.text = "28 Mins"
    pt1.font.name = FONT_MONO
    pt1.font.size = Pt(26)
    pt1.font.bold = True
    pt1.font.color.rgb = COLOR_RED
    pt1_sub = tf_ts1.add_paragraph()
    pt1_sub.text = "AVERAGE TIME TO SEARCH ONE DISPUTED ORDER"
    pt1_sub.font.name = FONT_MONO
    pt1_sub.font.size = Pt(9.5)
    pt1_sub.font.bold = True
    pt1_sub.font.color.rgb = COLOR_TEXT_MUTED
    pt1_sub.space_before = Pt(4)

    # Card 2: Rs 3,500 to Rs 15,000 Average Loss
    add_dark_card(s2, Inches(6.833), top_stat_y, top_w, top_h)
    tb_ts2 = s2.shapes.add_textbox(Inches(7.083), top_stat_y + Inches(0.18), top_w - Inches(0.5), top_h - Inches(0.36))
    tf_ts2 = tb_ts2.text_frame
    tf_ts2.word_wrap = True
    tf_ts2.margin_left = tf_ts2.margin_top = tf_ts2.margin_right = tf_ts2.margin_bottom = 0
    pt2 = tf_ts2.paragraphs[0]
    pt2.text = "Rs 3,500 to Rs 15,000"
    pt2.font.name = FONT_MONO
    pt2.font.size = Pt(24)
    pt2.font.bold = True
    pt2.font.color.rgb = COLOR_RED
    pt2_sub = tf_ts2.add_paragraph()
    pt2_sub.text = "AVERAGE LOSS PER CONTESTED SHIPMENT"
    pt2_sub.font.name = FONT_MONO
    pt2_sub.font.size = Pt(9.5)
    pt2_sub.font.bold = True
    pt2_sub.font.color.rgb = COLOR_TEXT_MUTED
    pt2_sub.space_before = Pt(4)

    # 4 Failure Mode Breakdown Cards (Option B)
    stage_y = Inches(3.35)
    stage_w = Inches(2.75)
    stage_h = Inches(3.5)
    stage_gap = Inches(0.24)

    failures = [
        ("FAILURE 01", "OBSTRUCTED VIEW", "Angle & Blind Spots",
         "Ceiling cameras mount 20 feet above and film workers from behind. The packer's shoulders block the box contents at tape down.",
         "Zero visual proof of items inside the box."),
        ("FAILURE 02", "UNINDEXED FOOTAGE", "No Barcode Linking",
         "Footage is organized only by time of day, not tracking number. Finding one parcel among thousands of daily dispatches is pure guesswork.",
         "Manual scrubbing wastes hours of manager time."),
        ("FAILURE 03", "LIGHTING & REFLECTION", "Tape Glare & Blur",
         "Warehouse tube lights reflect off clear packing tape. Standard security lenses blow out details and blur shipping label text.",
         "Label barcodes and serial numbers are unreadable."),
        ("FAILURE 04", "CLAIM FORFEIT", "Dispute Rejection",
         "Carriers and marketplaces reject blurry wide-angle ceiling clips. Without bench-level proof, merchants are forced to pay out the claim.",
         "100% of contested order value is written off.")
    ]

    for i, (f_num, f_tag, f_title, f_body, f_risk) in enumerate(failures):
        sx = Inches(0.8) + i * (stage_w + stage_gap)
        add_dark_card(s2, sx, stage_y, stage_w, stage_h)

        tb_sc = s2.shapes.add_textbox(sx + Inches(0.2), stage_y + Inches(0.2), stage_w - Inches(0.4), stage_h - Inches(0.4))
        tf_sc = tb_sc.text_frame
        tf_sc.word_wrap = True
        tf_sc.margin_left = tf_sc.margin_top = tf_sc.margin_right = tf_sc.margin_bottom = 0

        p1 = tf_sc.paragraphs[0]
        p1.text = f_num
        p1.font.name = FONT_MONO
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_WHITE

        p1b = tf_sc.add_paragraph()
        p1b.text = f_tag
        p1b.font.name = FONT_MONO
        p1b.font.size = Pt(9)
        p1b.font.bold = True
        p1b.font.color.rgb = COLOR_TEXT_MUTED
        p1b.space_before = Pt(3)

        p2 = tf_sc.add_paragraph()
        p2.text = f_title
        p2.font.name = FONT_PRIMARY
        p2.font.size = Pt(16)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_WHITE
        p2.space_before = Pt(8)

        p3 = tf_sc.add_paragraph()
        p3.text = f_body
        p3.font.name = FONT_PRIMARY
        p3.font.size = Pt(11.5)
        p3.font.color.rgb = COLOR_TEXT_SLATE
        p3.space_before = Pt(8)

        p4 = tf_sc.add_paragraph()
        p4.text = f_risk
        p4.font.name = FONT_PRIMARY
        p4.font.size = Pt(10.5)
        p4.font.color.rgb = COLOR_RED
        p4.space_before = Pt(12)

    add_hud_footer(s2, "02 of 10")
    set_speaker_notes(s2, "Presenter Goal: Disarm the common objection: We already have security cameras. Explain the surveillance gap: 20-foot ceiling cameras are designed for building security, not order verification. They film packers from behind, footage is not indexed by barcode, and tape glare blinds the sensor. When a claim comes in, teams waste 28 minutes searching footage only to have the claim rejected. Merchants in India lose between Rs 3,500 and Rs 15,000 per disputed order.")

    # =========================================================================
    # SLIDE 03: BEFORE VS AFTER TRANSFORMATION
    # Claude Aesthetics: Clean Dark Table + Giant 18% -> 82% Graphic Arrow
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_hud_header(s3, "Transformation Analysis", "Operational Shift: Blind Bench vs Cryptographic Proof", active_phase_idx=0)

    # Subtitle
    tb_sub3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.35))
    tf_sub3 = tb_sub3.text_frame
    tf_sub3.word_wrap = True
    tf_sub3.margin_left = tf_sub3.margin_top = tf_sub3.margin_right = tf_sub3.margin_bottom = 0
    p_s3 = tf_sub3.paragraphs[0]
    p_s3.text = "Comparison of legacy manual CCTV workflows against automated Provenance edge recording."
    p_s3.font.name = FONT_PRIMARY
    p_s3.font.size = Pt(13)
    p_s3.font.color.rgb = COLOR_TEXT_SLATE

    # Structured Comparison Table Card
    tbl_y = Inches(2.05)
    tbl_w = Inches(11.733)
    tbl_h = Inches(3.2)
    add_dark_card(s3, Inches(0.8), tbl_y, tbl_w, tbl_h)

    # Native Table shape
    matrix_rows = [
        ("Search Time", "28 min manual CCTV scrub across channels", "Sub-2s instant query by barcode number"),
        ("Clock Drift", "NTP drift between PC and overhead camera", "Hardware timestamp lock at video trigger"),
        ("Pre-Scan Footage", "Zero pre-roll buffer (item placement lost)", "5-second circular RAM pre-roll buffer"),
        ("Evidence Integrity", "Subjective word against word", "SHA-256 cryptographic hash signature"),
        ("Dispute Win Rate", "18% dispute recovery rate (82% lost)", "82% verified dispute win rate")
    ]

    t_shape = s3.shapes.add_table(len(matrix_rows) + 1, 3, Inches(1.0), tbl_y + Inches(0.15), tbl_w - Inches(0.4), tbl_h - Inches(0.3))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(2.6)
    tbl.columns[1].width = Inches(4.35)
    tbl.columns[2].width = Inches(4.383)

    # Header Row
    headers = ["METRIC", "BEFORE: BLIND DISPATCHES", "AFTER: CRYPTOGRAPHIC PROOF"]
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD
        cell.margin_left = Inches(0.12)
        cell.margin_right = Inches(0.12)
        cell.margin_top = Inches(0.08)
        cell.margin_bottom = Inches(0.08)
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_MONO
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_MUTED

    # Data Rows
    for r_idx, (m_lbl, m_bef, m_aft) in enumerate(matrix_rows):
        row_cells = [m_lbl, m_bef, m_aft]
        for c_idx, val in enumerate(row_cells):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD_SUBTLE if r_idx % 2 == 1 else COLOR_CARD
            cell.margin_left = Inches(0.12)
            cell.margin_right = Inches(0.12)
            cell.margin_top = Inches(0.08)
            cell.margin_bottom = Inches(0.08)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_PRIMARY
            p.font.size = Pt(11)
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_TEXT_WHITE
            elif c_idx == 1:
                p.font.color.rgb = COLOR_TEXT_SLATE
            else:
                p.font.color.rgb = COLOR_MINT if r_idx == 4 else COLOR_TEXT_WHITE

    # Dispute Win Rate Banner Card
    win_y = Inches(5.45)
    win_h = Inches(1.4)
    add_dark_card(s3, Inches(0.8), win_y, tbl_w, win_h, bg_color=COLOR_CARD_SUBTLE)

    # Left: 18% (Loss)
    tb_w1 = s3.shapes.add_textbox(Inches(1.2), win_y + Inches(0.25), Inches(1.8), Inches(0.9))
    tf_w1 = tb_w1.text_frame
    tf_w1.margin_left = tf_w1.margin_top = tf_w1.margin_right = tf_w1.margin_bottom = 0
    p1 = tf_w1.paragraphs[0]
    p1.text = "18%"
    p1.font.name = FONT_MONO
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_RED
    p1_sub = tf_w1.add_paragraph()
    p1_sub.text = "UNVERIFIED"
    p1_sub.font.name = FONT_MONO
    p1_sub.font.size = Pt(9)
    p1_sub.font.color.rgb = COLOR_TEXT_MUTED

    # Center: Arrow Text
    tb_arr = s3.shapes.add_textbox(Inches(3.2), win_y + Inches(0.35), Inches(1.5), Inches(0.6))
    tf_arr = tb_arr.text_frame
    tf_arr.margin_left = tf_arr.margin_top = tf_arr.margin_right = tf_arr.margin_bottom = 0
    pa = tf_arr.paragraphs[0]
    pa.text = "----->"
    pa.font.name = FONT_MONO
    pa.font.size = Pt(28)
    pa.font.bold = True
    pa.font.color.rgb = COLOR_BORDER_STRONG

    # Middle-Right: 82% (Verified)
    tb_w2 = s3.shapes.add_textbox(Inches(4.9), win_y + Inches(0.25), Inches(2.2), Inches(0.9))
    tf_w2 = tb_w2.text_frame
    tf_w2.margin_left = tf_w2.margin_top = tf_w2.margin_right = tf_w2.margin_bottom = 0
    p2 = tf_w2.paragraphs[0]
    p2.text = "82%"
    p2.font.name = FONT_MONO
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_MINT
    p2_sub = tf_w2.add_paragraph()
    p2_sub.text = "WITH PROVENANCE"
    p2_sub.font.name = FONT_MONO
    p2_sub.font.size = Pt(9)
    p2_sub.font.bold = True
    p2_sub.font.color.rgb = COLOR_MINT

    # Far-Right: Description block
    tb_w3 = s3.shapes.add_textbox(Inches(6.8), win_y + Inches(0.24), Inches(5.4), Inches(0.95))
    tf_w3 = tb_w3.text_frame
    tf_w3.word_wrap = True
    tf_w3.margin_left = tf_w3.margin_top = tf_w3.margin_right = tf_w3.margin_bottom = 0
    p3 = tf_w3.paragraphs[0]
    p3.text = "DISPUTE WIN RATE TRANSFORMATION"
    p3.font.name = FONT_MONO
    p3.font.size = Pt(11)
    p3.font.bold = True
    p3.font.color.rgb = COLOR_TEXT_WHITE
    p3_sub = tf_w3.add_paragraph()
    p3_sub.text = "Cryptographic proof delivered in under 90 seconds reverses false shortage claims with immediate carrier sign-off."
    p3_sub.font.name = FONT_PRIMARY
    p3_sub.font.size = Pt(11)
    p3_sub.font.color.rgb = COLOR_TEXT_SLATE
    p3_sub.space_before = Pt(3)

    add_hud_footer(s3, "03 / 10")
    set_speaker_notes(s3, "PRESENTER GOAL (30s): Highlight the contrast. Show how Provenance eliminates 28 minutes of manual NVR scrubbing and shifts dispute recovery from 18% to 82% with cryptographic proof.")

    # =========================================================================
    # SLIDE 04: THE PROVENANCE PLATFORM ARCHITECTURE
    # Claude Aesthetics: 3 Dark Subsystem Cards with Giant Monospace Metrics
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_hud_header(s4, "System Engineering", "The Solution: Automated Bench Chain-of-Custody", active_phase_idx=1)

    # Subtitle
    tb_sub4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.35))
    tf_sub4 = tb_sub4.text_frame
    tf_sub4.word_wrap = True
    tf_sub4.margin_left = tf_sub4.margin_top = tf_sub4.margin_right = tf_sub4.margin_bottom = 0
    p_s4 = tf_sub4.paragraphs[0]
    p_s4.text = "Autonomous edge recording daemon engineered specifically for warehouse packing bench ergonomics."
    p_s4.font.name = FONT_PRIMARY
    p_s4.font.size = Pt(13)
    p_s4.font.color.rgb = COLOR_TEXT_SLATE

    # 3 Subsystem Cards
    pil_w = Inches(3.75)
    pil_h = Inches(4.8)
    pil_gap = Inches(0.24)
    pil_y = Inches(2.05)

    subsystems = [
        ("SUBSYSTEM 01", "Sub-50ms Keystroke Trigger",
         "Background USB parser listens for the rapid barcode scanner keystroke burst. Zero mouse clicks, zero keyboard typing required.",
         [
             "Hardware-level keystroke parser (< 50ms latency)",
             "Runs entirely in background without window focus",
             "Compatible with all 2D USB & Bluetooth scanners",
             "Zero disruption to high-speed packing flow"
         ],
         "< 50ms", "TRIGGER LATENCY"),
        ("SUBSYSTEM 02", "5-Second Rolling Pre-Roll Buffer",
         "Circular uncompressed RAM ring holds the last 5 seconds, so 100% of pre-scan box placement is captured automatically.",
         [
             "Captures item pickup before barcode scan occurs",
             "Seamlessly prepends buffer frames to cut",
             "High-throughput OpenCV RTSP memory engine",
             "Zero storage write wear during standby ring"
         ],
         "5 SEC", "ROLLING PRE-ROLL"),
        ("SUBSYSTEM 03", "SHA-256 Tamper-Proof Stamp",
         "Cryptographic signature tied to hardware ID, NTP timestamp, and barcode metadata. Stored in a local SQLite database.",
         [
             "SHA-256 signature calculated at recording finish",
             "Station ID and millisecond timestamp stamped",
             "Local SQLite database ensures instant sub-2s query",
             "Admissible in formal carrier and legal disputes"
         ],
         "SHA-256", "TAMPER-PROOF STAMP")
    ]

    for i, (tag, title, lead, bullets, metric_num, metric_lbl) in enumerate(subsystems):
        px = Inches(0.8) + i * (pil_w + pil_gap)
        add_dark_card(s4, px, pil_y, pil_w, pil_h)

        tb_p = s4.shapes.add_textbox(px + Inches(0.25), pil_y + Inches(0.25), pil_w - Inches(0.5), pil_h - Inches(0.5))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0

        p1 = tf_p.paragraphs[0]
        p1.text = tag
        p1.font.name = FONT_MONO
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_MUTED

        p2 = tf_p.add_paragraph()
        p2.text = title
        p2.font.name = FONT_PRIMARY
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_WHITE
        p2.space_before = Pt(6)

        p3 = tf_p.add_paragraph()
        p3.text = lead
        p3.font.name = FONT_PRIMARY
        p3.font.size = Pt(11.5)
        p3.font.color.rgb = COLOR_TEXT_SLATE
        p3.space_before = Pt(8)

        for b in bullets:
            pb = tf_p.add_paragraph()
            pb.text = f"›  {b}"
            pb.font.name = FONT_PRIMARY
            pb.font.size = Pt(10.5)
            pb.font.color.rgb = COLOR_TEXT_SLATE
            pb.space_before = Pt(6)

        # Big Monospace Metric at Card Bottom
        pm = tf_p.add_paragraph()
        pm.text = metric_num
        pm.font.name = FONT_MONO
        pm.font.size = Pt(24)
        pm.font.bold = True
        pm.font.color.rgb = COLOR_MINT
        pm.space_before = Pt(18)

        pml = tf_p.add_paragraph()
        pml.text = metric_lbl
        pml.font.name = FONT_MONO
        pml.font.size = Pt(9)
        pml.font.color.rgb = COLOR_TEXT_MUTED
        pml.space_before = Pt(2)

    add_hud_footer(s4, "04 / 10")
    set_speaker_notes(s4, "PRESENTER GOAL (30-45s): Present the 3 pillars. Emphasize that packers never touch a keyboard or mouse. The rolling 5s circular buffer guarantees pre-scan packaging is captured.")

    # =========================================================================
    # SLIDE 05: OPERATOR WORKFLOW ON PACKING BENCH
    # Claude Aesthetics: 3 Step Cards on Top + Bench Placard Card with Mint Line
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_hud_header(s5, "Packing Bench Ergonomics", "Operator Bench Flow: Three-Step Zero-Click Cycle", active_phase_idx=1)

    # Subtitle
    tb_sub5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.35))
    tf_sub5 = tb_sub5.text_frame
    tf_sub5.word_wrap = True
    tf_sub5.margin_left = tf_sub5.margin_top = tf_sub5.margin_right = tf_sub5.margin_bottom = 0
    p_s5 = tf_sub5.paragraphs[0]
    p_s5.text = "Operators never touch a mouse or switch applications. All actions trigger via physical barcodes."
    p_s5.font.name = FONT_PRIMARY
    p_s5.font.size = Pt(13)
    p_s5.font.color.rgb = COLOR_TEXT_SLATE

    # Left Column: 3 Stacked Step Cards
    left_x = Inches(0.8)
    left_w = Inches(6.8)
    card_h = Inches(1.45)
    card_gap = Inches(0.2)

    steps = [
        ("STEP 01", "Scan Barcode", "0.2s", "DURATION",
         "Operator scans shipping label or product barcode with handheld scanner. System detects burst and locks pre-roll buffer."),
        ("STEP 02", "Pack & Seal Parcel", "NATURAL", "DURATION",
         "Overhead 4K camera records continuously while the operator packs. Real-time visual indicator confirms active recording."),
        ("STEP 03", "Scan Finish Placard", "0.1s", "DURATION",
         "Operator scans physical bench finish placard. Recording halts, encodes with hardware H.264, and indexes instantly.")
    ]

    for i, (st_num, st_name, st_metric, st_lbl, st_desc) in enumerate(steps):
        sy = Inches(2.05) + i * (card_h + card_gap)
        add_dark_card(s5, left_x, sy, left_w, card_h)

        # Left text inside step card
        tb_st = s5.shapes.add_textbox(left_x + Inches(0.25), sy + Inches(0.18), left_w - Inches(1.8), card_h - Inches(0.36))
        tf_st = tb_st.text_frame
        tf_st.word_wrap = True
        tf_st.margin_left = tf_st.margin_top = tf_st.margin_right = tf_st.margin_bottom = 0

        p1 = tf_st.paragraphs[0]
        p1.text = f"{st_num} // {st_name}"
        p1.font.name = FONT_PRIMARY
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_WHITE

        p2 = tf_st.add_paragraph()
        p2.text = st_desc
        p2.font.name = FONT_PRIMARY
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_TEXT_SLATE
        p2.space_before = Pt(4)

        # Right Metric inside step card
        tb_m = s5.shapes.add_textbox(left_x + left_w - Inches(1.5), sy + Inches(0.22), Inches(1.3), card_h - Inches(0.4))
        tf_m = tb_m.text_frame
        tf_m.word_wrap = True
        tf_m.margin_left = tf_m.margin_top = tf_m.margin_right = tf_m.margin_bottom = 0

        pm1 = tf_m.paragraphs[0]
        pm1.text = st_metric
        pm1.font.name = FONT_MONO
        pm1.font.size = Pt(18)
        pm1.font.bold = True
        pm1.font.color.rgb = COLOR_MINT
        pm1.alignment = PP_ALIGN.RIGHT

        pm2 = tf_m.add_paragraph()
        pm2.text = st_lbl
        pm2.font.name = FONT_MONO
        pm2.font.size = Pt(8.5)
        pm2.font.color.rgb = COLOR_TEXT_MUTED
        pm2.alignment = PP_ALIGN.RIGHT
        pm2.space_before = Pt(2)

    # Right Column: Dedicated Placard Preview Card
    right_x = Inches(7.85)
    right_w = Inches(4.683)
    right_h = Inches(4.75)
    add_dark_card(s5, right_x, Inches(2.05), right_w, right_h, bg_color=COLOR_CARD_SUBTLE)

    # Header inside Placard Card
    tb_rh = s5.shapes.add_textbox(right_x + Inches(0.25), Inches(2.25), right_w - Inches(0.5), Inches(0.3))
    tf_rh = tb_rh.text_frame
    tf_rh.word_wrap = True
    tf_rh.margin_left = tf_rh.margin_top = tf_rh.margin_right = tf_rh.margin_bottom = 0
    prh = tf_rh.paragraphs[0]
    prh.text = "BENCH FINISH PLACARD // RIGID ACRYLIC"
    prh.font.name = FONT_MONO
    prh.font.size = Pt(9.5)
    prh.font.bold = True
    prh.font.color.rgb = COLOR_TEXT_MUTED

    # Barcode image
    if os.path.exists(IMG_PLACARD):
        s5.shapes.add_picture(IMG_PLACARD, right_x + Inches(0.25), Inches(2.6), width=right_w - Inches(0.5))

    # Description & Callout below barcode image
    tb_rd = s5.shapes.add_textbox(right_x + Inches(0.25), Inches(5.35), right_w - Inches(0.5), Inches(1.3))
    tf_rd = tb_rd.text_frame
    tf_rd.word_wrap = True
    tf_rd.margin_left = tf_rd.margin_top = tf_rd.margin_right = tf_rd.margin_bottom = 0

    prd1 = tf_rd.paragraphs[0]
    prd1.text = "A physical barcode placard sits on the packing table within easy reach. One scan seals, encodes, hashes, and indexes the clip."
    prd1.font.name = FONT_PRIMARY
    prd1.font.size = Pt(11)
    prd1.font.color.rgb = COLOR_TEXT_SLATE

    prd2 = tf_rd.add_paragraph()
    prd2.text = "NO MOUSE. NO KEYBOARD. NO WINDOW SWITCHING."
    prd2.font.name = FONT_MONO
    prd2.font.size = Pt(11)
    prd2.font.bold = True
    prd2.font.color.rgb = COLOR_MINT
    prd2.space_before = Pt(8)

    add_hud_footer(s5, "05 / 10")
    set_speaker_notes(s5, "PRESENTER GOAL (30s): Walk through the operator experience. Stress zero screen changes, audible and visual confirmation beeps, and how simple the workflow is.")

    # =========================================================================
    # SLIDE 06: ENTERPRISE ARCHITECTURE SPECIFICATION
    # Claude Aesthetics: 3 Stacked Horizontal Layer Cards with Big Metric Tags
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_hud_header(s6, "Engineering Architecture", "Technical Architecture: Local-First Core", active_phase_idx=1)

    # Subtitle
    tb_sub6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.35))
    tf_sub6 = tb_sub6.text_frame
    tf_sub6.word_wrap = True
    tf_sub6.margin_left = tf_sub6.margin_top = tf_sub6.margin_right = tf_sub6.margin_bottom = 0
    p_s6 = tf_sub6.paragraphs[0]
    p_s6.text = "Designed to operate continuously on local hardware even during warehouse internet outages."
    p_s6.font.name = FONT_PRIMARY
    p_s6.font.size = Pt(13)
    p_s6.font.color.rgb = COLOR_TEXT_SLATE

    # 3 Stacked Horizontal Cards (Tier 03 on top, Tier 01 at bottom)
    tier_y = Inches(2.05)
    tier_w = Inches(11.733)
    tier_h = Inches(1.5)
    tier_gap = Inches(0.2)

    tier_stack = [
        ("TIER 03", "Dispute & Claims Portal",
         "Sub-2s barcode search. Each claim generates a self-contained MP4 video evidence package plus cryptographic SHA-256 JSON verification record for courier portals.",
         "Sub-2s", "BARCODE SEARCH"),
        ("TIER 02", "Station Edge Daemon",
         "Local-first Python OS service with a sub-50ms scanner event bus, circular OpenCV memory buffer, and local SQLite database for instant retrieval.",
         "Sub-50ms", "EVENT BUS"),
        ("TIER 01", "Hardware Bench Rig",
         "Overhead 4K camera with 120-degree FOV, 2D industrial barcode scanner in USB HID keystroke mode, bi-color LED beacon, and 85dB directional audio buzzer.",
         "4K UHD", "OVERHEAD CAMERA")
    ]

    for i, (t_tag, t_title, t_desc, t_metric, t_lbl) in enumerate(tier_stack):
        ty = tier_y + i * (tier_h + tier_gap)
        add_dark_card(s6, Inches(0.8), ty, tier_w, tier_h)

        # Left Text
        tb_t = s6.shapes.add_textbox(Inches(1.1), ty + Inches(0.2), Inches(8.5), tier_h - Inches(0.4))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0

        pt1 = tf_t.paragraphs[0]
        pt1.text = f"{t_tag} // {t_title}"
        pt1.font.name = FONT_PRIMARY
        pt1.font.size = Pt(16)
        pt1.font.bold = True
        pt1.font.color.rgb = COLOR_TEXT_WHITE

        pt2 = tf_t.add_paragraph()
        pt2.text = t_desc
        pt2.font.name = FONT_PRIMARY
        pt2.font.size = Pt(12)
        pt2.font.color.rgb = COLOR_TEXT_SLATE
        pt2.space_before = Pt(6)

        # Right Metric
        tb_tm = s6.shapes.add_textbox(Inches(9.8), ty + Inches(0.25), Inches(2.4), tier_h - Inches(0.5))
        tf_tm = tb_tm.text_frame
        tf_tm.word_wrap = True
        tf_tm.margin_left = tf_tm.margin_top = tf_tm.margin_right = tf_tm.margin_bottom = 0

        pm1 = tf_tm.paragraphs[0]
        pm1.text = t_metric
        pm1.font.name = FONT_MONO
        pm1.font.size = Pt(20)
        pm1.font.bold = True
        pm1.font.color.rgb = COLOR_MINT
        pm1.alignment = PP_ALIGN.RIGHT

        pm2 = tf_tm.add_paragraph()
        pm2.text = t_lbl
        pm2.font.name = FONT_MONO
        pm2.font.size = Pt(9)
        pm2.font.color.rgb = COLOR_TEXT_MUTED
        pm2.alignment = PP_ALIGN.RIGHT
        pm2.space_before = Pt(4)

    add_hud_footer(s6, "06 / 10")
    set_speaker_notes(s6, "PRESENTER GOAL (25-30s): Reassure technical buyers and warehouse IT. Emphasize local-first edge recording with zero external cloud dependencies for continuous capture.")

    # =========================================================================
    # SLIDE 07: PHYSICAL STATION HARDWARE SPECS
    # Claude Aesthetics: 4 Columns with Giant Stat Badges (4K, IP65, 16GB, 85dB)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_hud_header(s7, "Bench Equipment", "Hardware Specifications: Engineered for Industrial Duty", active_phase_idx=2)

    # Subtitle
    tb_sub7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.35))
    tf_sub7 = tb_sub7.text_frame
    tf_sub7.word_wrap = True
    tf_sub7.margin_left = tf_sub7.margin_top = tf_sub7.margin_right = tf_sub7.margin_bottom = 0
    p_s7 = tf_sub7.paragraphs[0]
    p_s7.text = "Rigid industrial components rated for dust, continuous vibration, and 24/7 warehouse operations."
    p_s7.font.name = FONT_PRIMARY
    p_s7.font.size = Pt(13)
    p_s7.font.color.rgb = COLOR_TEXT_SLATE

    # 4 Hardware Columns
    hw_w = Inches(2.75)
    hw_h = Inches(4.8)
    hw_gap = Inches(0.24)
    hw_y = Inches(2.05)

    hw_items = [
        ("01 // OVERHEAD CAM", "4K",
         [
             "4K UHD (3840x2160)",
             "60fps smooth capture",
             "120-degree wide FOV",
             "f/1.8 low-light sensor",
             "Articulated boom arm"
         ]),
        ("02 // 2D SCANNER", "IP65",
         [
             "IP65 rated casing",
             "2.0m drop spec",
             "USB 3.0 / Bluetooth 5.2",
             "Rapid keystroke profile",
             "Instant read on torn labels"
         ]),
        ("03 // EDGE PC", "16GB",
         [
             "Fanless aluminum casing",
             "Intel Quad-Core N100/i3",
             "16GB DDR5 Industrial RAM",
             "Dual 1TB NVMe Solid State",
             "Auto 90-day retention loop"
         ]),
        ("04 // BEACON", "85dB",
         [
             "Bi-color green/red LED",
             "85dB directional buzzer",
             "Start/stop sound tones",
             "Overhead eye-level mount",
             "Rigid acrylic bench placard"
         ])
    ]

    for i, (cat, big_badge, specs) in enumerate(hw_items):
        hx = Inches(0.8) + i * (hw_w + hw_gap)
        add_dark_card(s7, hx, hw_y, hw_w, hw_h)

        tb_h = s7.shapes.add_textbox(hx + Inches(0.2), hw_y + Inches(0.2), hw_w - Inches(0.4), hw_h - Inches(0.4))
        tf_h = tb_h.text_frame
        tf_h.word_wrap = True
        tf_h.margin_left = tf_h.margin_top = tf_h.margin_right = tf_h.margin_bottom = 0

        p1 = tf_h.paragraphs[0]
        p1.text = cat
        p1.font.name = FONT_MONO
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_MUTED

        p2 = tf_h.add_paragraph()
        p2.text = big_badge
        p2.font.name = FONT_MONO
        p2.font.size = Pt(36)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_WHITE
        p2.space_before = Pt(4)

        for sp in specs:
            ps = tf_h.add_paragraph()
            ps.text = f"›  {sp}"
            ps.font.name = FONT_PRIMARY
            ps.font.size = Pt(11)
            ps.font.color.rgb = COLOR_TEXT_SLATE
            ps.space_before = Pt(8)

    add_hud_footer(s7, "07 / 10")
    set_speaker_notes(s7, "PRESENTER GOAL (25-30s): Showcase industrial grade hardware. Rated for dust, high drops, and 24/7 continuous warehouse operations.")

    # =========================================================================
    # SLIDE 08: BUSINESS CASE & MEASURABLE ROI
    # Claude Aesthetics: 3 Big Top Stats (82%, 4.2x, $48,000) + Payback Table
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_hud_header(s8, "Measurable Value", "Business Case: Direct Bottom-Line Financial Impact", active_phase_idx=2)

    # Subtitle
    tb_sub8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.35))
    tf_sub8 = tb_sub8.text_frame
    tf_sub8.word_wrap = True
    tf_sub8.margin_left = tf_sub8.margin_top = tf_sub8.margin_right = tf_sub8.margin_bottom = 0
    p_s8 = tf_sub8.paragraphs[0]
    p_s8.text = "Proven payback metrics across pilot distribution centers and packaging benches."
    p_s8.font.name = FONT_PRIMARY
    p_s8.font.size = Pt(13)
    p_s8.font.color.rgb = COLOR_TEXT_SLATE

    # Top 3 Stat Cards
    stat_w8 = Inches(3.75)
    stat_h8 = Inches(1.8)
    stat_gap8 = Inches(0.24)
    stat_y8 = Inches(2.05)

    roi_stats = [
        ("82%", "DISPUTE WIN RATE", "Recovers 82% of contested merchandise value via courier proof.", COLOR_MINT),
        ("4.2x", "FASTER INVESTIGATIONS", "Claims resolved in under 90 seconds instead of 28 minutes.", COLOR_TEXT_WHITE),
        ("$48,000", "ANNUAL SAVINGS PER 10 BENCHES", "Net savings per 10 packaging benches deployed.", COLOR_BLUE)
    ]

    for i, (s_num, s_title, s_desc, s_color) in enumerate(roi_stats):
        rx = Inches(0.8) + i * (stat_w8 + stat_gap8)
        add_dark_card(s8, rx, stat_y8, stat_w8, stat_h8)

        tb_r = s8.shapes.add_textbox(rx + Inches(0.25), stat_y8 + Inches(0.18), stat_w8 - Inches(0.5), stat_h8 - Inches(0.36))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True
        tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0

        p1 = tf_r.paragraphs[0]
        p1.text = s_num
        p1.font.name = FONT_MONO
        p1.font.size = Pt(36)
        p1.font.bold = True
        p1.font.color.rgb = s_color

        p2 = tf_r.add_paragraph()
        p2.text = s_title
        p2.font.name = FONT_MONO
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(4)

        p3 = tf_r.add_paragraph()
        p3.text = s_desc
        p3.font.name = FONT_PRIMARY
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = COLOR_TEXT_SLATE
        p3.space_before = Pt(4)

    # Bottom Financial Payback Table Card (Claude Layout with Native Table)
    tbl_y8 = Inches(4.1)
    tbl_h8 = Inches(2.7)
    add_dark_card(s8, Inches(0.8), tbl_y8, Inches(11.733), tbl_h8, bg_color=COLOR_CARD_SUBTLE)

    payback_rows = [
        ("Write-off recovery", "$32,400"),
        ("Labor reduction", "$11,200"),
        ("Carrier surcharge avoidance", "$4,400"),
        ("Total annual savings", "$48,000"),
        ("Full payback", "Under 90 days")
    ]

    t_shape8 = s8.shapes.add_table(len(payback_rows) + 1, 2, Inches(1.0), tbl_y8 + Inches(0.15), Inches(11.333), tbl_h8 - Inches(0.3))
    tbl8 = t_shape8.table
    tbl8.columns[0].width = Inches(7.5)
    tbl8.columns[1].width = Inches(3.833)

    # Header Row
    c0 = tbl8.cell(0, 0)
    c0.fill.solid(); c0.fill.fore_color.rgb = COLOR_CARD
    c0.margin_left = c0.margin_right = Inches(0.12)
    c0.margin_top = c0.margin_bottom = Inches(0.08)
    p0 = c0.text_frame.paragraphs[0]
    p0.text = "FINANCIAL PAYBACK MODEL"
    p0.font.name = FONT_MONO
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_TEXT_MUTED

    c1 = tbl8.cell(0, 1)
    c1.fill.solid(); c1.fill.fore_color.rgb = COLOR_CARD
    c1.margin_left = c1.margin_right = Inches(0.12)
    c1.margin_top = c1.margin_bottom = Inches(0.08)
    p1 = c1.text_frame.paragraphs[0]
    p1.text = "ANNUAL, PER 10 BENCHES"
    p1.font.name = FONT_MONO
    p1.font.size = Pt(10)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MUTED
    p1.alignment = PP_ALIGN.RIGHT

    for r_idx, (p_name, p_val) in enumerate(payback_rows):
        cell0 = tbl8.cell(r_idx + 1, 0)
        cell1 = tbl8.cell(r_idx + 1, 1)
        bg = COLOR_CARD_SUBTLE if r_idx % 2 == 1 else COLOR_CARD
        cell0.fill.solid(); cell0.fill.fore_color.rgb = bg
        cell1.fill.solid(); cell1.fill.fore_color.rgb = bg

        cell0.margin_left = cell0.margin_right = cell1.margin_left = cell1.margin_right = Inches(0.12)
        cell0.margin_top = cell0.margin_bottom = cell1.margin_top = cell1.margin_bottom = Inches(0.06)

        pr0 = cell0.text_frame.paragraphs[0]
        pr0.text = p_name
        pr0.font.name = FONT_PRIMARY
        pr0.font.size = Pt(11.5)
        pr0.font.bold = (p_name == "Total annual savings")
        pr0.font.color.rgb = COLOR_MINT if (p_name in ["Total annual savings", "Full payback"]) else COLOR_TEXT_WHITE

        pr1 = cell1.text_frame.paragraphs[0]
        pr1.text = p_val
        pr1.font.name = FONT_MONO
        pr1.font.size = Pt(12)
        pr1.font.bold = True
        pr1.alignment = PP_ALIGN.RIGHT
        pr1.font.color.rgb = COLOR_MINT if (p_name in ["Total annual savings", "Full payback"]) else COLOR_TEXT_WHITE

    add_hud_footer(s8, "08 / 10")
    set_speaker_notes(s8, "PRESENTER GOAL (30s): Drive home the financial justification. Highlight the 82% win rate, 4.2x faster resolution, and $48,000 annual savings per 10 packaging benches.")

    # =========================================================================
    # SLIDE 09: 4-WEEK DEPLOYMENT ROADMAP
    # Claude Aesthetics: 4 Phased Timeline Cards
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_hud_header(s9, "Implementation Schedule", "4-Week Deployment Roadmap: Zero Downtime", active_phase_idx=3)

    # Subtitle
    tb_sub9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.35))
    tf_sub9 = tb_sub9.text_frame
    tf_sub9.word_wrap = True
    tf_sub9.margin_left = tf_sub9.margin_top = tf_sub9.margin_right = tf_sub9.margin_bottom = 0
    p_s9 = tf_sub9.paragraphs[0]
    p_s9.text = "Turnkey implementation designed to fit seamlessly into active packing bench operations."
    p_s9.font.name = FONT_PRIMARY
    p_s9.font.size = Pt(13)
    p_s9.font.color.rgb = COLOR_TEXT_SLATE

    # 4 Phased Timeline Cards
    rm_w = Inches(2.75)
    rm_h = Inches(4.8)
    rm_gap = Inches(0.24)
    rm_y = Inches(2.05)

    roadmap_steps = [
        ("WEEK 01", "Bench Audit & Rigging",
         [
             "Camera boom mount",
             "Scanner latency calibration",
             "Packing table FOV audit",
             "Power and cable delivery"
         ]),
        ("WEEK 02", "Station Pilot Launch",
         [
             "Single bench activation",
             "5s buffer validation",
             "Operator observation",
             "Local storage retention loop"
         ]),
        ("WEEK 03", "Full Facility Expansion",
         [
             "Multi-bench rollout",
             "NAS storage sync",
             "Claims team portal training",
             "Dispute workflow sign-off"
         ]),
        ("WEEK 04", "WMS / ERP Cutover",
         [
             "WMS barcode API sync",
             "Automated courier export",
             "Executive metrics sign-off",
             "Full production cutover"
         ])
    ]

    for i, (wk_num, wk_title, wk_tasks) in enumerate(roadmap_steps):
        rx = Inches(0.8) + i * (rm_w + rm_gap)
        add_dark_card(s9, rx, rm_y, rm_w, rm_h)

        tb_rm = s9.shapes.add_textbox(rx + Inches(0.2), rm_y + Inches(0.2), rm_w - Inches(0.4), rm_h - Inches(0.4))
        tf_rm = tb_rm.text_frame
        tf_rm.word_wrap = True
        tf_rm.margin_left = tf_rm.margin_top = tf_rm.margin_right = tf_rm.margin_bottom = 0

        p1 = tf_rm.paragraphs[0]
        p1.text = wk_num
        p1.font.name = FONT_MONO
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_MINT

        p2 = tf_rm.add_paragraph()
        p2.text = wk_title
        p2.font.name = FONT_PRIMARY
        p2.font.size = Pt(16)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_WHITE
        p2.space_before = Pt(6)

        for task in wk_tasks:
            pt = tf_rm.add_paragraph()
            pt.text = f"›  {task}"
            pt.font.name = FONT_PRIMARY
            pt.font.size = Pt(11)
            pt.font.color.rgb = COLOR_TEXT_SLATE
            pt.space_before = Pt(8)

    add_hud_footer(s9, "09 / 10")
    set_speaker_notes(s9, "PRESENTER GOAL (25s): Show low friction adoption. A structured 4-week rollout that integrates with existing bench layouts without warehouse downtime.")

    # =========================================================================
    # SLIDE 10: EXECUTIVE SUMMARY & NEXT STEPS
    # Claude Aesthetics: 3 Action Cards on Top + Clean Dark Callout Banner
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_hud_header(s10, "Executive Action Plan", "Transform Packing Bench Accountability", active_phase_idx=3)

    # Subtitle
    tb_sub10 = s10.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.35))
    tf_sub10 = tb_sub10.text_frame
    tf_sub10.word_wrap = True
    tf_sub10.margin_left = tf_sub10.margin_top = tf_sub10.margin_right = tf_sub10.margin_bottom = 0
    p_s10 = tf_sub10.paragraphs[0]
    p_s10.text = "Turn every dispatch into indisputable evidence with zero operator overhead."
    p_s10.font.name = FONT_PRIMARY
    p_s10.font.size = Pt(13)
    p_s10.font.color.rgb = COLOR_TEXT_SLATE

    # Top: 3 Action Cards
    act_w = Inches(3.75)
    act_h = Inches(2.4)
    act_gap = Inches(0.24)
    act_y = Inches(2.05)

    actions = [
        ("ACTION 01", "15-Minute Bench Demo",
         "Inspect the live camera angle, sub-50ms keystroke trigger, and instant search portal on a live test packing bench.",
         "Schedule: Virtual or on-site walkthrough"),
        ("ACTION 02", "30-Day Single-Station Pilot",
         "Deploy Provenance on your highest-volume packaging line with full hardware support and zero IT infrastructure overhaul.",
         "Commitment: Zero-risk pilot evaluation"),
        ("ACTION 03", "Sample Dispute Bundle Inspection",
         "Review the exportable dispute package, SHA-256 hash signature, and carrier-ready documentation format.",
         "Deliverable: Complete evidence package")
    ]

    for i, (act_tag, act_title, act_desc, act_meta) in enumerate(actions):
        ax = Inches(0.8) + i * (act_w + act_gap)
        add_dark_card(s10, ax, act_y, act_w, act_h)

        tb_a = s10.shapes.add_textbox(ax + Inches(0.25), act_y + Inches(0.2), act_w - Inches(0.5), act_h - Inches(0.4))
        tf_a = tb_a.text_frame
        tf_a.word_wrap = True
        tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0

        p1 = tf_a.paragraphs[0]
        p1.text = act_tag
        p1.font.name = FONT_MONO
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_MINT

        p2 = tf_a.add_paragraph()
        p2.text = act_title
        p2.font.name = FONT_PRIMARY
        p2.font.size = Pt(16)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_WHITE
        p2.space_before = Pt(6)

        p3 = tf_a.add_paragraph()
        p3.text = act_desc
        p3.font.name = FONT_PRIMARY
        p3.font.size = Pt(11.5)
        p3.font.color.rgb = COLOR_TEXT_SLATE
        p3.space_before = Pt(6)

        p4 = tf_a.add_paragraph()
        p4.text = act_meta
        p4.font.name = FONT_MONO
        p4.font.size = Pt(9.5)
        p4.font.color.rgb = COLOR_TEXT_MUTED
        p4.space_before = Pt(8)

    # Bottom: Clean Callout Banner (Claude Layout)
    cta_y = Inches(4.7)
    cta_h = Inches(2.1)
    cta_w = Inches(11.733)
    add_dark_card(s10, Inches(0.8), cta_y, cta_w, cta_h, bg_color=COLOR_CARD_SUBTLE)

    tb_cta = s10.shapes.add_textbox(Inches(1.2), cta_y + Inches(0.3), cta_w - Inches(0.8), cta_h - Inches(0.6))
    tf_cta = tb_cta.text_frame
    tf_cta.word_wrap = True

    p_c1 = tf_cta.paragraphs[0]
    p_c1.text = "READY TO ELIMINATE PACKING DISPUTE WRITE-OFFS?"
    p_c1.font.name = FONT_MONO
    p_c1.font.size = Pt(11)
    p_c1.font.bold = True
    p_c1.font.color.rgb = COLOR_MINT
    p_c1.alignment = PP_ALIGN.CENTER

    p_c2 = tf_cta.add_paragraph()
    p_c2.text = "Book a 15-Minute Live Packing Bench Walkthrough"
    p_c2.font.name = FONT_PRIMARY
    p_c2.font.size = Pt(26)
    p_c2.font.bold = True
    p_c2.font.color.rgb = COLOR_TEXT_WHITE
    p_c2.alignment = PP_ALIGN.CENTER
    p_c2.space_before = Pt(6)

    p_c3 = tf_cta.add_paragraph()
    p_c3.text = "sales@provenance-systems.com   |   +1 (800) 555-PACK"
    p_c3.font.name = FONT_MONO
    p_c3.font.size = Pt(13)
    p_c3.font.color.rgb = COLOR_TEXT_SLATE
    p_c3.alignment = PP_ALIGN.CENTER
    p_c3.space_before = Pt(10)

    add_hud_footer(s10, "10 / 10")
    set_speaker_notes(s10, "PRESENTER GOAL (20-30s): Call to action. Close with a frictionless offer: a 15-minute live bench demonstration or a 30-day pilot on their highest-volume line.")

    # Save PowerPoint deck safely
    os.system("taskkill /f /im POWERPNT.exe >nul 2>&1")
    prs.save(output_path)
    print(f"[SUCCESS] Dark HUD presentation generated at: {output_path}")

    # Apply content-tailored PowerPoint transitions
    try:
        import win32com.client
        ppt_app = win32com.client.Dispatch('PowerPoint.Application')
        pres = ppt_app.Presentations.Open(os.path.abspath(output_path), WithWindow=False)

        transitions_map = [
            (1, 3849, 1.0, "FadeSmoothly (Hero Title Opening)"),
            (2, 3932, 0.8, "PanRight (Problem Timeline Tracking)"),
            (3, 3585, 0.75, "SplitHorizontalOut (Before vs After Contrast Reveal)"),
            (4, 3895, 0.7, "RevealSmoothRight (Solution Architecture Reveal)"),
            (5, 3854, 0.7, "PushRight (Packing Bench Conveyor Flow)"),
            (6, 3855, 0.8, "PushUp (Technical Architecture Stack Deep Dive)"),
            (7, 2051, 0.7, "UncoverRight (Physical Hardware Uncover)"),
            (8, 2819, 0.65, "WipeRight (High-Velocity Data Wipe)"),
            (9, 3932, 0.75, "PanRight (Roadmap Timeline Pan)"),
            (10, 3849, 1.0, "FadeSmoothly (Executive Summary & Action Call)"),
        ]

        for slide_num, effect_id, duration, desc in transitions_map:
            slide_obj = pres.Slides(slide_num)
            slide_obj.SlideShowTransition.EntryEffect = effect_id
            slide_obj.SlideShowTransition.Duration = duration
            slide_obj.SlideShowTransition.AdvanceOnClick = -1
            print(f"  Slide {slide_num:02d}: Applied {desc}")

        pres.Save()

        # Export all 10 slide previews at 1080p
        out_preview_dir = os.path.join(BRAIN_DIR, "slides_preview")
        os.makedirs(out_preview_dir, exist_ok=True)
        for i in range(1, pres.Slides.Count + 1):
            dest_png = os.path.join(out_preview_dir, f"slide_{i:02d}.png")
            pres.Slides(i).Export(dest_png, "PNG", 1920, 1080)
        print(f"[SUCCESS] Exported all 10 slide previews to: {out_preview_dir}")

        pres.Close()
        ppt_app.Quit()
        print("[SUCCESS] All 10 content-tailored transitions applied cleanly.")
    except Exception as exc:
        print(f"[NOTE] Native transitions skipped or handled offline: {exc}")


if __name__ == "__main__":
    out_file = r"C:\Users\sharv\barcode-test\Provenance_Client_Presentation.pptx"
    build_presentation(out_file)
