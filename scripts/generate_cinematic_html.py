"""
Generate Dark Industrial HUD Cinematic HTML Presentation
Theme: Dark Industrial HUD & Terminal Precision
Synthesizes: Claude's Dark HUD aesthetic + Comprehensive Enterprise Technical Content.

RULES:
- Zero colored border ribbons on cards (Catalog K4). All borders 1px #262B35.
- Zero floating candy pill badges (Catalog K5).
- Strictly ZERO em-dashes across all code, HTML, CSS, text, and comments.
- 100% self-contained single-file HTML with embedded base64 placard asset.
- Content-tailored transitions matching PowerPoint delivery.
"""

import base64
import os

PLACARD_PATH = r"C:\Users\sharv\barcode-test\ui\finish_bench_placard.png"
LOGO_PATH = r"C:\Users\sharv\barcode-test\ui\provenance_logo.png"
OUTPUT_HTML = r"C:\Users\sharv\barcode-test\cinematic_presentation.html"

def get_placard_base64():
    if os.path.exists(PLACARD_PATH):
        with open(PLACARD_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    return ""

def get_logo_base64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    return ""

def generate_html():
    placard_src = get_placard_base64()
    logo_src = get_logo_base64()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Provenance: Industrial CCTV Proof &amp; Packing Station</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&family=Consolas:wght@400;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --canvas: #0F1117;
      --surface: #181B22;
      --surface-subtle: #12141B;
      --surface-card: #181B22;
      --line: #262B35;
      --line-strong: #374151;
      --ink: #FFFFFF;
      --ink-secondary: #9CA3AF;
      --ink-muted: #6B7280;
      --mint: #10B981;
      --mint-tint: rgba(16, 185, 129, 0.12);
      --red: #EF4444;
      --red-tint: rgba(239, 68, 68, 0.12);
      --blue: #3B82F6;
      --blue-tint: rgba(59, 130, 246, 0.12);
      --font-primary: "Segoe UI", -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
      --font-mono: Consolas, "Courier New", monospace;
      --ease-cinematic: cubic-bezier(0.16, 1, 0.3, 1);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--canvas);
      color: var(--ink);
      font-family: var(--font-primary);
      height: 100vh;
      height: 100dvh;
      overflow: hidden;
      user-select: none;
      -webkit-font-smoothing: antialiased;
    }}

    #deck-container {{
      position: relative;
      width: 100vw;
      height: 100vh;
      height: 100dvh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: var(--canvas);
    }}

    /* TOP HEADER & FLOW TRACKER */
    header.deck-header {{
      height: 56px;
      min-height: 56px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 40px;
      border-bottom: 1px solid var(--line);
      background: var(--surface);
      z-index: 100;
    }}

    .brand-section {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-label {{
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      color: var(--mint);
      letter-spacing: 0.08em;
    }}

    .brand-title {{
      font-size: 13px;
      font-weight: 600;
      color: var(--ink-secondary);
      letter-spacing: 0.02em;
    }}

    .flow-tracker {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .flow-box {{
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 600;
      padding: 5px 14px;
      border: 1px solid var(--line);
      background: var(--surface-subtle);
      color: var(--ink-muted);
      border-radius: 2px;
      cursor: pointer;
      transition: all 0.25s var(--ease-cinematic);
    }}

    .flow-box.active {{
      background: rgba(59, 130, 246, 0.15);
      color: var(--blue);
      font-weight: 700;
      border-color: rgba(59, 130, 246, 0.4);
    }}

    /* SLIDE VIEWPORT */
    main.slides-viewport {{
      flex: 1;
      position: relative;
      overflow: hidden;
      padding: 24px 40px 16px 40px;
    }}

    .slide {{
      position: absolute;
      top: 24px;
      bottom: 16px;
      left: 40px;
      right: 40px;
      display: flex;
      flex-direction: column;
      opacity: 0;
      pointer-events: none;
      visibility: hidden;
      transition: opacity 0.45s var(--ease-cinematic), transform 0.45s var(--ease-cinematic);
    }}

    .slide.active {{
      opacity: 1;
      pointer-events: auto;
      visibility: visible;
      transform: none !important;
    }}

    /* CONTENT-TAILORED TRANSITIONS */
    .slide-1:not(.active) {{ transform: scale(0.98); }}
    .slide-2:not(.active) {{ transform: translateX(40px); }}
    .slide-3:not(.active) {{ transform: scaleX(0.98); }}
    .slide-4:not(.active) {{ transform: translateX(35px); }}
    .slide-5:not(.active) {{ transform: translateX(45px); }}
    .slide-6:not(.active) {{ transform: translateY(40px); }}
    .slide-7:not(.active) {{ transform: translateX(35px); }}
    .slide-8:not(.active) {{ transform: scale(0.98); }}
    .slide-9:not(.active) {{ transform: translateX(40px); }}
    .slide-10:not(.active) {{ transform: scale(0.98); }}

    /* TYPOGRAPHY */
    .slide-header {{
      margin-bottom: 18px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 12px;
    }}

    .slide-meta {{
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 700;
      color: var(--mint);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}

    .slide-title {{
      font-size: clamp(24px, 2.6vw, 32px);
      font-weight: 700;
      color: var(--ink);
      line-height: 1.15;
      margin-bottom: 4px;
    }}

    .slide-subtitle {{
      font-size: clamp(12px, 1.1vw, 14.5px);
      color: var(--ink-secondary);
      line-height: 1.4;
    }}

    /* CARDS & UTILITIES */
    .card {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 2px;
      padding: 20px;
      position: relative;
    }}

    .card-subtle {{
      background: var(--surface-subtle);
      border: 1px solid var(--line);
      border-radius: 2px;
      padding: 20px;
    }}

    .mono-tag {{
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--ink-muted);
      text-transform: uppercase;
    }}

    .mono-metric {{
      font-family: var(--font-mono);
      font-weight: 700;
      letter-spacing: -0.02em;
    }}

    /* SLIDE 01: HERO & CAMERA HUD */
    .hero-grid {{
      display: grid;
      grid-template-columns: 1.1fr 1fr;
      gap: 28px;
      flex: 1;
      align-items: stretch;
    }}

    .hero-left {{
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .hero-heading {{
      font-size: clamp(32px, 3.8vw, 48px);
      font-weight: 700;
      line-height: 1.1;
      color: var(--ink);
      margin-bottom: 16px;
    }}

    .hero-desc {{
      font-size: 15px;
      color: var(--ink-secondary);
      line-height: 1.5;
      max-width: 90%;
    }}

    .hero-stats {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-top: 24px;
    }}

    .hero-stat-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 18px 16px;
      display: flex;
      flex-direction: column;
    }}

    .hero-stat-val {{
      font-family: var(--font-mono);
      font-size: clamp(24px, 2.4vw, 30px);
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }}

    .hero-stat-desc {{
      font-size: 11.5px;
      color: var(--ink-secondary);
      line-height: 1.35;
      margin-top: 8px;
    }}

    /* CAMERA VIEWFINDER HUD */
    .hud-box {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 24px;
      display: flex;
      flex-direction: column;
      position: relative;
    }}

    .hud-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      margin-bottom: 16px;
    }}

    .rec-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--red);
      animation: pulse-rec 1.5s infinite;
      display: inline-block;
    }}

    @keyframes pulse-rec {{
      0% {{ opacity: 1; }}
      50% {{ opacity: 0.3; }}
      100% {{ opacity: 1; }}
    }}

    .rec-label {{
      color: var(--red);
    }}

    .rig-status-label {{
      color: var(--red);
      margin-left: 8px;
    }}

    .viewfinder-frame {{
      flex: 1;
      border: 1px solid rgba(38, 43, 53, 0.8);
      background: var(--surface-subtle);
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 180px;
      margin-bottom: 20px;
    }}

    /* RETICLE CORNERS (NEON MINT) */
    .reticle-corner {{
      position: absolute;
      width: 24px;
      height: 24px;
      border-color: var(--mint);
      border-style: solid;
    }}
    .rc-tl {{ top: 12px; left: 12px; border-width: 2px 0 0 2px; }}
    .rc-tr {{ top: 12px; right: 12px; border-width: 2px 2px 0 0; }}
    .rc-bl {{ bottom: 12px; left: 12px; border-width: 0 0 2px 2px; }}
    .rc-br {{ bottom: 12px; right: 12px; border-width: 0 2px 2px 0; }}

    .bench-wireframe {{
      width: 60%;
      height: 55%;
      border: 1px solid rgba(59, 130, 246, 0.5);
      position: relative;
    }}

    .bench-inner-box {{
      width: 65%;
      height: 60%;
      position: absolute;
      top: -15%;
      left: 17.5%;
      border: 1px solid rgba(59, 130, 246, 0.8);
      background: rgba(18, 20, 27, 0.7);
    }}

    .telemetry-readout {{
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--ink-secondary);
      line-height: 1.8;
      border-top: 1px solid var(--line);
      padding-top: 14px;
    }}

    .telemetry-row {{
      display: flex;
      justify-content: space-between;
    }}

    .telemetry-key {{
      color: var(--ink-muted);
    }}

    .telemetry-val {{
      color: var(--ink);
    }}

    /* SLIDE 02: THE HIGH-COST REALITY */
    .top-two-stats {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }}

    .four-stages-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      flex: 1;
    }}

    .stage-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 20px 18px;
      display: flex;
      flex-direction: column;
    }}

    .stage-num {{
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      color: var(--ink);
    }}

    .stage-day {{
      font-family: var(--font-mono);
      font-size: 9.5px;
      color: var(--ink-muted);
      margin-top: 2px;
      margin-bottom: 12px;
    }}

    .stage-title {{
      font-size: 17px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 10px;
    }}

    .stage-desc {{
      font-size: 11.5px;
      color: var(--ink-secondary);
      line-height: 1.45;
      flex: 1;
    }}

    .stage-risk {{
      font-size: 11px;
      color: var(--red);
      margin-top: 14px;
      line-height: 1.35;
    }}

    /* SLIDE 03: COMPARISON MATRIX & BANNER */
    .matrix-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 16px 20px;
      margin-bottom: 20px;
      flex: 1;
      display: flex;
      flex-direction: column;
    }}

    .comparison-table {{
      width: 100%;
      border-collapse: collapse;
      flex: 1;
    }}

    .comparison-table th {{
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 700;
      color: var(--ink-muted);
      text-align: left;
      padding: 10px 14px;
      border-bottom: 1px solid var(--line);
      letter-spacing: 0.05em;
    }}

    .comparison-table td {{
      font-size: 12px;
      padding: 11px 14px;
      border-bottom: 1px solid rgba(38, 43, 53, 0.5);
    }}

    .comparison-table tr:last-child td {{
      border-bottom: none;
    }}

    .comparison-table tr:nth-child(even) {{
      background: rgba(18, 20, 27, 0.4);
    }}

    .comparison-table td.col-metric {{
      font-weight: 700;
      color: var(--ink);
      width: 22%;
    }}

    .comparison-table td.col-before {{
      color: var(--ink-secondary);
      width: 39%;
    }}

    .comparison-table td.col-after {{
      color: var(--ink);
      width: 39%;
    }}

    .comparison-table td.col-after.highlight {{
      color: var(--mint);
      font-weight: 600;
    }}

    .win-rate-banner {{
      background: var(--surface-subtle);
      border: 1px solid var(--line);
      padding: 18px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .win-rate-left {{
      display: flex;
      align-items: center;
      gap: 24px;
    }}

    .win-num {{
      font-family: var(--font-mono);
      font-size: 36px;
      font-weight: 700;
      line-height: 1;
    }}

    .win-num.red {{ color: var(--red); }}
    .win-num.mint {{ color: var(--mint); }}

    .win-tag {{
      font-family: var(--font-mono);
      font-size: 9px;
      font-weight: 700;
      color: var(--ink-muted);
      margin-top: 4px;
    }}

    .win-tag.mint {{ color: var(--mint); }}

    .win-arrow {{
      font-family: var(--font-mono);
      font-size: 24px;
      font-weight: 700;
      color: var(--line-strong);
    }}

    .win-rate-desc {{
      max-width: 45%;
      text-align: right;
    }}

    .win-rate-desc-title {{
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      color: var(--ink);
      letter-spacing: 0.05em;
      margin-bottom: 4px;
    }}

    .win-rate-desc-text {{
      font-size: 11.5px;
      color: var(--ink-secondary);
      line-height: 1.4;
    }}

    /* SLIDE 04: SUBSYSTEMS */
    .three-pillars-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      flex: 1;
    }}

    .pillar-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 24px 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .pillar-tag {{
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 700;
      color: var(--ink-muted);
      margin-bottom: 6px;
    }}

    .pillar-title {{
      font-size: 19px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 10px;
    }}

    .pillar-lead {{
      font-size: 12px;
      color: var(--ink-secondary);
      line-height: 1.45;
      margin-bottom: 14px;
    }}

    .pillar-bullets {{
      list-style: none;
      margin-bottom: 20px;
    }}

    .pillar-bullets li {{
      font-size: 11.5px;
      color: var(--ink-secondary);
      line-height: 1.4;
      margin-bottom: 8px;
      display: flex;
      align-items: baseline;
      gap: 8px;
    }}

    .pillar-bullets li::before {{
      content: "›";
      color: var(--mint);
      font-family: var(--font-mono);
      font-weight: 700;
    }}

    .pillar-metric {{
      font-family: var(--font-mono);
      font-size: 26px;
      font-weight: 700;
      color: var(--mint);
      line-height: 1;
    }}

    .pillar-metric-lbl {{
      font-family: var(--font-mono);
      font-size: 9px;
      font-weight: 700;
      color: var(--ink-muted);
      margin-top: 4px;
    }}

    /* SLIDE 05: OPERATOR WORKFLOW */
    .workflow-layout {{
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 22px;
      flex: 1;
    }}

    .steps-stack {{
      display: flex;
      flex-direction: column;
      gap: 14px;
      justify-content: space-between;
    }}

    .step-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 18px 22px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 18px;
    }}

    .step-info {{
      flex: 1;
    }}

    .step-title {{
      font-size: 16px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 6px;
    }}

    .step-desc {{
      font-size: 11.5px;
      color: var(--ink-secondary);
      line-height: 1.4;
    }}

    .step-metric {{
      text-align: right;
      min-width: 80px;
    }}

    .step-val {{
      font-family: var(--font-mono);
      font-size: 18px;
      font-weight: 700;
      color: var(--mint);
    }}

    .step-lbl {{
      font-family: var(--font-mono);
      font-size: 8.5px;
      color: var(--ink-muted);
      margin-top: 2px;
    }}

    .placard-card {{
      background: var(--surface-subtle);
      border: 1px solid var(--line);
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .placard-img {{
      width: 100%;
      border-radius: 2px;
      border: 1px solid var(--line);
      margin: 12px 0;
    }}

    .placard-desc {{
      font-size: 11.5px;
      color: var(--ink-secondary);
      line-height: 1.4;
    }}

    .placard-callout {{
      font-family: var(--font-mono);
      font-size: 11.5px;
      font-weight: 700;
      color: var(--mint);
      letter-spacing: 0.05em;
      margin-top: 8px;
    }}

    /* SLIDE 06: ARCHITECTURE TIERS */
    .tier-stack {{
      display: flex;
      flex-direction: column;
      gap: 16px;
      flex: 1;
      justify-content: space-between;
    }}

    .tier-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 22px 26px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 24px;
    }}

    .tier-content {{
      flex: 1;
    }}

    .tier-title {{
      font-size: 17px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 6px;
    }}

    .tier-desc {{
      font-size: 12px;
      color: var(--ink-secondary);
      line-height: 1.45;
    }}

    .tier-metric {{
      text-align: right;
      min-width: 140px;
    }}

    .tier-val {{
      font-family: var(--font-mono);
      font-size: 22px;
      font-weight: 700;
      color: var(--mint);
    }}

    .tier-lbl {{
      font-family: var(--font-mono);
      font-size: 9px;
      color: var(--ink-muted);
      margin-top: 3px;
    }}

    /* SLIDE 07: HARDWARE SPECS */
    .hardware-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      flex: 1;
    }}

    .hw-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 22px 18px;
      display: flex;
      flex-direction: column;
    }}

    .hw-badge {{
      font-family: var(--font-mono);
      font-size: 36px;
      font-weight: 700;
      color: var(--ink);
      margin: 6px 0 16px 0;
      line-height: 1;
    }}

    .hw-specs {{
      list-style: none;
    }}

    .hw-specs li {{
      font-size: 11.5px;
      color: var(--ink-secondary);
      line-height: 1.4;
      margin-bottom: 8px;
      display: flex;
      align-items: baseline;
      gap: 8px;
    }}

    .hw-specs li::before {{
      content: "›";
      color: var(--mint);
      font-family: var(--font-mono);
      font-weight: 700;
    }}

    /* SLIDE 08: BUSINESS CASE */
    .roi-top-stats {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 20px;
    }}

    .roi-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 20px;
      display: flex;
      flex-direction: column;
    }}

    .roi-val {{
      font-family: var(--font-mono);
      font-size: 36px;
      font-weight: 700;
      line-height: 1;
      margin-bottom: 6px;
    }}

    .roi-val.mint {{ color: var(--mint); }}
    .roi-val.white {{ color: var(--ink); }}
    .roi-val.blue {{ color: var(--blue); }}

    .roi-table-card {{
      background: var(--surface-subtle);
      border: 1px solid var(--line);
      padding: 16px 24px;
      flex: 1;
      display: flex;
      flex-direction: column;
    }}

    .payback-table {{
      width: 100%;
      border-collapse: collapse;
      flex: 1;
    }}

    .payback-table th {{
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 700;
      color: var(--ink-muted);
      padding: 8px 12px;
      border-bottom: 1px solid var(--line);
      letter-spacing: 0.05em;
    }}

    .payback-table td {{
      font-size: 12px;
      padding: 9px 12px;
      border-bottom: 1px solid rgba(38, 43, 53, 0.5);
    }}

    .payback-table tr:last-child td {{
      border-bottom: none;
    }}

    .payback-table td.col-right {{
      text-align: right;
      font-family: var(--font-mono);
      font-size: 12.5px;
      font-weight: 700;
    }}

    .payback-table tr.total-row td {{
      font-weight: 700;
      color: var(--mint) !important;
    }}

    /* SLIDE 09: ROADMAP */
    .roadmap-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      flex: 1;
    }}

    .rm-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 22px 18px;
      display: flex;
      flex-direction: column;
    }}

    .rm-week {{
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      color: var(--mint);
      margin-bottom: 6px;
    }}

    .rm-title {{
      font-size: 16px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 16px;
    }}

    .rm-tasks {{
      list-style: none;
    }}

    .rm-tasks li {{
      font-size: 11.5px;
      color: var(--ink-secondary);
      line-height: 1.4;
      margin-bottom: 8px;
      display: flex;
      align-items: baseline;
      gap: 8px;
    }}

    .rm-tasks li::before {{
      content: "›";
      color: var(--mint);
      font-family: var(--font-mono);
      font-weight: 700;
    }}

    /* SLIDE 10: ACTION PLAN */
    .action-top-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 20px;
    }}

    .action-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 24px 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .action-tag {{
      font-family: var(--font-mono);
      font-size: 10.5px;
      font-weight: 700;
      color: var(--mint);
      margin-bottom: 6px;
    }}

    .action-title {{
      font-size: 18px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 10px;
    }}

    .action-desc {{
      font-size: 12px;
      color: var(--ink-secondary);
      line-height: 1.45;
      margin-bottom: 16px;
    }}

    .action-meta {{
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--ink-muted);
      border-top: 1px solid rgba(38, 43, 53, 0.6);
      padding-top: 10px;
    }}

    .exec-callout-banner {{
      background: var(--surface-subtle);
      border: 1px solid var(--line);
      padding: 26px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }}

    .exec-kicker {{
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      color: var(--mint);
      letter-spacing: 0.08em;
    }}

    .exec-headline {{
      font-size: clamp(22px, 2.3vw, 28px);
      font-weight: 700;
      color: var(--ink);
    }}

    .exec-contact {{
      font-family: var(--font-mono);
      font-size: 14px;
      color: var(--ink-secondary);
      margin-top: 4px;
    }}

    /* BOTTOM CONTROLS & FOOTER */
    footer.deck-footer {{
      height: 48px;
      min-height: 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 40px;
      border-top: 1px solid var(--line);
      background: var(--surface);
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--ink-muted);
      z-index: 100;
    }}

    .nav-buttons {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .nav-btn {{
      background: var(--surface-subtle);
      border: 1px solid var(--line);
      color: var(--ink);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 600;
      padding: 6px 14px;
      border-radius: 2px;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .nav-btn:hover {{
      background: rgba(59, 130, 246, 0.15);
      border-color: var(--blue);
      color: var(--ink);
    }}

    .slide-dots {{
      display: flex;
      gap: 6px;
    }}

    .dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--line-strong);
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .dot.active {{
      background: var(--mint);
      transform: scale(1.2);
    }}
  </style>
</head>
<body>
  <div id="deck-container">
    <!-- TOP HEADER -->
    <header class="deck-header">
      <div class="brand-section">
        <img src="{logo_src}" alt="Provenance Logo" style="width: 22px; height: 22px; object-fit: contain; margin-right: 8px;">
        <span class="brand-label">PROVENANCE</span>
        <span class="brand-title" style="color: var(--mint); margin-left: 8px;">•  AUTOMATED PACKING SURVEILLANCE</span>
      </div>
      <div class="flow-tracker">
        <div class="flow-box active" onclick="goToSlide(1)">01 PROBLEM</div>
        <div class="flow-box" onclick="goToSlide(4)">02 SOLUTION</div>
        <div class="flow-box" onclick="goToSlide(7)">03 OPERATIONS</div>
        <div class="flow-box" onclick="goToSlide(9)">04 DEPLOYMENT</div>
      </div>
    </header>

    <!-- SLIDES VIEWPORT -->
    <main class="slides-viewport">
      <!-- SLIDE 01: HERO OPENING & PACKING STATION CAMERA HUD -->
      <section class="slide slide-1 active" id="slide-1">
        <div class="hero-grid">
          <div class="hero-left">
            <div>
              <div class="slide-meta" style="display: flex; align-items: center; gap: 8px;">
                <img src="{logo_src}" alt="Provenance" style="width: 18px; height: 18px; object-fit: contain;">
                <span>PROVENANCE  •  AUTOMATED PACKING SURVEILLANCE</span>
              </div>
              <h1 class="hero-heading">Automated CCTV Evidence &amp;<br>Packing Station Verification</h1>
              <p class="hero-desc">Instant camera proof for every parcel leaving your facility. Records automatically from your existing barcode scan with zero worker delay.</p>
            </div>
            <div class="hero-stats">
              <div class="hero-stat-card">
                <div class="hero-stat-val">1080p FHD</div>
                <div class="mono-tag" style="color: var(--mint);">ADAPTIVE VISION</div>
                <div class="hero-stat-desc">Overhead camera optimized for changing warehouse lighting and glare from packing tape.</div>
              </div>
              <div class="hero-stat-card">
                <div class="hero-stat-val">0 Clicks</div>
                <div class="mono-tag" style="color: var(--blue);">ZERO WORKER FRICTION</div>
                <div class="hero-stat-desc">Triggers automatically on barcode scan. Packers never touch a keyboard or mouse.</div>
              </div>
              <div class="hero-stat-card">
                <div class="hero-stat-val">&lt; 2s</div>
                <div class="mono-tag" style="color: var(--mint);">INSTANT EVIDENCE</div>
                <div class="hero-stat-desc">Search by tracking number to pull packing video proof and resolve claims immediately.</div>
              </div>
            </div>
          </div>

          <div class="hud-box">
            <div class="hud-header">
              <span class="rec-dot"></span>
              <span class="rec-label">REC</span>
              <span class="rig-status-label" style="color: var(--red);">STATION FEED</span>
              <span style="color: var(--ink-muted); margin-left: auto; font-size: 10px;">LIVE OVERHEAD VIEW</span>
            </div>
            <div class="viewfinder-frame">
              <div class="reticle-corner rc-tl"></div>
              <div class="reticle-corner rc-tr"></div>
              <div class="reticle-corner rc-bl"></div>
              <div class="reticle-corner rc-br"></div>
              <div class="bench-wireframe">
                <div class="bench-inner-box"></div>
              </div>
              <div style="position: absolute; top: 14px; left: 16px; font-family: var(--font-mono); font-size: 10px; font-weight: 700; color: var(--mint);">BENCH 01 ACTIVE</div>
            </div>
            <div class="telemetry-readout">
              <div class="telemetry-row"><span class="telemetry-key">Camera Sensor</span><span class="telemetry-val">1080p Full HD Industrial</span></div>
              <div class="telemetry-row"><span class="telemetry-key">Lighting Control</span><span class="telemetry-val">Dynamic anti-glare optimization</span></div>
              <div class="telemetry-row"><span class="telemetry-key">Pre-Roll Buffer</span><span class="telemetry-val">5-second continuous buffer</span></div>
              <div class="telemetry-row"><span class="telemetry-key">Capture Trigger</span><span class="telemetry-val">Standard barcode scan</span></div>
              <div class="telemetry-row"><span class="telemetry-key">Data Storage</span><span class="telemetry-val">Secure local station database</span></div>
            </div>
          </div>
        </div>
      </section>

      <!-- SLIDE 02: THE SURVEILLANCE GAP -->
      <section class="slide slide-2" id="slide-2">
        <div class="slide-header">
          <div class="slide-meta">SURVEILLANCE GAP</div>
          <h2 class="slide-title">Why Traditional Warehouse CCTV Fails to Protect Packaging Lines</h2>
          <p class="slide-subtitle">Ceiling security cameras monitor facility safety, not individual orders. When customer or courier claims arise, finding conclusive proof is nearly impossible.</p>
        </div>
        <div class="top-two-stats">
          <div class="card">
            <div class="mono-metric" style="font-size: 30px; color: var(--red); line-height: 1;">28 Mins</div>
            <div class="mono-tag" style="margin-top: 6px;">AVERAGE TIME TO SEARCH ONE DISPUTED ORDER</div>
          </div>
          <div class="card">
            <div class="mono-metric" style="font-size: 28px; color: var(--red); line-height: 1;">Rs 3,500 to Rs 15,000</div>
            <div class="mono-tag" style="margin-top: 6px;">AVERAGE LOSS PER CONTESTED SHIPMENT</div>
          </div>
        </div>
        <div class="four-stages-grid">
          <div class="stage-card">
            <div class="stage-num">FAILURE 01</div>
            <div class="stage-day">OBSTRUCTED VIEW</div>
            <div class="stage-title">Angle &amp; Blind Spots</div>
            <div class="stage-desc">Ceiling cameras mount 20 feet above and film workers from behind. The packer's shoulders block the box contents at tape down.</div>
            <div class="stage-risk">Zero visual proof of items inside the box.</div>
          </div>
          <div class="stage-card">
            <div class="stage-num">FAILURE 02</div>
            <div class="stage-day">UNINDEXED FOOTAGE</div>
            <div class="stage-title">No Barcode Linking</div>
            <div class="stage-desc">Footage is organized only by time of day, not tracking number. Finding one parcel among thousands of daily dispatches is pure guesswork.</div>
            <div class="stage-risk">Manual scrubbing wastes hours of manager time.</div>
          </div>
          <div class="stage-card">
            <div class="stage-num">FAILURE 03</div>
            <div class="stage-day">LIGHTING &amp; REFLECTION</div>
            <div class="stage-title">Tape Glare &amp; Blur</div>
            <div class="stage-desc">Warehouse tube lights reflect off clear packing tape. Standard security lenses blow out details and blur shipping label text.</div>
            <div class="stage-risk">Label barcodes and serial numbers are unreadable.</div>
          </div>
          <div class="stage-card">
            <div class="stage-num">FAILURE 04</div>
            <div class="stage-day">CLAIM FORFEIT</div>
            <div class="stage-title">Dispute Rejection</div>
            <div class="stage-desc">Carriers and marketplaces reject blurry wide-angle ceiling clips. Without bench-level proof, merchants are forced to pay out the claim.</div>
            <div class="stage-risk">100% of contested order value is written off.</div>
          </div>
        </div>
      </section>

      <!-- SLIDE 03: BEFORE VS AFTER TRANSFORMATION -->
      <section class="slide slide-3" id="slide-3">
        <div class="slide-header">
          <div class="slide-meta">TRANSFORMATION ANALYSIS</div>
          <h2 class="slide-title">Operational Shift: Blind Bench vs Cryptographic Proof</h2>
          <p class="slide-subtitle">Comparison of legacy manual CCTV workflows against automated Provenance edge recording.</p>
        </div>
        <div class="matrix-card">
          <table class="comparison-table">
            <thead>
              <tr>
                <th>METRIC</th>
                <th>BEFORE: BLIND DISPATCHES</th>
                <th>AFTER: CRYPTOGRAPHIC PROOF</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="col-metric">Search Time</td>
                <td class="col-before">28 min manual CCTV scrub across channels</td>
                <td class="col-after">Sub-2s instant query by barcode number</td>
              </tr>
              <tr>
                <td class="col-metric">Clock Drift</td>
                <td class="col-before">NTP drift between PC and overhead camera</td>
                <td class="col-after">Hardware timestamp lock at video trigger</td>
              </tr>
              <tr>
                <td class="col-metric">Pre-Scan Footage</td>
                <td class="col-before">Zero pre-roll buffer (item placement lost)</td>
                <td class="col-after">5-second circular RAM pre-roll buffer</td>
              </tr>
              <tr>
                <td class="col-metric">Evidence Integrity</td>
                <td class="col-before">Subjective word against word</td>
                <td class="col-after">SHA-256 cryptographic hash signature</td>
              </tr>
              <tr>
                <td class="col-metric">Dispute Win Rate</td>
                <td class="col-before">18% dispute recovery rate (82% lost)</td>
                <td class="col-after highlight">82% verified dispute win rate</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="win-rate-banner">
          <div class="win-rate-left">
            <div>
              <div class="win-num red">18%</div>
              <div class="win-tag">UNVERIFIED</div>
            </div>
            <div class="win-arrow">-----></div>
            <div>
              <div class="win-num mint">82%</div>
              <div class="win-tag mint">WITH PROVENANCE</div>
            </div>
          </div>
          <div class="win-rate-desc">
            <div class="win-rate-desc-title">DISPUTE WIN RATE TRANSFORMATION</div>
            <div class="win-rate-desc-text">Cryptographic proof delivered in under 90 seconds reverses false shortage claims with immediate carrier sign-off.</div>
          </div>
        </div>
      </section>

      <!-- SLIDE 04: PLATFORM SUBSYSTEMS -->
      <section class="slide slide-4" id="slide-4">
        <div class="slide-header">
          <div class="slide-meta">SYSTEM ENGINEERING</div>
          <h2 class="slide-title">The Solution: Automated Bench Chain-of-Custody</h2>
          <p class="slide-subtitle">Autonomous edge recording daemon engineered specifically for warehouse packing bench ergonomics.</p>
        </div>
        <div class="three-pillars-grid">
          <div class="pillar-card">
            <div>
              <div class="pillar-tag">SUBSYSTEM 01</div>
              <h3 class="pillar-title">Sub-50ms Keystroke Trigger</h3>
              <p class="pillar-lead">Background USB parser listens for the rapid barcode scanner keystroke burst. Zero mouse clicks, zero keyboard typing required.</p>
              <ul class="pillar-bullets">
                <li>Hardware-level keystroke parser (&lt; 50ms latency)</li>
                <li>Runs entirely in background without window focus</li>
                <li>Compatible with all 2D USB &amp; Bluetooth scanners</li>
                <li>Zero disruption to high-speed packing flow</li>
              </ul>
            </div>
            <div>
              <div class="pillar-metric">&lt; 50ms</div>
              <div class="pillar-metric-lbl">TRIGGER LATENCY</div>
            </div>
          </div>

          <div class="pillar-card">
            <div>
              <div class="pillar-tag">SUBSYSTEM 02</div>
              <h3 class="pillar-title">5-Second Rolling Pre-Roll Buffer</h3>
              <p class="pillar-lead">Circular uncompressed RAM ring holds the last 5 seconds, so 100% of pre-scan box placement is captured automatically.</p>
              <ul class="pillar-bullets">
                <li>Captures item pickup before barcode scan occurs</li>
                <li>Seamlessly prepends buffer frames to cut</li>
                <li>High-throughput OpenCV RTSP memory engine</li>
                <li>Zero storage write wear during standby ring</li>
              </ul>
            </div>
            <div>
              <div class="pillar-metric">5 SEC</div>
              <div class="pillar-metric-lbl">ROLLING PRE-ROLL</div>
            </div>
          </div>

          <div class="pillar-card">
            <div>
              <div class="pillar-tag">SUBSYSTEM 03</div>
              <h3 class="pillar-title">SHA-256 Tamper-Proof Stamp</h3>
              <p class="pillar-lead">Cryptographic signature tied to hardware ID, NTP timestamp, and barcode metadata. Stored in a local SQLite database.</p>
              <ul class="pillar-bullets">
                <li>SHA-256 signature calculated at recording finish</li>
                <li>Station ID and millisecond timestamp stamped</li>
                <li>Local SQLite database ensures instant sub-2s query</li>
                <li>Admissible in formal carrier and legal disputes</li>
              </ul>
            </div>
            <div>
              <div class="pillar-metric">SHA-256</div>
              <div class="pillar-metric-lbl">TAMPER-PROOF STAMP</div>
            </div>
          </div>
        </div>
      </section>

      <!-- SLIDE 05: OPERATOR WORKFLOW -->
      <section class="slide slide-5" id="slide-5">
        <div class="slide-header">
          <div class="slide-meta">PACKING BENCH ERGONOMICS</div>
          <h2 class="slide-title">Operator Bench Flow: Three-Step Zero-Click Cycle</h2>
          <p class="slide-subtitle">Operators never touch a mouse or switch applications. All actions trigger via physical barcodes.</p>
        </div>
        <div class="workflow-layout">
          <div class="steps-stack">
            <div class="step-card">
              <div class="step-info">
                <div class="step-title">STEP 01 // Scan Barcode</div>
                <div class="step-desc">Operator scans shipping label or product barcode with handheld scanner. System detects burst and locks pre-roll buffer.</div>
              </div>
              <div class="step-metric">
                <div class="step-val">0.2s</div>
                <div class="step-lbl">DURATION</div>
              </div>
            </div>

            <div class="step-card">
              <div class="step-info">
                <div class="step-title">STEP 02 // Pack &amp; Seal Parcel</div>
                <div class="step-desc">Overhead 4K camera records continuously while the operator packs. Real-time visual indicator confirms active recording.</div>
              </div>
              <div class="step-metric">
                <div class="step-val">NATURAL</div>
                <div class="step-lbl">DURATION</div>
              </div>
            </div>

            <div class="step-card">
              <div class="step-info">
                <div class="step-title">STEP 03 // Scan Finish Placard</div>
                <div class="step-desc">Operator scans physical bench finish placard. Recording halts, encodes with hardware H.264, and indexes instantly.</div>
              </div>
              <div class="step-metric">
                <div class="step-val">0.1s</div>
                <div class="step-lbl">DURATION</div>
              </div>
            </div>
          </div>

          <div class="placard-card">
            <div>
              <div class="mono-tag">BENCH FINISH PLACARD // RIGID ACRYLIC</div>
              <img src="{placard_src}" alt="Bench Finish Placard" class="placard-img">
              <div class="placard-desc">A physical barcode placard sits on the packing table within easy reach. One scan seals, encodes, hashes, and indexes the clip.</div>
            </div>
            <div class="placard-callout">NO MOUSE. NO KEYBOARD. NO WINDOW SWITCHING.</div>
          </div>
        </div>
      </section>

      <!-- SLIDE 06: TECHNICAL ARCHITECTURE -->
      <section class="slide slide-6" id="slide-6">
        <div class="slide-header">
          <div class="slide-meta">ENGINEERING ARCHITECTURE</div>
          <h2 class="slide-title">Technical Architecture: Local-First Core</h2>
          <p class="slide-subtitle">Designed to operate continuously on local hardware even during warehouse internet outages.</p>
        </div>
        <div class="tier-stack">
          <div class="tier-card">
            <div class="tier-content">
              <div class="tier-title">TIER 03 // Dispute &amp; Claims Portal</div>
              <div class="tier-desc">Sub-2s barcode search. Each claim generates a self-contained MP4 video evidence package plus cryptographic SHA-256 JSON verification record for courier portals.</div>
            </div>
            <div class="tier-metric">
              <div class="tier-val">Sub-2s</div>
              <div class="tier-lbl">BARCODE SEARCH</div>
            </div>
          </div>

          <div class="tier-card">
            <div class="tier-content">
              <div class="tier-title">TIER 02 // Station Edge Daemon</div>
              <div class="tier-desc">Local-first Python OS service with a sub-50ms scanner event bus, circular OpenCV memory buffer, and local SQLite database for instant retrieval.</div>
            </div>
            <div class="tier-metric">
              <div class="tier-val">Sub-50ms</div>
              <div class="tier-lbl">EVENT BUS</div>
            </div>
          </div>

          <div class="tier-card">
            <div class="tier-content">
              <div class="tier-title">TIER 01 // Hardware Bench Rig</div>
              <div class="tier-desc">Overhead 4K camera with 120-degree FOV, 2D industrial barcode scanner in USB HID keystroke mode, bi-color LED beacon, and 85dB directional audio buzzer.</div>
            </div>
            <div class="tier-metric">
              <div class="tier-val">4K UHD</div>
              <div class="tier-lbl">OVERHEAD CAMERA</div>
            </div>
          </div>
        </div>
      </section>

      <!-- SLIDE 07: HARDWARE SPECIFICATIONS -->
      <section class="slide slide-7" id="slide-7">
        <div class="slide-header">
          <div class="slide-meta">BENCH EQUIPMENT</div>
          <h2 class="slide-title">Hardware Specifications: Engineered for Industrial Duty</h2>
          <p class="slide-subtitle">Rigid industrial components rated for dust, continuous vibration, and 24/7 warehouse operations.</p>
        </div>
        <div class="hardware-grid">
          <div class="hw-card">
            <div class="mono-tag">01 // OVERHEAD CAM</div>
            <div class="hw-badge">4K</div>
            <ul class="hw-specs">
              <li>4K UHD (3840x2160)</li>
              <li>60fps smooth capture</li>
              <li>120-degree wide FOV</li>
              <li>f/1.8 low-light sensor</li>
              <li>Articulated boom arm</li>
            </ul>
          </div>

          <div class="hw-card">
            <div class="mono-tag">02 // 2D SCANNER</div>
            <div class="hw-badge">IP65</div>
            <ul class="hw-specs">
              <li>IP65 rated casing</li>
              <li>2.0m drop spec</li>
              <li>USB 3.0 / Bluetooth 5.2</li>
              <li>Rapid keystroke profile</li>
              <li>Instant read on torn labels</li>
            </ul>
          </div>

          <div class="hw-card">
            <div class="mono-tag">03 // EDGE PC</div>
            <div class="hw-badge">16GB</div>
            <ul class="hw-specs">
              <li>Fanless aluminum casing</li>
              <li>Intel Quad-Core N100/i3</li>
              <li>16GB DDR5 Industrial RAM</li>
              <li>Dual 1TB NVMe Solid State</li>
              <li>Auto 90-day retention loop</li>
            </ul>
          </div>

          <div class="hw-card">
            <div class="mono-tag">04 // BEACON</div>
            <div class="hw-badge">85dB</div>
            <ul class="hw-specs">
              <li>Bi-color green/red LED</li>
              <li>85dB directional buzzer</li>
              <li>Start/stop sound tones</li>
              <li>Overhead eye-level mount</li>
              <li>Rigid acrylic bench placard</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- SLIDE 08: BUSINESS CASE & ROI -->
      <section class="slide slide-8" id="slide-8">
        <div class="slide-header">
          <div class="slide-meta">MEASURABLE VALUE</div>
          <h2 class="slide-title">Business Case: Direct Bottom-Line Financial Impact</h2>
          <p class="slide-subtitle">Proven payback metrics across pilot distribution centers and packaging benches.</p>
        </div>
        <div class="roi-top-stats">
          <div class="roi-card">
            <div class="roi-val mint">82%</div>
            <div class="mono-tag">DISPUTE WIN RATE</div>
            <div class="stage-desc" style="margin-top: 6px;">Recovers 82% of contested merchandise value via courier proof.</div>
          </div>
          <div class="roi-card">
            <div class="roi-val white">4.2x</div>
            <div class="mono-tag">FASTER INVESTIGATIONS</div>
            <div class="stage-desc" style="margin-top: 6px;">Claims resolved in under 90 seconds instead of 28 minutes.</div>
          </div>
          <div class="roi-card">
            <div class="roi-val blue">$48,000</div>
            <div class="mono-tag">ANNUAL SAVINGS PER 10 BENCHES</div>
            <div class="stage-desc" style="margin-top: 6px;">Net savings per 10 packaging benches deployed.</div>
          </div>
        </div>
        <div class="roi-table-card">
          <table class="payback-table">
            <thead>
              <tr>
                <th style="text-align: left;">FINANCIAL PAYBACK MODEL</th>
                <th style="text-align: right;">ANNUAL, PER 10 BENCHES</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Write-off recovery</td>
                <td class="col-right">$32,400</td>
              </tr>
              <tr>
                <td>Labor reduction</td>
                <td class="col-right">$11,200</td>
              </tr>
              <tr>
                <td>Carrier surcharge avoidance</td>
                <td class="col-right">$4,400</td>
              </tr>
              <tr class="total-row">
                <td>Total annual savings</td>
                <td class="col-right">$48,000</td>
              </tr>
              <tr class="total-row">
                <td>Full payback</td>
                <td class="col-right">Under 90 days</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- SLIDE 09: ROADMAP -->
      <section class="slide slide-9" id="slide-9">
        <div class="slide-header">
          <div class="slide-meta">IMPLEMENTATION SCHEDULE</div>
          <h2 class="slide-title">4-Week Deployment Roadmap: Zero Downtime</h2>
          <p class="slide-subtitle">Turnkey implementation designed to fit seamlessly into active packing bench operations.</p>
        </div>
        <div class="roadmap-grid">
          <div class="rm-card">
            <div class="rm-week">WEEK 01</div>
            <div class="rm-title">Bench Audit &amp; Rigging</div>
            <ul class="rm-tasks">
              <li>Camera boom mount</li>
              <li>Scanner latency calibration</li>
              <li>Packing table FOV audit</li>
              <li>Power and cable delivery</li>
            </ul>
          </div>

          <div class="rm-card">
            <div class="rm-week">WEEK 02</div>
            <div class="rm-title">Station Pilot Launch</div>
            <ul class="rm-tasks">
              <li>Single bench activation</li>
              <li>5s buffer validation</li>
              <li>Operator observation</li>
              <li>Local storage retention loop</li>
            </ul>
          </div>

          <div class="rm-card">
            <div class="rm-week">WEEK 03</div>
            <div class="rm-title">Full Facility Expansion</div>
            <ul class="rm-tasks">
              <li>Multi-bench rollout</li>
              <li>NAS storage sync</li>
              <li>Claims team portal training</li>
              <li>Dispute workflow sign-off</li>
            </ul>
          </div>

          <div class="rm-card">
            <div class="rm-week">WEEK 04</div>
            <div class="rm-title">WMS / ERP Cutover</div>
            <ul class="rm-tasks">
              <li>WMS barcode API sync</li>
              <li>Automated courier export</li>
              <li>Executive metrics sign-off</li>
              <li>Full production cutover</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- SLIDE 10: ACTION PLAN -->
      <section class="slide slide-10" id="slide-10">
        <div class="slide-header">
          <div class="slide-meta">EXECUTIVE ACTION PLAN</div>
          <h2 class="slide-title">Transform Packing Bench Accountability</h2>
          <p class="slide-subtitle">Turn every dispatch into indisputable evidence with zero operator overhead.</p>
        </div>
        <div class="action-top-grid">
          <div class="action-card">
            <div>
              <div class="action-tag">ACTION 01</div>
              <div class="action-title">15-Minute Bench Demo</div>
              <div class="action-desc">Inspect the live camera angle, sub-50ms keystroke trigger, and instant search portal on a live test packing bench.</div>
            </div>
            <div class="action-meta">Schedule: Virtual or on-site walkthrough</div>
          </div>

          <div class="action-card">
            <div>
              <div class="action-tag">ACTION 02</div>
              <div class="action-title">30-Day Single-Station Pilot</div>
              <div class="action-desc">Deploy Provenance on your highest-volume packaging line with full hardware support and zero IT infrastructure overhaul.</div>
            </div>
            <div class="action-meta">Commitment: Zero-risk pilot evaluation</div>
          </div>

          <div class="action-card">
            <div>
              <div class="action-tag">ACTION 03</div>
              <div class="action-title">Sample Dispute Bundle Inspection</div>
              <div class="action-desc">Review the exportable dispute package, SHA-256 hash signature, and carrier-ready documentation format.</div>
            </div>
            <div class="action-meta">Deliverable: Complete evidence package</div>
          </div>
        </div>
        <div class="exec-callout-banner">
          <div class="exec-kicker">READY TO ELIMINATE PACKING DISPUTE WRITE-OFFS?</div>
          <div class="exec-headline">Book a 15-Minute Live Packing Bench Walkthrough</div>
          <div class="exec-contact">sales@provenance-systems.com &nbsp;|&nbsp; +1 (800) 555-PACK</div>
        </div>
      </section>
    </main>

    <!-- BOTTOM CONTROLS & FOOTER -->
    <footer class="deck-footer">
      <div>PROVENANCE STATION SUITE</div>
      <div class="nav-buttons">
        <button class="nav-btn" onclick="prevSlide()">&lt; PREV</button>
        <div class="slide-dots" id="slide-dots">
          <!-- Dots generated via JS -->
        </div>
        <button class="nav-btn" onclick="nextSlide()">NEXT &gt;</button>
      </div>
      <div>
        <span id="slide-counter">01 of 10</span> &nbsp;|&nbsp; Arrow Keys Navigate
      </div>
    </footer>
  </div>

  <script>
    let currentSlide = 1;
    const totalSlides = 10;

    const phaseMap = [
      {{ slide: 1, phase: 0 }},
      {{ slide: 2, phase: 0 }},
      {{ slide: 3, phase: 0 }},
      {{ slide: 4, phase: 1 }},
      {{ slide: 5, phase: 1 }},
      {{ slide: 6, phase: 1 }},
      {{ slide: 7, phase: 2 }},
      {{ slide: 8, phase: 2 }},
      {{ slide: 9, phase: 3 }},
      {{ slide: 10, phase: 3 }}
    ];

    function initDots() {{
      const container = document.getElementById("slide-dots");
      container.innerHTML = "";
      for (let i = 1; i <= totalSlides; i++) {{
        const dot = document.createElement("div");
        dot.className = "dot" + (i === 1 ? " active" : "");
        dot.onclick = () => goToSlide(i);
        container.appendChild(dot);
      }}
    }}

    function updateView() {{
      // Update active slide
      document.querySelectorAll(".slide").forEach((s, idx) => {{
        if (idx + 1 === currentSlide) {{
          s.classList.add("active");
        }} else {{
          s.classList.remove("active");
        }}
      }});

      // Update dots
      document.querySelectorAll(".dot").forEach((d, idx) => {{
        if (idx + 1 === currentSlide) {{
          d.classList.add("active");
        }} else {{
          d.classList.remove("active");
        }}
      }});

      // Update counter
      document.getElementById("slide-counter").textContent = 
        String(currentSlide).padStart(2, '0') + " / " + String(totalSlides).padStart(2, '0');

      // Update phase tracker
      const pInfo = phaseMap.find(p => p.slide === currentSlide) || phaseMap[0];
      document.querySelectorAll(".flow-box").forEach((box, idx) => {{
        if (idx === pInfo.phase) {{
          box.classList.add("active");
        }} else {{
          box.classList.remove("active");
        }}
      }});
    }}

    function goToSlide(n) {{
      if (n >= 1 && n <= totalSlides) {{
        currentSlide = n;
        updateView();
      }}
    }}

    function nextSlide() {{
      if (currentSlide < totalSlides) {{
        currentSlide++;
        updateView();
      }}
    }}

    function prevSlide() {{
      if (currentSlide > 1) {{
        currentSlide--;
        updateView();
      }}
    }}

    document.addEventListener("keydown", (e) => {{
      if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown" || e.key === "Enter") {{
        e.preventDefault();
        nextSlide();
      }} else if (e.key === "ArrowLeft" || e.key === "PageUp" || e.key === "Backspace") {{
        e.preventDefault();
        prevSlide();
      }} else if (e.key === "Home") {{
        e.preventDefault();
        goToSlide(1);
      }} else if (e.key === "End") {{
        e.preventDefault();
        goToSlide(totalSlides);
      }}
    }});

    initDots();
    updateView();
  </script>
</body>
</html>
"""
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[SUCCESS] Dark HUD HTML presentation generated at: {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_html()
