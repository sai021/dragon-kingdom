"""Verified build targets and ROM-based chip detection (never infer from USB VID)."""
import json
from pathlib import Path
import re
import subprocess

TARGETS = {
    's3': 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=4M,PSRAM=enabled,PartitionScheme=custom',
    'c3': 'esp32:esp32:esp32c3:CDCOnBoot=cdc,FlashSize=4M,FlashMode=dio,PartitionScheme=custom',
}


def parse_chip(output):
    # Accept esptool 4/5 banners, including package suffixes such as ESP32-C3FH4.
    chips = {chip.lower() for chip in re.findall(r'(?:Chip is|Chip type:)\s*ESP32-(S3|C3)\b', output, re.I)}
    # Some esptool versions append a package code without a separating space.
    chips.update(chip.lower() for chip in re.findall(r'(?:Chip is|Chip type:)\s*ESP32-(S3|C3)(?=F|R|\s|\(|$)', output, re.I))
    if len(chips) != 1:
        raise RuntimeError('Could not identify a supported ESP32-S3/C3. Nothing was written. Try BOOT/RESET and retry.')
    return chips.pop().lower()


def detect_board(cli, port):
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    details = subprocess.run([cli, 'board', 'details', '--fqbn', TARGETS['s3'], '--format', 'json'],
                             capture_output=True, text=True, check=True, timeout=30, creationflags=flags)
    properties = dict(item.split('=', 1) for item in json.loads(details.stdout)['build_properties'] if '=' in item)
    tool = Path(properties['runtime.tools.esptool_py.path']) / properties['tools.esptool_py.cmd']
    # Read the ROM identity and leave the chip in the loader for the following upload.
    # This can reset the board but does not erase or write flash.
    probe = subprocess.run([str(tool), '--chip', 'auto', '--port', port, '--baud', '115200',
                            '--after', 'no-reset', 'chip-id'], capture_output=True, text=True,
                           timeout=30, creationflags=flags)
    if probe.returncode:
        raise RuntimeError('Chip detection failed. Nothing was written. Close serial monitors; try BOOT/RESET and retry.\n'
                           + probe.stdout + probe.stderr)
    return parse_chip(probe.stdout + probe.stderr)
