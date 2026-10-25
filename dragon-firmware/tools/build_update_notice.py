"""Build the universal, printable class update notice. No device credentials."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from build_setup_card import paragraph, qr, INK, TEAL

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/pdf/dragon-kingdom-update-notice.pdf'
BASE = 'https://sai021.github.io/dragon-kingdom/'

def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = Canvas(str(OUT), pagesize=A4)
    c.setTitle('Dragon Kingdom - family update and setup notice')
    c.setAuthor('Dragon Kingdom')
    w, h = A4
    c.setFillColor(TEAL); c.rect(0, h-12, w, 12, fill=1, stroke=0)
    paragraph(c, '<b>DRAGON KINGDOM / FOR GROWN-UPS</b>', 42, h-36, w-84, 10, TEAL)
    top = paragraph(c, '<b>A small update for<br/>your Wall Dragon</b>', 42, h-65, w-84, 27)
    top = paragraph(c, '26 October 2026 - please keep this sheet with your setup card.', 42, top-13, w-84, 10, TEAL)
    top = paragraph(c, 'If your dragon shows an <b>HTTPS error</b> when checking for updates, there is a repair. Touch play and local phone controls still work. <b>Do not factory-reset it.</b>', 42, top-17, w-84, 11)
    top = paragraph(c, '<b>Easy Update - recommended</b>', 42, top-19, w-84, 16)
    steps = [
        '<b>1.</b> Keep each dragon on its normal bottom USB-C supply. Scan UPDATE and download Easy Update for Windows or Mac.',
        '<b>2.</b> Open the app while the computer has internet. It downloads latest stable firmware automatically. Wait until ready; offline mode is selected.',
        '<b>3.</b> For lamps <b>not on home Wi-Fi</b>, choose <b>Find &amp; update all dragons</b>. Allow OS Wi-Fi/location permission if asked. It joins each dragon, updates older firmware and skips current/newer lamps. Only use this where all nearby dragons are yours.',
        '<b>Already on home Wi-Fi?</b> Choose <b>Home Wi-Fi</b> instead, then <b>Check for updates</b> and <b>Find dragons</b>, with computer and lamp on the same home network.',
        '<b>4.</b> Wait for the results report. Parent password <b>dragon123</b> is filled in and editable. Each update backs up and checks the lamp, then tries to restore Wi-Fi. <b>Stop</b> finishes safely.',
    ]
    for text in steps: top = paragraph(c, text, 42, top-9, w-84, 10)
    top = paragraph(c, '<b>No laptop USB or opening the box.</b> Setup AP closes 15 seconds after joining home Wi-Fi. The guide includes manual and phone-only alternatives.', 42, top-11, w-84, 10)
    # Three independent, high contrast QR codes with their quiet zones intact.
    y = 241; size = 33*mm
    for x, title, url, short in [(42, 'UPDATE / DOWNLOADS', BASE+'update/', 'sai021.github.io/<br/>dragon-kingdom/update/'),
                                (218, 'SETUP / MANUAL', BASE+'setup/', 'sai021.github.io/<br/>dragon-kingdom/setup/'),
                                (394, 'OPEN YOUR DRAGON', 'http://192.168.4.1/', 'http://192.168.4.1/<br/>Join dragon Wi-Fi first')]:
        paragraph(c, '<b>'+title+'</b>', x, y+size+23, 160, 9, TEAL)
        qr(c, url, x, y, size)
        paragraph(c, short, x, y-7, 160, 9)
    paragraph(c, '<b>Need to set up Wi-Fi again?</b>', 42, 181, w-84, 14)
    paragraph(c, 'Power the dragon on. On your phone, join <b>Dragon-Kingdom-XXXXXX</b> (your dragon has its own six letters/numbers). Wi-Fi password: <b>dragon123</b>. Stay connected if warned there is no internet. Open <b>http://192.168.4.1/</b>.', 42, 156, w-84, 10)
    paragraph(c, 'Unlock Parent settings with <b>dragon123</b>, then teach it your <b>2.4 GHz home Wi-Fi</b>. Rejoin home Wi-Fi and open the saved dragon address. The SETUP link repeats the full instructions and user manual.', 42, 104, w-84, 10)
    paragraph(c, 'Cannot find the lamp? Avoid guest/isolated networks; use Add address from its webpage.\nIf you need help, contact the person who supplied your dragon.', 42, 54, w-84, 8, TEAL)
    c.showPage(); c.save(); print(OUT)

if __name__ == '__main__': build()
