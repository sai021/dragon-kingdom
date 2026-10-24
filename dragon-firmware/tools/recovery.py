"""USB-only migration/recovery. Preserve and verify the original NVS partition."""
import argparse, json, struct, subprocess, time
from pathlib import Path
from board_targets import TARGETS, detect_board, parse_chip
from flash_support import ROOT, FILES, load_bundle, digest, check_startup

def validate_partitions(raw):
    entries={}
    for at in range(0,len(raw)-31,32):
        magic,kind,sub,offset,size,label,flags=struct.unpack('<HBBII16sI',raw[at:at+32])
        if magic!=0x50aa:break
        entries[label.rstrip(b'\0').decode('ascii')]=(kind,sub,offset,size)
    expected={'nvs':(1,2,0x9000,0x5000),'otadata':(1,0,0xe000,0x2000),'app0':(0,0x10,0x10000,0x180000),'app1':(0,0x11,0x190000,0x180000)}
    if any(entries.get(k)!=v for k,v in expected.items()):raise ValueError('Recovery requires the new two-slot partition layout with unchanged NVS offset and size.')
    return entries

def validate_current_nvs(raw):
    for at in range(0,len(raw)-31,32):
        magic,kind,sub,offset,size,label,flags=struct.unpack('<HBBII16sI',raw[at:at+32])
        if magic!=0x50aa:break
        if label.rstrip(b'\0')==b'nvs':
            if (kind,sub,offset,size)==(1,2,0x9000,0x5000):return
            raise ValueError('Connected board has a different NVS layout. Nothing was written.')
    raise ValueError('Could not verify the connected board NVS layout. Nothing was written.')

def esptool_path(cli):
    result=subprocess.run([cli,'board','details','--fqbn',TARGETS['s3'],'--format','json'],capture_output=True,text=True,check=True,timeout=30)
    props=dict(v.split('=',1) for v in json.loads(result.stdout)['build_properties'] if '=' in v)
    return Path(props['runtime.tools.esptool_py.path'])/props['tools.esptool_py.cmd']

def recover(cli,port,usb_only,emit=print,cache=None,tool=None):
    if not usb_only:raise ValueError('Disconnect external/main power before internal laptop USB recovery.')
    if tool:
        probe=subprocess.run([str(tool),'--chip','auto','--port',port,'--baud','115200','--after','no-reset','chip-id'],capture_output=True,text=True,timeout=30,check=True)
        board=parse_chip(probe.stdout+probe.stderr)
    else:board=detect_board(cli,port)
    emit('Verified ESP32-'+board.upper())
    build=load_bundle(board=board,cache=cache or ROOT/'.tools/recovery-release')
    validate_partitions((build/FILES[2]).read_bytes())
    tool=Path(tool) if tool else esptool_path(cli);session=ROOT/'.tools/recovery'/time.strftime('%Y%m%d-%H%M%S');session.mkdir(parents=True,exist_ok=False)
    def run(*args):
        result=subprocess.run([str(tool),'--chip','esp32'+board,'--port',port,'--after','no-reset',*map(str,args)],capture_output=True,text=True,timeout=180)
        if result.returncode:raise RuntimeError('Recovery operation failed. Keep USB connected and retain the local NVS backup. '+result.stderr[-1000:])
    live_table=session/'partitions-before.bin';run('read-flash','0x8000','0x1000',live_table);validate_current_nvs(live_table.read_bytes())
    before=session/'nvs-before.bin';after=session/'nvs-after.bin'
    emit('Backing up saved data locally. This file contains credentials; keep it private.')
    run('read-flash','0x9000','0x5000',before)
    if before.stat().st_size!=0x5000:raise RuntimeError('NVS backup is incomplete. Nothing was written.')
    # These ranges exclude 0x9000..0xDFFF. No erase-flash, merged image or NVS write.
    ota=session/'otadata-reset.bin';ota.write_bytes(b'\xff'*0x2000)
    emit('Writing verified board image and two-slot layout. Keep USB connected.')
    run('write-flash','0x0',build/FILES[1],'0x8000',build/FILES[2],'0xe000',ota,'0x10000',build/FILES[0])
    run('read-flash','0x9000','0x5000',after)
    if digest(before)!=digest(after):raise RuntimeError('Saved-data verification FAILED. Keep the NVS backup; do not claim successful migration.')
    emit('Saved NVS bytes verified unchanged. Resetting the verified board for startup checks.')
    subprocess.run([str(tool),'--chip','esp32'+board,'--port',port,'--no-stub','--after','hard-reset','chip-id'],capture_output=True,text=True,timeout=30,check=True)
    check_startup(port,emit)
    emit('Recovery complete. Keep USB-only power until unplugged. Setup Wi-Fi opens at startup.')
    return session

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True);p.add_argument('--cli',default=str(ROOT/'.tools/arduino-cli/arduino-cli.exe'));p.add_argument('--esptool',type=Path,help='Use an installed standalone esptool, without Arduino CLI');p.add_argument('--usb-only',action='store_true');a=p.parse_args()
    recover(a.cli,a.port,a.usb_only,tool=a.esptool)

if __name__=='__main__':main()
