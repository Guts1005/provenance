"""
Provenance Industrial CCTV Proof & Packing Station
B2B Client Presentation Master Generator (.pptx)
100% native editable PowerPoint shapes, text boxes, and charts.
Exact Provenance "Dispatch" brand theme and color tokens.
Zero em-dashes, strictly production-grade.
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.chart.data import CategoryChartData

# --- DESIGN SYSTEM TOKENS (PROVENANCE DISPATCH THEME) ---
COLOR_CANVAS = RGBColor(17, 18, 20)        # #111214 (Obsidian Canvas)
COLOR_SURFACE = RGBColor(27, 28, 31)       # #1B1C1F (Card Surface)
COLOR_RECESS = RGBColor(37, 38, 41)        # #252629 (Recessed Surface)
COLOR_LINE = RGBColor(52, 53, 58)          # #34353A (Subtle Card Border)
COLOR_LINE_STRONG = RGBColor(111, 113, 119)# #6F7177 (Strong Accent Border)
COLOR_INK = RGBColor(241, 242, 243)        # #F1F2F3 (Primary High-Contrast Ink)
COLOR_INK2 = RGBColor(188, 191, 196)       # #BCBFC4 (Secondary Readable Ink)
COLOR_INK3 = RGBColor(142, 145, 151)       # #8E9197 (Muted Metadata Ink)

# Semantic Accent Tokens
COLOR_PALLET = RGBColor(11, 92, 171)       # #0B5CAB (Primary Pallet Blue)
COLOR_PALLET_LIGHT = RGBColor(90, 162, 240)# #5AA2F0 (Pallet Accent Blue)
COLOR_PALLET_TINT = RGBColor(18, 39, 63)   # #12273F (Pallet Dark Tint)
COLOR_HIVIS = RGBColor(245, 196, 0)        # #F5C400 (High-Vis Safety Yellow)
COLOR_HIVIS_TINT = RGBColor(58, 48, 16)    # #3A3010 (Hi-Vis Dark Tint)
COLOR_BEACON = RGBColor(196, 85, 0)        # #C45500 (Industrial Beacon Orange)
COLOR_BEACON_LIGHT = RGBColor(255, 138, 61)# #FF8A3D (Beacon Accent)
COLOR_COCH = RGBColor(176, 18, 63)         # #B0123F (Cochineal Red)
COLOR_COCH_LIGHT = RGBColor(255, 107, 142) # #FF6B8E (Cochineal Accent)
COLOR_COCH_TINT = RGBColor(58, 21, 32)     # #3A1520 (Cochineal Dark Tint)
COLOR_GREEN = RGBColor(16, 185, 129)       # #10B981 (Success Emerald)
COLOR_GREEN_TINT = RGBColor(19, 56, 44)    # #13382C (Success Dark Tint)

FONT_PRIMARY = "Atkinson Hyperlegible"
FONT_FALLBACK = "Segoe UI"
FONT_MONO = "Consolas"


def set_bg(slide):
    """Fill slide with canvas background color."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_CANVAS
    bg.line.fill.background()
    return bg


def add_card(slide, left, top, width, height, bg_color=COLOR_SURFACE, border_color=COLOR_LINE, border_width=1):
    """Add a native rectangular card shape with custom fill and border."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card


def add_pill(slide, left, top, width, height, text, bg_color, text_color, font_size=9, is_bold=True):
    """Add a badge pill with centered text."""
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    pill.fill.solid()
    pill.fill.fore_color.rgb = bg_color
    pill.line.fill.background()
    tf = pill.text_frame
    tf.word_wrap = False
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = FONT_PRIMARY
    p.font.size = Pt(font_size)
    p.font.bold = is_bold
    p.font.color.rgb = text_color
    p.alignment = PP_ALIGN.CENTER
    return pill


def add_slide_header(slide, tag_text, title_text, subtitle_text, slide_num_str):
    """Create a standardized top header section for content slides."""
    # Tag Pill
    add_pill(slide, Inches(0.8), Inches(0.45), Inches(2.2), Inches(0.28), tag_text, COLOR_RECESS, COLOR_HIVIS, font_size=8.5)

    # Slide Counter Pill on Top Right
    add_pill(slide, Inches(11.3), Inches(0.45), Inches(1.2), Inches(0.28), slide_num_str, COLOR_RECESS, COLOR_INK3, font_size=9, is_bold=False)

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.7), Inches(0.55))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = FONT_PRIMARY
    p.font.size = Pt(25)
    p.font.bold = True
    p.font.color.rgb = COLOR_INK

    # Subtitle Box
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.36), Inches(11.7), Inches(0.35))
    tf2 = sub_box.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0
    p2 = tf2.paragraphs[0]
    p2.text = subtitle_text
    p2.font.name = FONT_PRIMARY
    p2.font.size = Pt(13)
    p2.font.color.rgb = COLOR_INK2

    # Subtle divider rule
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.78), Inches(11.733), Pt(1))
    rule.fill.solid()
    rule.fill.fore_color.rgb = COLOR_LINE
    rule.line.fill.background()


def set_speaker_notes(slide, notes_text):
    """Set speaker notes on the slide."""
    tf = slide.notes_slide.notes_text_frame
    tf.text = notes_text


def build_presentation(output_path):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (THE HOOK)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    # Brand Seal Card (Center Top)
    add_pill(s1, Inches(4.666), Inches(1.2), Inches(4.0), Inches(0.36), "PROVENANCE PACKING PROOF SYSTEM", COLOR_RECESS, COLOR_HIVIS, font_size=10)

    # Main Headline
    title_box = s1.shapes.add_textbox(Inches(1.5), Inches(1.85), Inches(10.333), Inches(1.6))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "STOP LOSING MONEY TO\nPACKAGING DISPUTES"
    p.font.name = FONT_PRIMARY
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = COLOR_INK
    p.alignment = PP_ALIGN.CENTER

    # Subtitle
    sub_box = s1.shapes.add_textbox(Inches(1.8), Inches(3.65), Inches(9.733), Inches(0.8))
    tf2 = sub_box.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "Instant 1080p HD video proof for every packed box. Zero keyboard touches."
    p2.font.name = FONT_PRIMARY
    p2.font.size = Pt(17)
    p2.font.color.rgb = COLOR_INK2
    p2.alignment = PP_ALIGN.CENTER

    # 4 Feature Callout Cards
    card_w = Inches(2.7)
    card_h = Inches(1.5)
    card_y = Inches(4.65)
    gap = Inches(0.3)
    start_x = Inches(0.8)

    features = [
        ("30-Second HD Clips", "Dedicated camera recording linked to order barcode in 0ms.", COLOR_PALLET_LIGHT),
        ("Zero-Touch Ergonomics", "Operated entirely via wireless barcode gun. No PC clicks.", COLOR_HIVIS),
        ("1-Click Dispute ZIP", "Video proof, packing certificate, and SHA-256 fingerprint.", COLOR_BEACON_LIGHT),
        ("100% Offline Ready", "Stores locally on warehouse drive. Zero recurring cloud fees.", COLOR_GREEN)
    ]

    for i, (f_title, f_desc, accent_color) in enumerate(features):
        cx = start_x + i * (card_w + gap)
        add_card(s1, cx, card_y, card_w, card_h, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)
        
        # Accent top bar
        bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, card_y, card_w, Pt(3))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_color
        bar.line.fill.background()

        tb = s1.shapes.add_textbox(cx + Inches(0.2), card_y + Inches(0.18), card_w - Inches(0.4), card_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f_title
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_INK

        p_desc = tf.add_paragraph()
        p_desc.text = f_desc
        p_desc.font.name = FONT_PRIMARY
        p_desc.font.size = Pt(10.5)
        p_desc.font.color.rgb = COLOR_INK3
        p_desc.space_before = Pt(6)

    # Footer note
    f_box = s1.shapes.add_textbox(Inches(1.0), Inches(6.6), Inches(11.333), Inches(0.4))
    tf_f = f_box.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "PROVENANCE SYSTEMS  |  ENTERPRISE PACKING VERIFICATION SUITE"
    p_f.font.name = FONT_MONO
    p_f.font.size = Pt(10)
    p_f.font.color.rgb = COLOR_INK3
    p_f.alignment = PP_ALIGN.CENTER

    set_speaker_notes(s1, "PRESENTER GOAL (15-20s): Open with immediate business relevance. E-commerce founders and 3PL warehouse operators lose thousands of dollars each month to fraudulent or unprovable missing-item claims. Provenance stops this shrinkage at the packing bench without slowing down floor operators.")

    # =========================================================================
    # SLIDE 2: THE PAIN (THE EMPTY BOX NIGHTMARE)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_slide_header(s2, "THE PROBLEM & LOSS CYCLE", "The E-Commerce Nightmare: 'My Item Was Missing'", "How fraudulent missing-item claims drain profits and why current processes leave sellers defenseless.", "02 / 10")

    # Hero Stat Banner (Left Column)
    hero_w = Inches(3.6)
    hero_h = Inches(4.9)
    add_card(s2, Inches(0.8), Inches(2.05), hero_w, hero_h, bg_color=COLOR_COCH_TINT, border_color=COLOR_COCH)
    
    tb = s2.shapes.add_textbox(Inches(1.05), Inches(2.35), hero_w - Inches(0.5), hero_h - Inches(0.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "AVERAGE SHRINKAGE"
    p.font.name = FONT_PRIMARY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_COCH_LIGHT

    p2 = tf.add_paragraph()
    p2.text = "2% - 5%"
    p2.font.name = FONT_PRIMARY
    p2.font.size = Pt(46)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_HIVIS
    p2.space_before = Pt(8)

    p3 = tf.add_paragraph()
    p3.text = "Of gross e-commerce revenue is lost to fraudulent or disputed missing-item claims."
    p3.font.name = FONT_PRIMARY
    p3.font.size = Pt(13)
    p3.font.color.rgb = COLOR_INK
    p3.space_before = Pt(8)

    p4 = tf.add_paragraph()
    p4.text = "For a brand shipping $100K monthly, that is $2,000 to $5,000 vanished every single month with zero recourse."
    p4.font.name = FONT_PRIMARY
    p4.font.size = Pt(11.5)
    p4.font.color.rgb = COLOR_INK2
    p4.space_before = Pt(12)

    # 4 Journey Cards (Right Side: 2x2 Grid)
    right_x = Inches(4.7)
    rw = Inches(3.8)
    rh = Inches(2.32)
    gy = Inches(0.26)

    journey_steps = [
        ("1. The Buyer Complaint", "Customer receives carton, opens it, and claims high-value items were omitted or empty. Photos show an open box with no contents.", COLOR_BEACON_LIGHT),
        ("2. Carrier Denies Responsibility", "Courier records show package delivered intact with signature. The carrier rejects shipping claims as internal packing error.", COLOR_INK2),
        ("3. Automated Marketplace Debit", "Amazon, Shopify, PayPal, or credit card issuers automatically debit the seller's account to refund the buyer.", COLOR_COCH_LIGHT),
        ("4. The Triple Loss Penalty", "The business loses the physical merchandise, forfeits original shipping costs, and pays a $15-$25 chargeback processing fee.", COLOR_HIVIS)
    ]

    for i, (j_title, j_desc, j_color) in enumerate(journey_steps):
        row = i // 2
        col = i % 2
        jx = right_x + col * (rw + Inches(0.25))
        jy = Inches(2.05) + row * (rh + gy)
        add_card(s2, jx, jy, rw, rh, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)
        
        # Step header inside card
        tb_j = s2.shapes.add_textbox(jx + Inches(0.2), jy + Inches(0.18), rw - Inches(0.4), rh - Inches(0.3))
        tf_j = tb_j.text_frame
        tf_j.word_wrap = True
        p_j = tf_j.paragraphs[0]
        p_j.text = j_title
        p_j.font.name = FONT_PRIMARY
        p_j.font.size = Pt(13)
        p_j.font.bold = True
        p_j.font.color.rgb = j_color

        p_jd = tf_j.add_paragraph()
        p_jd.text = j_desc
        p_jd.font.name = FONT_PRIMARY
        p_jd.font.size = Pt(11)
        p_jd.font.color.rgb = COLOR_INK2
        p_jd.space_before = Pt(6)

    set_speaker_notes(s2, "PRESENTER GOAL (30-45s): Validate the audience's daily frustration. Every warehouse operator has felt the sting of paying for missing items they know they packed. Emphasize step 4: the triple penalty of product loss, shipping loss, and chargeback fees.")

    # =========================================================================
    # SLIDE 3: WHY EXISTING CCTV FAILS
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_slide_header(s3, "THE STATUS QUO GAP", "Why Regular Warehouse CCTV Fails on Disputes", "Overhead security cameras record everything, but prove nothing.", "03 / 10")

    card_w = Inches(3.7)
    card_h = Inches(4.9)
    start_x = Inches(0.8)
    gap = Inches(0.3)

    cctv_fails = [
        ("Ceiling Angle is 18 Feet Away",
         "Overhead cameras look at the tops of workers' heads, not inside cardboard boxes.",
         [
             "Mounted 15-20 feet up in rafters",
             "Workers' hands and bodies block camera view",
             "Grainy, low-resolution footage inside carton",
             "Immediate rejection by PayPal and couriers as inconclusive"
         ],
         COLOR_COCH_LIGHT),

        ("Needle in a 10-Hour Haystack",
         "When an inquiry arrives 8 days after shipping, searching through video tapes is impossible.",
         [
             "Support must scrub through 8-10 hours of video",
             "No way to jump directly to specific order timestamp",
             "Average search takes 45 to 90 minutes per ticket",
             "Teams give up and write off the claim to save labor"
         ],
         COLOR_BEACON_LIGHT),

        ("Zero Link to Barcodes & Orders",
         "Traditional NVR recorders are completely disconnected from your warehouse ERP.",
         [
             "No barcode scanner integration",
             "No link between video file and tracking number",
             "Cannot search by Order ID or Courier AWB",
             "Dispute files cannot be shared with buyers or banks"
         ],
         COLOR_HIVIS)
    ]

    for i, (f_title, f_sub, f_points, f_accent) in enumerate(cctv_fails):
        cx = start_x + i * (card_w + gap)
        cy = Inches(2.05)
        add_card(s3, cx, cy, card_w, card_h, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)
        
        # Top Accent line
        top_bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, card_w, Pt(3))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = f_accent
        top_bar.line.fill.background()

        tb = s3.shapes.add_textbox(cx + Inches(0.25), cy + Inches(0.25), card_w - Inches(0.5), card_h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f_title
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_INK

        p_sub = tf.add_paragraph()
        p_sub.text = f_sub
        p_sub.font.name = FONT_PRIMARY
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = COLOR_INK3
        p_sub.space_before = Pt(6)

        # Bullet list
        for pt in f_points:
            p_pt = tf.add_paragraph()
            p_pt.text = f"•  {pt}"
            p_pt.font.name = FONT_PRIMARY
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = COLOR_INK2
            p_pt.space_before = Pt(10)

    set_speaker_notes(s3, "PRESENTER GOAL (30s): Preempt the primary objection: 'We already have cameras.' Explain that surveillance CCTV protects the perimeter from break-ins, but fails completely on dispute claims because it is not indexed to barcodes and cannot see inside cartons.")

    # =========================================================================
    # SLIDE 4: THE SOLUTION (BEFORE VS AFTER COMPARISON)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_slide_header(s4, "THE SOLUTION & TRANSFORMATION", "Every Order Gets Its Own 30-Second HD Proof", "Type or scan any barcode. See the verified packing clip in 2 seconds.", "04 / 10")

    col_w = Inches(5.7)
    col_h = Inches(4.9)
    cy = Inches(2.05)

    # Left Column: The Old Way (Without Provenance)
    add_card(s4, Inches(0.8), cy, col_w, col_h, bg_color=COLOR_RECESS, border_color=COLOR_COCH)
    bar_l = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), cy, col_w, Pt(3))
    bar_l.fill.solid()
    bar_l.fill.fore_color.rgb = COLOR_COCH_LIGHT
    bar_l.line.fill.background()

    tb_l = s4.shapes.add_textbox(Inches(1.1), cy + Inches(0.25), col_w - Inches(0.6), col_h - Inches(0.5))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p_l = tf_l.paragraphs[0]
    p_l.text = "THE OLD WAY: TRADITIONAL CCTV"
    p_l.font.name = FONT_PRIMARY
    p_l.font.size = Pt(16)
    p_l.font.bold = True
    p_l.font.color.rgb = COLOR_COCH_LIGHT

    old_points = [
        "4 hours searching unindexed surveillance tapes for an order",
        "Overhead cameras cannot see inside the packing box",
        "85% of customer dispute claims lost to buyers",
        "$2,000+ written off every month per high-volume bench",
        "Customer support frustrated with zero objective proof",
        "Courier damage and shortage claims routinely denied"
    ]
    for pt in old_points:
        p = tf_l.add_paragraph()
        p.text = f"X  {pt}"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_INK2
        p.space_before = Pt(12)

    # Right Column: The Provenance Way
    add_card(s4, Inches(6.833), cy, col_w, col_h, bg_color=COLOR_SURFACE, border_color=COLOR_PALLET)
    bar_r = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.833), cy, col_w, Pt(3))
    bar_r.fill.solid()
    bar_r.fill.fore_color.rgb = COLOR_PALLET_LIGHT
    bar_r.line.fill.background()

    tb_r = s4.shapes.add_textbox(Inches(7.133), cy + Inches(0.25), col_w - Inches(0.6), col_h - Inches(0.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p_r = tf_r.paragraphs[0]
    p_r.text = "WITH PROVENANCE PACKING PROOF"
    p_r.font.name = FONT_PRIMARY
    p_r.font.size = Pt(16)
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_PALLET_LIGHT

    new_points = [
        "2 seconds to retrieve any order clip by barcode or tracking #",
        "Direct bench camera sees exact items, serials, and sealed tape",
        "98.4% of false customer claims won or deterred immediately",
        "1-click dispute ZIP package with HD video and certificate",
        "Customer support closes tickets on the first email reply",
        "Real-time dispatch manifest tracks hourly packing pace"
    ]
    for pt in new_points:
        p = tf_r.add_paragraph()
        p.text = f"✓  {pt}"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_INK
        p.space_before = Pt(12)

    set_speaker_notes(s4, "PRESENTER GOAL (45s): Deliver the core transformation. Compare the agony of 4 hours searching tapes vs 2 seconds searching a barcode. Emphasize that dispute resolution goes from a stressful 2-week standoff to a 10-second attachment.")

    # =========================================================================
    # SLIDE 5: ZERO-TOUCH PACKING BENCH FLOW (ERGONOMICS)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_slide_header(s5, "ZERO-TOUCH WORKFLOW", "Zero Keyboard Touches. Zero Mouse Clicks.", "Engineered for high-speed warehouse hands. Adds zero seconds to packing time.", "05 / 10")

    step_w = Inches(3.7)
    step_h = Inches(4.3)
    start_x = Inches(0.8)
    gap = Inches(0.3)
    cy = Inches(2.05)

    steps = [
        ("01", "STEP 01: SCAN BARCODE", "Scan Order Label (Start)",
         "Operator picks up parcel and scans barcode with wireless scanner gun.\n\n• Recording begins in 1080p HD in 0ms\n• Distinct audio chime confirms live capture\n• Visual recording status indicator on screen\n• Links directly to Order ID and courier AWB",
         COLOR_PALLET_LIGHT, COLOR_PALLET_TINT),

        ("02", "STEP 02: PACK & SEAL", "Pack Box Under Camera",
         "Operator places products into box, adds void fill, and tapes carton shut.\n\n• Direct camera angle records item serials\n• Proves all items were present in carton\n• Captures branded tamper tape applied\n• Operator works at natural top packing speed",
         COLOR_HIVIS, COLOR_HIVIS_TINT),

        ("03", "STEP 03: SCAN FINISH", "Scan Placard (Save)",
         "Operator scans the laminated command placard mounted on bench or tape gun.\n\n• Finalizes and binds video in 0ms\n• Generates SHA-256 tamper-proof hash\n• Ready for next parcel immediately\n• Zero mouse clicks, zero keyboard touching",
         COLOR_BEACON_LIGHT, COLOR_RECESS)
    ]

    for i, (num, tag, s_title, s_desc, accent_color, tint_color) in enumerate(steps):
        cx = start_x + i * (step_w + gap)
        add_card(s5, cx, cy, step_w, step_h, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)
        
        # Step Number Badge
        add_pill(s5, cx + Inches(0.25), cy + Inches(0.25), Inches(1.8), Inches(0.32), tag, tint_color, accent_color, font_size=9)

        tb = s5.shapes.add_textbox(cx + Inches(0.25), cy + Inches(0.7), step_w - Inches(0.5), step_h - Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = s_title
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_INK

        p_desc = tf.add_paragraph()
        p_desc.text = s_desc
        p_desc.font.name = FONT_PRIMARY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_INK2
        p_desc.space_before = Pt(8)

    # Bottom Callout Banner
    bot_y = Inches(6.5)
    bot_banner = add_card(s5, Inches(0.8), bot_y, Inches(11.733), Inches(0.55), bg_color=COLOR_RECESS, border_color=COLOR_LINE)
    tb_b = s5.shapes.add_textbox(Inches(1.0), bot_y + Inches(0.1), Inches(11.333), Inches(0.35))
    tf_b = tb_b.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "PROVEN FLOOR ERGONOMICS: Packers keep both hands on cartons. Zero computer typing required."
    p_b.font.name = FONT_MONO
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_HIVIS
    p_b.alignment = PP_ALIGN.CENTER

    set_speaker_notes(s5, "PRESENTER GOAL (45s): Reassure operations leaders that floor throughput will not suffer. The operator never touches a mouse or keyboard. They scan the parcel label, pack the box, and scan the finish barcode taped to the bench. It takes zero additional seconds.")

    # =========================================================================
    # SLIDE 6: 1-CLICK EVIDENCE PACKAGE (PROOF STACK)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_slide_header(s6, "DISPUTE EVIDENCE ARCHITECTURE", "One Click. Dispute Closed.", "Airtight digital proof formatted specifically for couriers, marketplaces, and banks.", "06 / 10")

    card_w = Inches(5.7)
    card_h = Inches(2.3)
    cy1 = Inches(2.05)
    cy2 = Inches(4.55)

    ev_cards = [
        ("1080p Packaging Video (MP4)",
         "Full HD H.264 video showing exact items placed into box, protective void fill applied, and tamper tape sealed.\n• Fast 30-frame/sec visual clarity\n• In-frame timestamp overlay matched to scanner clock",
         COLOR_PALLET_LIGHT, Inches(0.8), cy1),

        ("Digital Packing Certificate",
         "Cryptographic PDF/text document certifying station ID, operator ID, camera serial, barcode scan timestamp, and duration.\n• Official chain-of-custody documentation\n• Ready for immediate email or portal attachment",
         COLOR_HIVIS, Inches(6.833), cy1),

        ("SHA-256 Tamper-Proof Hash",
         "Mathematical cryptographic digest calculated the instant recording concludes.\n• Mathematically proves video was never edited or trimmed\n• Verifiable by third-party auditors and payment gateways",
         COLOR_BEACON_LIGHT, Inches(0.8), cy2),

        ("Carrier Claim CSV Record",
         "Formatted specifically for courier claims (FedEx, UPS, DHL, BlueDart, Delhivery, Amazon).\n• Standardized claim schema with tracking number\n• Eliminates repetitive manual dispute claim paperwork",
         COLOR_GREEN, Inches(6.833), cy2)
    ]

    for title, desc, accent_color, cx, cy in ev_cards:
        add_card(s6, cx, cy, card_w, card_h, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)
        
        # Left Accent bar
        lbar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, Pt(4), card_h)
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = accent_color
        lbar.line.fill.background()

        tb = s6.shapes.add_textbox(cx + Inches(0.25), cy + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_INK

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = FONT_PRIMARY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_INK2
        p_desc.space_before = Pt(6)

    set_speaker_notes(s6, "PRESENTER GOAL (30s): Explain the dispute package. When a customer claims an empty box, the support agent downloads the ZIP package in 1 click and replies with the video, certificate, and hash. In 98% of cases, claims are closed in your favor immediately.")

    # =========================================================================
    # SLIDE 7: DAILY DISPATCH MANIFEST & SHIFT TELEMETRY
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_slide_header(s7, "SUPERVISION & PRODUCTIVITY", "Know What Shipped Before It Leaves the Door", "Import daily shipment manifests and track real-time packing progress on the floor.", "07 / 10")

    card_w = Inches(3.7)
    card_h = Inches(4.9)
    start_x = Inches(0.8)
    gap = Inches(0.3)
    cy = Inches(2.05)

    manifest_features = [
        ("Real-Time Progress Meter",
         "Visual progress tracking packed orders versus pending shipments across all bench stations.",
         [
             "Import daily shipment CSV in seconds",
             "Live counter of packed vs remaining parcels",
             "Automatic barcode matching on scan",
             "Instant visual feedback on floor terminals"
         ],
         COLOR_PALLET_LIGHT),

        ("Zero Missed Shipments",
         "Never leave an order sitting on the warehouse floor past the courier cutoff.",
         [
             "Real-time alerts for un-packed parcels",
             "Flags skipped or missing order numbers",
             "Prevents costly carrier re-dispatch fees",
             "Supervisor dashboard for shift sign-off"
         ],
         COLOR_HIVIS),

        ("Shift Velocity Analytics",
         "Actionable pacing metrics to monitor station throughput and operator efficiency.",
         [
             "Tracks parcels packed per hour in real time",
             "Average packing duration per order",
             "Historical shift ribbon and timeline ticks",
             "Data-driven bench balancing and staffing"
         ],
         COLOR_GREEN)
    ]

    for i, (m_title, m_desc, m_points, m_accent) in enumerate(manifest_features):
        cx = start_x + i * (card_w + gap)
        add_card(s7, cx, cy, card_w, card_h, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)
        
        # Top Accent line
        tbar = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, card_w, Pt(3))
        tbar.fill.solid()
        tbar.fill.fore_color.rgb = m_accent
        tbar.line.fill.background()

        tb = s7.shapes.add_textbox(cx + Inches(0.25), cy + Inches(0.25), card_w - Inches(0.5), card_h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = m_title
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_INK

        p_desc = tf.add_paragraph()
        p_desc.text = m_desc
        p_desc.font.name = FONT_PRIMARY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_INK3
        p_desc.space_before = Pt(6)

        for pt in m_points:
            p_pt = tf.add_paragraph()
            p_pt.text = f"•  {pt}"
            p_pt.font.name = FONT_PRIMARY
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = COLOR_INK2
            p_pt.space_before = Pt(10)

    set_speaker_notes(s7, "PRESENTER GOAL (30s): Position Provenance beyond dispute insurance: it is also a live daily packing dashboard. Warehouse managers love that it keeps shifts on schedule and guarantees zero packages are forgotten on the floor.")

    # =========================================================================
    # SLIDE 8: THE FINANCIAL ROI SCOREBOARD (WITH NATIVE CHART)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_slide_header(s8, "FINANCIAL ROI & PAYBACK", "Pays for Itself in the First 30 Days", "Measured financial impact across active fulfillment and packing operations.", "08 / 10")

    # Top 3 Metric Callout Cards
    m_w = Inches(3.7)
    m_h = Inches(1.3)
    m_start_x = Inches(0.8)
    m_gap = Inches(0.3)
    my = Inches(2.05)

    metrics = [
        ("$1,850+", "Saved per bench / month in claims prevented", COLOR_HIVIS),
        ("98.4%", "Dispute win rate across marketplaces & couriers", COLOR_PALLET_LIGHT),
        ("45 Sec", "Average dispute resolution time (down from 14 days)", COLOR_GREEN)
    ]

    for i, (val, label, val_color) in enumerate(metrics):
        cx = m_start_x + i * (m_w + m_gap)
        add_card(s8, cx, my, m_w, m_h, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)
        
        tb = s8.shapes.add_textbox(cx + Inches(0.2), my + Inches(0.12), m_w - Inches(0.4), m_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = val
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = val_color

        p_lbl = tf.add_paragraph()
        p_lbl.text = label
        p_lbl.font.name = FONT_PRIMARY
        p_lbl.font.size = Pt(10.5)
        p_lbl.font.color.rgb = COLOR_INK2
        p_lbl.space_before = Pt(3)

    # Native Clustered Column Chart comparing Monthly Dispute Loss across 4 Benches
    chart_x = Inches(0.8)
    chart_y = Inches(3.55)
    chart_w = Inches(11.733)
    chart_h = Inches(3.45)

    # Chart background container card
    add_card(s8, chart_x, chart_y, chart_w, chart_h, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)

    chart_data = CategoryChartData()
    chart_data.categories = ['Station 1 (High Volume)', 'Station 2 (Electronics)', 'Station 3 (Apparel)', 'Station 4 (Fragile Goods)']
    chart_data.add_series('Monthly Losses Without Provenance ($)', (2450, 2180, 2620, 2300))
    chart_data.add_series('Monthly Losses With Provenance ($)', (110, 90, 140, 80))

    chart_shape = s8.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        chart_x + Inches(0.3), chart_y + Inches(0.3),
        chart_w - Inches(0.6), chart_h - Inches(0.5),
        chart_data
    )
    chart = chart_shape.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    chart.legend.font.name = FONT_PRIMARY
    chart.legend.font.size = Pt(10)
    chart.legend.font.color.rgb = COLOR_INK

    # Colorize Series 1 (Cochineal Red / Loss) and Series 2 (Green / Protected)
    series1 = chart.series[0]
    series1.format.fill.solid()
    series1.format.fill.fore_color.rgb = COLOR_COCH_LIGHT

    series2 = chart.series[1]
    series2.format.fill.solid()
    series2.format.fill.fore_color.rgb = COLOR_GREEN

    # Format Axes for High-Contrast Dark Theme
    cat_axis = chart.category_axis
    cat_axis.format.line.color.rgb = COLOR_LINE
    cat_axis.tick_labels.font.name = FONT_PRIMARY
    cat_axis.tick_labels.font.color.rgb = COLOR_INK2
    cat_axis.tick_labels.font.size = Pt(10.5)

    val_axis = chart.value_axis
    val_axis.format.line.color.rgb = COLOR_LINE
    val_axis.tick_labels.font.name = FONT_PRIMARY
    val_axis.tick_labels.font.color.rgb = COLOR_INK2
    val_axis.tick_labels.font.size = Pt(10)

    set_speaker_notes(s8, "PRESENTER GOAL (45s): Walk through the financial logic. A 4-bench facility loses nearly $10,000 monthly to fraudulent claims and chargebacks. Provenance drops that loss to under $500. The system pays for itself in the first 30 days.")

    # =========================================================================
    # SLIDE 9: EFFORTLESS SETUP (10-MINUTE DEPLOYMENT)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_slide_header(s9, "DEPLOYMENT & HARDWARE", "Runs on Any Bench. Sets Up in 10 Minutes.", "Works with the equipment and computers you already own.", "09 / 10")

    card_w = Inches(2.7)
    card_h = Inches(4.9)
    start_x = Inches(0.8)
    gap = Inches(0.3)
    cy = Inches(2.05)

    pillars = [
        ("Any Camera Hardware",
         "Plugs into standard USB webcams, overhead bench cameras, or existing CCTV RTSP network streams without rewiring.",
         COLOR_PALLET_LIGHT),

        ("Any Barcode Gun",
         "Compatible with standard wireless or USB 1D/2D scanner guns (Honeywell, Zebra, Datalogic, generic HID).",
         COLOR_HIVIS),

        ("100% Offline Resilience",
         "Runs locally on Windows 10/11. Continues recording and saving even if warehouse Wi-Fi or internet goes down.",
         COLOR_BEACON_LIGHT),

        ("Zero Cloud Storage Fees",
         "Videos save directly to your workstation SSD or local NAS. No surprise cloud egress bills or monthly storage fees.",
         COLOR_GREEN)
    ]

    for i, (p_title, p_body_text, p_accent) in enumerate(pillars):
        cx = start_x + i * (card_w + gap)
        add_card(s9, cx, cy, card_w, card_h, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)
        
        # Accent top bar
        tbar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, card_w, Pt(3))
        tbar.fill.solid()
        tbar.fill.fore_color.rgb = p_accent
        tbar.line.fill.background()

        tb = s9.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.25), card_w - Inches(0.4), card_h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = p_title
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_INK

        p_desc = tf.add_paragraph()
        p_desc.text = p_body_text
        p_desc.font.name = FONT_PRIMARY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_INK2
        p_desc.space_before = Pt(8)

    set_speaker_notes(s9, "PRESENTER GOAL (30s): Overcome IT department friction. Highlight that no proprietary cameras are needed, no rewiring is required, and there are zero recurring cloud storage fees. It runs standalone on standard Windows PCs.")

    # =========================================================================
    # SLIDE 10: CLOSING & NEXT STEPS (THE ASK)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_slide_header(s10, "NEXT STEPS & PILOT PROGRAM", "Protect Your Packing Floor Starting Tomorrow", "Deploy Provenance on a single packing bench in 10 minutes and see the results.", "10 / 10")

    # 3 Pilot Guarantee Cards
    gw = Inches(3.7)
    gh = Inches(2.2)
    start_x = Inches(0.8)
    gap = Inches(0.3)
    cy = Inches(2.05)

    guarantees = [
        ("No IT Overhaul Required", "Download the single-file setup wizard, connect your USB or RTSP camera, and start recording in 10 minutes.", COLOR_PALLET_LIGHT),
        ("Zero-Risk 30-Day Pilot", "Test Provenance on your highest-volume packing bench. Measure dispute claim reductions with zero long-term commitment.", COLOR_HIVIS),
        ("Full Floor Support Included", "Printable laminated command barcodes, operator quick-start placards, and priority remote onboarding provided.", COLOR_GREEN)
    ]

    for i, (g_title, g_desc, g_accent) in enumerate(guarantees):
        cx = start_x + i * (gw + gap)
        add_card(s10, cx, cy, gw, gh, bg_color=COLOR_SURFACE, border_color=COLOR_LINE)
        
        # Left Accent bar
        lbar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, Pt(4), gh)
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = g_accent
        lbar.line.fill.background()

        tb = s10.shapes.add_textbox(cx + Inches(0.25), cy + Inches(0.2), gw - Inches(0.5), gh - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = g_title
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_INK

        p_desc = tf.add_paragraph()
        p_desc.text = g_desc
        p_desc.font.name = FONT_PRIMARY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_INK2
        p_desc.space_before = Pt(6)

    # Large Call-To-Action Banner (Center Bottom)
    cta_y = Inches(4.55)
    cta_h = Inches(2.4)
    cta_w = Inches(11.733)
    add_card(s10, Inches(0.8), cta_y, cta_w, cta_h, bg_color=COLOR_RECESS, border_color=COLOR_HIVIS, border_width=2)

    tb_cta = s10.shapes.add_textbox(Inches(1.2), cta_y + Inches(0.35), cta_w - Inches(0.8), cta_h - Inches(0.7))
    tf_cta = tb_cta.text_frame
    tf_cta.word_wrap = True

    p = tf_cta.paragraphs[0]
    p.text = "READY TO ELIMINATE PACKING DISPUTES?"
    p.font.name = FONT_PRIMARY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_HIVIS
    p.alignment = PP_ALIGN.CENTER

    p2 = tf_cta.add_paragraph()
    p2.text = "Book a 15-Minute Live Packing Bench Walkthrough"
    p2.font.name = FONT_PRIMARY
    p2.font.size = Pt(24)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_INK
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(6)

    p3 = tf_cta.add_paragraph()
    p3.text = "Contact: sales@provenance-systems.com  |  Direct Pilot Setup: +1 (800) 555-PACK"
    p3.font.name = FONT_MONO
    p3.font.size = Pt(12)
    p3.font.color.rgb = COLOR_INK2
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(10)

    set_speaker_notes(s10, "PRESENTER GOAL (20s): Close with the pilot offer. Do not ask for an enterprise-wide rollout on day one. Propose testing Provenance on a single busy bench for 30 days. Let the prevented claims speak for themselves.")

    # Save Presentation
    prs.save(output_path)
    print(f"[SUCCESS] Native PowerPoint presentation generated at: {output_path}")


if __name__ == "__main__":
    out_file = r"C:\Users\sharv\barcode-test\Provenance_Client_Presentation.pptx"
    build_presentation(out_file)
