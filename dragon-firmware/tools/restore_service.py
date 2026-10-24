"""Back up raw NVS before deliberate corrupt-journal recovery. Internal USB power only."""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from recovery import installed_esptool, validate_current_nvs
from board_targets import parse_chip
from flash_support import ROOT, serial_modules

def backup(port,usb_only,tool=None):
    if not usb_only:raise ValueError('Confirm external/main power is disconnected before any device access.')
    tool=tool or installed_esptool()
    if not tool:raise ValueError('Installed esptool required')
    def run(*args):
        return subprocess.run([str(tool),'--chip','auto','--port',port,'--after','no-reset',*map(str,args)],capture_output=True,text=True,check=True,timeout=90)
    board=parse_chip(run('chip-id').stdout)
    directory=ROOT/'.tools/restore-service'/time.strftime('%Y%m%d-%H%M%S');directory.mkdir(parents=True,exist_ok=False)
    table=directory/'partitions.bin';run('read-flash','0x8000','0x1000',table);validate_current_nvs(table.read_bytes())
    dump=directory/'nvs-before.bin';run('read-flash','0x9000','0x5000',dump)
    if dump.stat().st_size!=0x5000:raise ValueError('Incomplete evidence; do not clear anything')
    # A second independent read verifies evidence before any service mutation.
    check=directory/'nvs-verify.bin';run('read-flash','0x9000','0x5000',check)
    if dump.read_bytes()!=check.read_bytes():raise ValueError('NVS evidence changed; retain both captures and stop')
    (directory/'evidence.json').write_text(json.dumps({'board':board,'nvs_sha256':hashlib.sha256(dump.read_bytes()).hexdigest()}))
    return directory

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True);p.add_argument('--usb-only',action='store_true');a=p.parse_args()
    directory=backup(a.port,a.usb_only)
    print('Private NVS evidence verified at '+str(directory))
    print('Reset with external power still disconnected. Reconfirm the runtime port, then use restore retry. Only for an invalid journal, deliberately send: restore abandon-invalid EVIDENCE-SAVED. Inspect all saved settings after reboot; interrupted namespaces may contain mixed old/new data.')
