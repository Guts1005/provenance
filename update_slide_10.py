import os
import subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

pptx_path = r"C:\Users\sharv\barcode-test\Provenance_Client_Presentation.pptx"
logo_path = r"C:\Users\sharv\barcode-test\ui\provenance_logo.png"

# Ensure PowerPoint is closed
subprocess.run(["powershell", "-Command", "Stop-Process -Name POWERPNT -Force -ErrorAction SilentlyContinue"], capture_output=True)

prs = Presentation(pptx_path)
slide = prs.slides[9] # Slide 10 (0-indexed: 9)

def update_run_text(shape, paragraph_idx, text, font_size_pt=None):
    p = shape.text_frame.paragraphs[paragraph_idx]
    if p.runs:
        p.runs[0].text = text
        if font_size_pt:
            p.runs[0].font.size = Pt(font_size_pt)
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.text = text
        if font_size_pt:
            p.font.size = Pt(font_size_pt)

# 1. Update Action Cards (1, 2, 3)
# Action 01 (Shapes 13, 14, 15)
update_run_text(slide.shapes[13], 0, "15-Minute Bench Demo")
update_run_text(slide.shapes[14], 0, "Inspect the live 1080p camera view, automated barcode trigger, and instant dispute search on a live packing bench.")
update_run_text(slide.shapes[15], 0, "Schedule: Virtual or on-site walkthrough")

# Action 02 (Shapes 20, 21, 22)
update_run_text(slide.shapes[20], 0, "30-Day Single-Station Pilot")
update_run_text(slide.shapes[21], 0, "Deploy Provenance on your highest-volume packaging line with full hardware support and zero IT infrastructure overhaul.")
update_run_text(slide.shapes[22], 0, "Commitment: Zero-risk pilot evaluation")

# Action 03 (Shapes 27, 28, 29)
update_run_text(slide.shapes[27], 0, "Courier Evidence Review")
update_run_text(slide.shapes[28], 0, "Inspect sample video exports and tamper-evident packaging clips ready for Delhivery, Bluedart, and marketplace portals.")
update_run_text(slide.shapes[29], 0, "Deliverable: Complete sample evidence clip")

# 2. Update CTA Box (Shapes 30, 31, 32, 33)
# Expand width/position for text to leave room on right for Big Logo + Name
cta_card = slide.shapes[30]
cta_card.top = Inches(5.48)
cta_card.height = Inches(1.48)

# Left Side Text
t28 = slide.shapes[31] # Kicker
t28.top = Inches(5.62)
t28.left = Inches(1.00)
t28.width = Inches(7.50)
update_run_text(t28, 0, "READY TO ELIMINATE PACKING DISPUTE WRITE-OFFS?")

t29 = slide.shapes[32] # Title
t29.top = Inches(5.88)
t29.left = Inches(1.00)
t29.width = Inches(7.50)
update_run_text(t29, 0, "Book a Live Packing Bench Walkthrough", font_size_pt=20.0)

t30 = slide.shapes[33] # Contact
t30.top = Inches(6.38)
t30.left = Inches(1.00)
t30.width = Inches(7.50)
update_run_text(t30, 0, "miltronics@rediffmail.com   •   +91 98209 32930", font_size_pt=13.5)
# Ensure contact text is dark slate and bold for readability on white card
if t30.text_frame.paragraphs[0].runs:
    t30.text_frame.paragraphs[0].runs[0].font.bold = True
    t30.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

# Remove any previous added logo on slide 10 if exists
for s in list(slide.shapes):
    if s.name in ["Miltronics Big Logo", "Miltronics Big Name"]:
        sp_elem = s._element
        sp_elem.getparent().remove(sp_elem)

# 3. Add Big Logo & Name on the Right Side of CTA Card
# Logo at left=8.70, top=5.62, width=1.15, height=1.15
logo_pic = slide.shapes.add_picture(
    logo_path,
    Inches(8.75),
    Inches(5.65),
    width=Inches(1.15),
    height=Inches(1.15)
)
logo_pic.name = "Miltronics Big Logo"

# Text box alongside logo at left=10.05, top=5.65, width=2.45, height=1.15
name_box = slide.shapes.add_textbox(
    Inches(10.05),
    Inches(5.68),
    Inches(2.45),
    Inches(1.10)
)
name_box.name = "Miltronics Big Name"
tf = name_box.text_frame
tf.word_wrap = True
tf.margin_left = Inches(0)
tf.margin_top = Inches(0)
tf.margin_right = Inches(0)
tf.margin_bottom = Inches(0)

p1 = tf.paragraphs[0]
p1.text = "MILTRONICS"
p1.font.size = Pt(22.0)
p1.font.bold = True
p1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Dark obsidian

p2 = tf.add_paragraph()
p2.text = "PROVENANCE SUITE"
p2.font.size = Pt(11.0)
p2.font.bold = True
p2.font.color.rgb = RGBColor(0x05, 0x96, 0x69) # Emerald Green

p3 = tf.add_paragraph()
p3.text = "Automated Bench Systems"
p3.font.size = Pt(9.5)
p3.font.bold = False
p3.font.color.rgb = RGBColor(0x64, 0x74, 0x8B) # Muted slate

prs.save(pptx_path)
print("Slide 10 updated with Miltronics contact, big logo, and brand name")
