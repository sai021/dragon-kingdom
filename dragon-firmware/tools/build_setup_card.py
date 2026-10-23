"""Build universal QR setup cards and rear labels; no connected device required.

Requires reportlab. The two universal PDFs in output/setup/ are tracked in Git.
"""
import argparse
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'output/setup'
MANUAL_URL = 'https://sai021.github.io/dragon-kingdom/manual.pdf'
CONTROL_URL = 'http://192.168.4.1/'
INK = colors.HexColor('#302b49')
TEAL = colors.HexColor('#21686c')


def paragraph(c, text, x, top, width, size=10, color=INK):
    p = Paragraph(text, ParagraphStyle('text', fontName='Helvetica', fontSize=size,
                  leading=size * 1.35, textColor=color))
    _, height = p.wrap(width, 1000)
    p.drawOn(c, x, top - height)
    return top - height


def qr(c, url, x, y, size):
    # Default four-module quiet zone is included; preserve it in print.
    widget = QrCodeWidget(url, barLevel='M')
    x0, y0, x1, y1 = widget.getBounds()
    drawing = Drawing(size, size, transform=[size/(x1-x0), 0, 0, size/(y1-y0), 0, 0])
    drawing.add(widget)
    renderPDF.draw(drawing, c, x, y)
    c.linkURL(url, (x, y, x + size, y + size), relative=0)


def build(output=OUTPUT, manual_url=MANUAL_URL):
    if not manual_url.startswith('https://'):
        raise ValueError('The public manual must use an HTTPS URL.')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    card = output / 'dragon-setup-card.pdf'
    c = Canvas(str(card), pagesize=A5)
    c.setTitle('Dragon Kingdom - universal setup card')
    w, h = A5
    x, width = 13*mm, w-26*mm
    c.setFillColor(TEAL); c.rect(0, h-5*mm, w, 5*mm, fill=1, stroke=0)
    y = paragraph(c, '<b>Welcome, dragon keeper!</b>', x, h-14*mm, width, 21)
    y = paragraph(c, 'One card for every dragon. No app or account needed.', x, y-5*mm, width, 10)
    for line in [
        '<b>1. Read first.</b> Scan Setup &amp; manual while your phone has internet. Then power on one new dragon and wait for it to wake.',
        '<b>2. Join your dragon.</b> In phone Wi-Fi settings, choose a network starting <b>Dragon-Kingdom-</b>. Password: <b>dragon123</b>. If asked, stay connected without internet.',
        '<b>3. Open controls.</b> The setup page may appear automatically. Otherwise scan Open dragon below. Browser login: <b>parent</b>; password: <b>dragon123</b>.',
    ]:
        y = paragraph(c, line, x, y-4*mm, width, 10)
    qr_y = y-40*mm
    qr(c, manual_url, x+10*mm, qr_y, 32*mm)
    qr(c, CONTROL_URL, x+76*mm, qr_y, 32*mm)
    paragraph(c, '<b>Setup &amp; manual</b><br/>Needs internet', x, qr_y-1*mm, 57*mm, 10)
    paragraph(c, '<b>Open dragon</b><br/>Join dragon Wi-Fi first', x+65*mm, qr_y-1*mm, 57*mm, 10)
    y = qr_y-18*mm
    y = paragraph(c, '<b>My dragon\'s Wi-Fi name (optional)</b><br/>Dragon-Kingdom-________________', x, y, width, 10)
    y = paragraph(c, 'Several dragon networks? Power off the others while setting up. Home Wi-Fi is optional; after joining it, bookmark the address shown in the controls.', x, y-5*mm, width, 9)
    y = paragraph(c, '<b>Need setup again?</b> Hold the right-side touch button while connecting power. Keep holding through the blue pulses; release when purple appears.', x, y-4*mm, width, 9)
    paragraph(c, 'QR fallback after joining dragon Wi-Fi: http://192.168.4.1/<br/>Manual: sai021.github.io/dragon-kingdom/manual.pdf', x, y-4*mm, width, 7)
    c.showPage(); c.save()

    labels = output / 'dragon-rear-labels.pdf'
    c = Canvas(str(labels), pagesize=A4)
    c.setTitle('Dragon Kingdom - universal rear labels')
    paragraph(c, '<b>Dragon Kingdom | shared rear labels</b>', 15*mm, A4[1]-12*mm, 180*mm, 14)
    paragraph(c, 'Print at 100% / Actual size. Cut on the outlines. Each label is 90 x 65 mm.<br/>Check space on your finished enclosure before printing adhesive stock.', 15*mm, A4[1]-22*mm, 180*mm, 9)
    for row in range(3):
        for col in range(2):
            lx = (12 + col*96)*mm
            ly = A4[1]-(105+row*72)*mm
            c.setStrokeColor(colors.HexColor('#b8b8c0'))
            c.roundRect(lx, ly, 90*mm, 65*mm, 3*mm, stroke=1, fill=0)
            paragraph(c, '<b>DRAGON KINGDOM</b>', lx+5*mm, ly+60*mm, 80*mm, 11)
            qr(c, manual_url, lx+6*mm, ly+23*mm, 29*mm)
            qr(c, CONTROL_URL, lx+53*mm, ly+23*mm, 29*mm)
            paragraph(c, '<b>Setup &amp; manual</b><br/>Needs internet', lx+5*mm, ly+22*mm, 40*mm, 8)
            paragraph(c, '<b>Open dragon</b><br/>Join dragon Wi-Fi first', lx+48*mm, ly+22*mm, 40*mm, 8)
            paragraph(c, 'Wi-Fi: Dragon-Kingdom-... | Password: dragon123<br/>Browser login: parent / dragon123', lx+5*mm, ly+10*mm, 80*mm, 7)
    c.showPage(); c.save()
    print(card)
    print(labels)
    return card, labels


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--manual-url', default=MANUAL_URL)
    args = parser.parse_args()
    build(args.output, args.manual_url)
