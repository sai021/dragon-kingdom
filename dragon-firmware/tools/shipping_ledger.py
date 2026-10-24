"""Append private, explicit production results. Never infer physical acceptance from startup."""
import argparse
import datetime
import json
from pathlib import Path
from recovery import prepared_release
from flash_support import ROOT

CHECKS=('startup','led','touch','ldr','external_power','phone_setup','router_reconnect','overnight')
def record(bundle,unit,board,calibrated,results,path=None):
    info=prepared_release(bundle)
    if not unit or len(unit)>80 or any(ord(c)<32 for c in unit):raise ValueError('Use a short local unit identifier')
    if any(k not in CHECKS or v not in ('pass','fail','pending') for k,v in results.items()):raise ValueError('Unknown functional result')
    path=path or ROOT/'.tools/shipping/ledger.jsonl'
    path.parent.mkdir(parents=True,exist_ok=True)
    row={'unit':unit,'board':board,'firmware':info['firmware_tag'],'image_sha256':info['targets'][board]['sha256']['DragonPrototype.ino.bin'],'calibration_present':calibrated,'test_date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'functional_results':{k:results.get(k,'pending') for k in CHECKS}}
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(row)+'\n')
    return row

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--unit',required=True);p.add_argument('--board',choices=['s3','c3'],required=True);p.add_argument('--calibrated',choices=['yes','no','unknown'],default='unknown')
    for check in CHECKS:p.add_argument('--'+check.replace('_','-'),choices=['pass','fail','pending'],default='pending')
    a=p.parse_args();record(a.bundle,a.unit,a.board,{'yes':True,'no':False,'unknown':None}[a.calibrated],{k:getattr(a,k) for k in CHECKS})
