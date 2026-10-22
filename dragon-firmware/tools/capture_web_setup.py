"""Capture boot diagnostics locally, then build the universal QR setup card."""
import argparse
import json
from pathlib import Path
import re
import time
import serial
from build_setup_card import build

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
                line = re.sub(r'password=\S+', 'password=[redacted]', line)
            lines.append(line)
    local = ROOT / '.tools'
    local.mkdir(exist_ok=True)
    (local / 'web-installed-live.log').write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines[-14:]))
    if not details:
        raise SystemExit('Boot setup details not captured; no setup card created.')
    (local / 'setup-credentials.json').write_text(json.dumps(details), encoding='utf-8')
    if any('Guru Meditation' in line or 'panic' in line for line in lines):
        raise SystemExit('Startup crash detected; do not hand over this build.')
    build()

if __name__ == '__main__':
    main()
