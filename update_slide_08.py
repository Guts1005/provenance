import os
import subprocess
from pptx import Presentation
from pptx.util import Pt

pptx_path = r"C:\Users\sharv\barcode-test\Provenance_Client_Presentation.pptx"

# Ensure PowerPoint is closed
subprocess.run(["powershell", "-Command", "Stop-Process -Name POWERPNT -Force -ErrorAction SilentlyContinue"], capture_output=True)

prs = Presentation(pptx_path)
slide = prs.slides[7] # Slide 8 (0-indexed: 7)

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

# Header & Subtitle
update_run_text(slide.shapes[7], 0, "Business Case")
update_run_text(slide.shapes[7], 1, "Direct Bottom-Line Financial Impact")
update_run_text(slide.shapes[8], 0, "Proven payback metrics across distribution centers and high-volume packing benches.")

# Hero Card (Left White Box)
update_run_text(slide.shapes[10], 0, "CAPITAL PAYBACK TIMELINE")
update_run_text(slide.shapes[11], 0, "< 90 Days", font_size_pt=54.0)
update_run_text(slide.shapes[12], 0, "Station investment typically recovered through reversed false claims within the first quarter of deployment.")

# Top Right Card 1 (Dispute Win Rate)
update_run_text(slide.shapes[14], 0, "82%")
update_run_text(slide.shapes[15], 0, "DISPUTE WIN RATE")
update_run_text(slide.shapes[16], 0, "Recovers over 80% of contested order value with indisputable packaging proof.")

# Top Right Card 2 (Faster Resolution)
update_run_text(slide.shapes[18], 0, "15x")
update_run_text(slide.shapes[19], 0, "FASTER RESOLUTION")
update_run_text(slide.shapes[20], 0, "Disputes investigated and closed in seconds instead of 28 minutes of manual CCTV scrubbing.")

# Table updates
tbl = slide.shapes[21].table

def update_cell_text(cell, text):
    p = cell.text_frame.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.text = text

update_cell_text(tbl.rows[0].cells[0], "OPERATIONAL VALUE DRIVER")
update_cell_text(tbl.rows[0].cells[1], "MEASURED IMPACT")

update_cell_text(tbl.rows[1].cells[0], "False Shortage Claims")
update_cell_text(tbl.rows[1].cells[1], "80%+ of contested value recovered")

update_cell_text(tbl.rows[2].cells[0], "CCTV Investigation Labor")
update_cell_text(tbl.rows[2].cells[1], "90%+ reduction in manual footage hunting")

update_cell_text(tbl.rows[3].cells[0], "Courier Dispute Liability")
update_cell_text(tbl.rows[3].cells[1], "Immediate sign-off with verified video proof")

update_cell_text(tbl.rows[4].cells[0], "Net Operational Impact")
update_cell_text(tbl.rows[4].cells[1], "Positive cash-flow from Month 1")

update_cell_text(tbl.rows[5].cells[0], "Capital Payback Horizon")
update_cell_text(tbl.rows[5].cells[1], "Under 60 to 90 days")

prs.save(pptx_path)
print("Slide 8 updated successfully in Provenance_Client_Presentation.pptx")
