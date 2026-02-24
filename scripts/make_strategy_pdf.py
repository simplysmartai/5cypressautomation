#!/usr/bin/env python3
"""
Convert 01-marketing-strategy.html to PDF using weasyprint (preferred)
or reportlab as fallback. Saves to the same folder.
"""
from pathlib import Path, PurePosixPath
import sys, subprocess

REVIEW_DIR = Path(r"c:\Users\smart\Downloads\5cypress-marketing-team\5cypress-marketing-team\output\medsync-solutions-review")
HTML_IN = REVIEW_DIR / "01-marketing-strategy.html"
PDF_OUT = REVIEW_DIR / "01-marketing-strategy.pdf"

def try_weasyprint():
    import weasyprint
    weasyprint.HTML(filename=str(HTML_IN)).write_pdf(str(PDF_OUT))
    return True

def try_pdfkit():
    import pdfkit
    pdfkit.from_file(str(HTML_IN), str(PDF_OUT))
    return True

def fallback_reportlab():
    """Simple text-extraction fallback using reportlab."""
    import re
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable, KeepTogether)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    html = HTML_IN.read_text(encoding='utf-8')
    # Strip tags but preserve structure markers
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
    def tag_to_marker(m):
        # group(2) is the tag name; split on whitespace to handle attrs in group(2)
        tag = m.group(2).lower().strip()
        map_ = {'h1':'##H1##','h2':'##H2##','h3':'##H3##','p':'##P##',
                'li':'##LI##','td':'##TD##','th':'##TH##','tr':'##TR##',
                'div':'##P##','br':'\\n'}
        return '\n'+map_.get(tag,'')+'\n'
    html = re.sub(r'<(/?)([a-zA-Z0-9]+)[^>]*>', tag_to_marker, html)
    html = re.sub(r'&amp;','&',html)
    html = re.sub(r'&lt;','<',html)
    html = re.sub(r'&gt;','>',html)
    html = re.sub(r'&mdash;','—',html)
    html = re.sub(r'&#\d+;','',html)
    html = re.sub(r'&[a-z]+;','',html)

    GREEN = colors.HexColor('#1B4332')
    GREEN_L = colors.HexColor('#52B788')
    ACCENT = colors.HexColor('#D8F3DC')

    doc = SimpleDocTemplate(str(PDF_OUT), pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54,
        title='MedSync Solutions — Marketing Strategy Report',
        author='5 Cypress Automation')

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('h1',fontName='Helvetica-Bold',fontSize=22,textColor=GREEN,
                         spaceAfter=10,spaceBefore=20,alignment=TA_LEFT)
    h2 = ParagraphStyle('h2',fontName='Helvetica-Bold',fontSize=16,textColor=GREEN,
                         spaceAfter=6,spaceBefore=18)
    h3 = ParagraphStyle('h3',fontName='Helvetica-Bold',fontSize=12,textColor=colors.HexColor('#2D6A4F'),
                         spaceAfter=4,spaceBefore=12)
    body = ParagraphStyle('body',fontName='Helvetica',fontSize=9.5,
                           textColor=colors.HexColor('#374151'),spaceAfter=8,leading=15)
    li_s = ParagraphStyle('li',fontName='Helvetica',fontSize=9,
                           textColor=colors.HexColor('#374151'),spaceAfter=4,
                           leftIndent=16,firstLineIndent=-10,leading=14)

    elems = []
    lines = html.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('##H1##'):
            t = line.replace('##H1##','').strip()
            if t: elems.append(Paragraph(t, h1))
        elif line.startswith('##H2##'):
            t = line.replace('##H2##','').strip()
            if t:
                elems.append(HRFlowable(width='100%',thickness=1,color=colors.HexColor('#e5e7eb'),spaceAfter=6,spaceBefore=16))
                elems.append(Paragraph(t, h2))
        elif line.startswith('##H3##'):
            t = line.replace('##H3##','').strip()
            if t: elems.append(Paragraph(t, h3))
        elif line.startswith('##LI##'):
            t = line.replace('##LI##','').strip()
            if t: elems.append(Paragraph('→ '+t, li_s))
        elif line.startswith(('##P##','##TD##','##TH##','##TR##')):
            t = re.sub(r'##\w+##','',line).strip()
            if t and len(t) > 2:
                elems.append(Paragraph(t, body))
        elif len(line) > 4 and not line.startswith('#'):
            try:
                elems.append(Paragraph(line, body))
            except Exception:
                pass
        elems.append(Spacer(1, 2))
    doc.build(elems)
    return True

if __name__ == '__main__':
    print(f'Converting: {HTML_IN}')
    print(f'Output:     {PDF_OUT}')

    success = False
    for method_name, method in [('weasyprint', try_weasyprint),
                                  ('pdfkit', try_pdfkit),
                                  ('reportlab-fallback', fallback_reportlab)]:
        try:
            print(f'Trying {method_name}...')
            if method():
                print(f'✓ PDF created via {method_name}: {PDF_OUT}')
                success = True
                break
        except ImportError:
            print(f'  {method_name} not installed, trying next...')
        except Exception as e:
            print(f'  {method_name} failed: {e}')

    if not success:
        print('All methods failed. Please open the HTML in Chrome and use Print → Save as PDF.')
        sys.exit(1)
