#!/usr/bin/env python3
"""Portable Arduino CLI setup, build, upload and monitor helper."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from palettes import generate as generate_palettes
from embed_web import generate as generate_web
from board_targets import TARGETS, detect_board

ROOT = Path(__file__).resolve().parents[1]
FQBN = TARGETS['s3']
INDEX = 'https://espressif.github.io/arduino-esp32/package_esp32_index.json'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['setup', 'ports', 'build', 'upload', 'monitor'])
    parser.add_argument('--port', help='For example COM5 or /dev/cu.usbmodem123')
    parser.add_argument('--cli', default=os.environ.get('ARDUINO_CLI', 'arduino-cli'))
    parser.add_argument('--board', choices=['s3', 'c3', 'auto'], default='s3', help='auto probes the connected chip for upload')
    parser.add_argument('--fqbn', help='Override for your verified board configuration')
    args = parser.parse_args()
    if args.board == 'auto' and args.fqbn:
        parser.error('--fqbn cannot override automatic chip selection')
    if args.action in ('upload', 'monitor') and not args.port:
        parser.error('--port is required; run ports first')
    cli = shutil.which(args.cli)
    if not cli:
        parser.error('Install Arduino CLI and add it to PATH, or use --cli with its full path. See OTHER-COMPUTER.md.')
    def run(*items):
        subprocess.run([cli, *items], check=True)
    if args.action == 'setup':
        run('core', 'update-index', '--additional-urls', INDEX)
        run('core', 'install', 'esp32:esp32@3.2.1', '--additional-urls', INDEX)
        run('lib', 'install', 'Adafruit NeoPixel@1.12.5')
    elif args.action == 'ports':
        run('board', 'list')
    elif args.action == 'monitor':
        run('monitor', '-p', args.port, '--config', 'baudrate=115200')
    else:
        if args.board == 'auto' and (args.action != 'upload' or not args.port):
            parser.error('--board auto requires upload --port PORT')
        board = detect_board(cli, args.port) if args.board == 'auto' else args.board
        fqbn = args.fqbn or TARGETS[board]
        generate_palettes()
        generate_web()
        build = ROOT / 'build' / board
        run('compile', '--fqbn', fqbn, '--build-path', str(build), str(ROOT / 'DragonPrototype'))
        app = build / 'DragonPrototype.ino.bin'
        if not app.is_file() or not 0 < app.stat().st_size <= 0x180000:
            parser.error('application is missing, empty or exceeds the custom 0x180000-byte app partition')
        from flash_support import source_fingerprint
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        (build/'provenance.json').write_text(json.dumps({'source_commit':commit,'source_sha256':source_fingerprint(),'board':board,'toolchain':'esp32:esp32@3.2.1;Adafruit NeoPixel@1.12.5'}))
        if args.action == 'upload':
            run('upload', '--fqbn', fqbn, '--port', args.port,
                '--input-dir', str(build), str(ROOT / 'DragonPrototype'))

if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)
