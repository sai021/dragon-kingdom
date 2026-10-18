"""Capture boot setup details locally and make a printable parent setup card."""
import argparse
import html
import json
from pathlib import Path
import re
import time
import serial

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True)
    parser.add_argument('--seconds', type=int, default=20)
    args = parser.parse_args()
    details = None
    lines = []
    with serial.Serial(args.port, 115200, timeout=0.2) as port:
        port.write(b'status\n')
        deadline = time.monotonic() + args.seconds
        while time.monotonic() < deadline:
            line = port.readline().decode('utf-8', 'replace').strip()
            if not line:
                continue
            match = re.search(r'Dragon web: network=(\S+) password=(\S+) login=(\S+) setup=(\S+) home=(\S+)', line)
            if match:
                details = dict(zip(['network', 'password', 'login', 'setup', 'home'], match.groups()))
                line = re.sub(r'password=\S+', 'password=[on local setup card]', line)
            lines.append(line)
    local = ROOT / '.tools'
    local.mkdir(exist_ok=True)
    (local / 'web-installed-live.log').write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines[-14:]))
    if not details:
        raise SystemExit('Boot setup details not captured; no setup card created.')
    (local / 'setup-credentials.json').write_text(json.dumps(details), encoding='utf-8')
    escaped = {key: html.escape(value, quote=True) for key, value in details.items()}
    card = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dragon Kingdom setup card</title><style>body{font:18px system-ui;max-width:600px;margin:40px auto;padding:24px;color:#19182d}h1{color:#514476}li{margin:18px 0;line-height:1.6}code{font-size:20px;overflow-wrap:anywhere}aside{background:#eef4f4;padding:20px;border-radius:16px}button{font:inherit;padding:12px}@media print{button{display:none}}</style>
<h1>Your Dragon Kingdom</h1><p>Keep this card for connecting from a phone.</p><ol>
<li>Plug in your dragon.</li><li>In your phone's Wi-Fi settings, join <strong>{network}</strong>.<br>Password: <code>{password}</code><br>If it says “No internet”, choose to stay connected.</li>
<li>Open <a href="{setup}">{setup}</a> in your browser.<br>Login: <strong>{login}</strong><br>Use the same password shown above.</li>
<li>Play, or open <strong>For grown-ups · Wi-Fi &amp; help</strong> to connect your dragon to home Wi-Fi.</li></ol>
<aside><strong>To reopen setup later</strong><p>Hold the touch pad while plugging in. Keep holding through the blue startup pulses, then release when purple appears. Join the dragon network again using this card.</p><p>When connected to home Wi-Fi, try <a href="{home}">{home}</a>.</p></aside>
<p>Internet is optional for dragon play.</p><button onclick="print()">Print this card</button></html>'''
    for key, value in escaped.items():
        card = card.replace('{'+key+'}', value)
    output = local / 'dragon-setup-card.html'
    output.write_text(card, encoding='utf-8')
    print('Created local setup card:', output)
    if any('Guru Meditation' in line or 'panic' in line for line in lines):
        raise SystemExit('Startup crash detected; do not hand over this build.')

if __name__ == '__main__':
    main()
