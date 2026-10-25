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
    top = paragraph(c, '<b>Update over home Wi-Fi</b>', 42, top-19, w-84, 16)
    steps = [
        '<b>1.</b> Keep the dragon on its normal bottom USB-C power supply. Connect your Windows computer or Mac to the same home network.',
        '<b>2.</b> Scan UPDATE below. Download and open Dragon Kingdom Updater. Choose <b>Find dragons</b>, select yours and enter the parent password: <b>dragon123</b>.',
        '<b>3.</b> Review the offered version and choose <b>Update selected dragon</b>. Keep power, Wi-Fi and the app connected until it confirms the restart and saved settings.',
    ]
    for text in steps: top = paragraph(c, text, 42, top-11, w-84, 11)
    top = paragraph(c, '<b>No laptop USB cable or opening the box is needed.</b> The same app works for later compatible releases. The update page also explains the phone-only file-upload option.', 42, top-13, w-84, 10)
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
