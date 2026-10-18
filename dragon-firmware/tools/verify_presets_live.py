"""Short serial smoke test for installed presets; restores blue at the end."""
import time
import argparse
from pathlib import Path
from flash_support import serial_modules, check_startup

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',required=True,help='Actual current port from tools/dev.py ports')
    args=parser.parse_args()
    serial,ports=serial_modules()
    if args.port not in {p.device for p in ports.comports()}:parser.error('Selected port is not currently present.')
    check_startup(args.port,lambda text:None)
    port=serial.Serial(port=None,baudrate=115200,timeout=.15,write_timeout=2)
    port.dtr=True;port.rts=False;port.port=args.port;port.open()
    logpath=Path(__file__).resolve().parents[1]/'.tools'/'dragon-presets-live.log'
    try:
        with logpath.open('w',encoding='utf-8') as log:
            for dragon in ('glory','moonwatcher','winter','sundew','mightyclaws','blue'):
                port.reset_input_buffer()
                port.write(f'dragon {dragon}\nstatus\n'.encode())
                end=time.monotonic()+2;confirmed=False
                while time.monotonic()<end:
                    line=port.readline().decode(errors='replace').strip()
                    if not line:continue
                    log.write(line+'\n');log.flush()
                    if line.startswith(('dragon=','startup_pending=')):print(line,flush=True)
                    confirmed|=line.startswith(f'dragon={dragon} ')
                if not confirmed:raise RuntimeError(f'No confirmation for {dragon}')
            print('PASS: six installed preset selections confirmed; blue restored.',flush=True)
    finally:
        port.write(b'dragon blue\n')
        port.close()

if __name__=='__main__':main()
