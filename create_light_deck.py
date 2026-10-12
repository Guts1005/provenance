import zipfile
import shutil
import os
from PIL import Image, ImageDraw
import io

src_pptx = r"C:\Users\sharv\barcode-test\Provenance_Client_Presentation.pptx"
dst_pptx = r"C:\Users\sharv\barcode-test\Provenance_Client_Presentation_Light.pptx"

# 1. Generate tactile light dot-grid canvas
w, h = 1920, 1080
# Canvas base: #E4E7E9 (228, 231, 233) matching the app's --canvas token
bg_img = Image.new('RGB', (w, h), (228, 231, 233))
draw = ImageDraw.Draw(bg_img)

# Subtle dot grid every 48px matching app layout
dot_color = (201, 206, 210) # #C9CED2 (--line token)
for y in range(24, h, 48):
    for x in range(24, w, 48):
        draw.ellipse([x-1, y-1, x+1, y+1], fill=dot_color)

bg_bytes = io.BytesIO()
bg_img.save(bg_bytes, format='PNG')
bg_data = bg_bytes.getvalue()

# 2. Light Theme XML
# In DrawingML:
# lt1 -> bg1 (titles/headings) -> #17181A (deep obsidian)
# lt2 -> bg2 (subtitles/body text) -> #3F454C (deep slate)
# dk1 -> tx1 -> #17181A (black)
# dk2 -> tx2 (card fill) -> #FFFFFF (pure white card surface)
# accent1 -> #059669 (industrial emerald green)
# accent2 -> #DC2626 (crimson alert)
# accent3 -> #64748B (slate category kickers)
# accent4 -> #C9CED2 (crisp light border)
# accent5 -> #F1F5F9 (recessed light surface)
# accent6 -> #047857 (deep emerald)

light_theme_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Provenance Light">
  <a:themeElements>
    <a:clrScheme name="Provenance Light">
      <a:dk1><a:srgbClr val="17181A"/></a:dk1>
      <a:lt1><a:srgbClr val="17181A"/></a:lt1>
      <a:dk2><a:srgbClr val="FFFFFF"/></a:dk2>
      <a:lt2><a:srgbClr val="3F454C"/></a:lt2>
      <a:accent1><a:srgbClr val="059669"/></a:accent1>
      <a:accent2><a:srgbClr val="DC2626"/></a:accent2>
      <a:accent3><a:srgbClr val="64748B"/></a:accent3>
      <a:accent4><a:srgbClr val="C9CED2"/></a:accent4>
      <a:accent5><a:srgbClr val="F1F5F9"/></a:accent5>
      <a:accent6><a:srgbClr val="047857"/></a:accent6>
      <a:hlink><a:srgbClr val="059669"/></a:hlink>
      <a:folHlink><a:srgbClr val="64748B"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Provenance Fonts">
      <a:majorFont><a:latin typeface="Segoe UI"/></a:majorFont>
      <a:minorFont><a:latin typeface="Segoe UI"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Provenance Format">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>"""

# 3. Create new zip
with zipfile.ZipFile(src_pptx, 'r') as zin, zipfile.ZipFile(dst_pptx, 'w') as zout:
    for item in zin.infolist():
        if item.filename == 'ppt/theme/theme1.xml':
            zout.writestr(item, light_theme_xml)
        elif item.filename in ['ppt/media/CONTENT-image-1.png', 'ppt/media/COVER-image-1.png', 'ppt/media/CLOSE-image-1.png']:
            zout.writestr(item, bg_data)
        else:
            zout.writestr(item, zin.read(item.filename))

print("Created Provenance_Client_Presentation_Light.pptx")
