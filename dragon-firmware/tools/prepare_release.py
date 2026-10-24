"""Prepare an immutable, signed two-board release from fresh build outputs. Never publish or flash."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from flash_support import ROOT, FILES, bundle_manifest, source_fingerprint
from board_targets import TARGETS
from recovery import validate_partitions, validate_image_target, image_app_digest
from release_contract import canonical, public_key
from sign_update import package, online_manifest

def prepare(builds,output,key_path,tag):
    if output.exists():raise ValueError('Output already exists; release bundles are immutable.')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no','--','DragonPrototype','tools','web','presets'],cwd=ROOT,text=True).strip():
        raise ValueError('Commit reviewed sources before preparing a release.')
    current=(ROOT/'DragonPrototype/OnlinePolicy.h').read_text()
    if 'CURRENT_TAG="'+tag+'"' not in current:raise ValueError('Tag differs from source firmware identity')
    key=serialization.load_pem_private_key(key_path.read_bytes(),password=None)
    if key.public_key().public_numbers()!=public_key().public_numbers():raise ValueError('Signing key does not match installed trust root')
    targets={}
    # Validate everything before creating the immutable output folder.
    for board in TARGETS:
        build=builds/board
        targets[board]=bundle_manifest(build,board)
        validate_partitions((build/FILES[2]).read_bytes())
        for name in FILES[:2]:validate_image_target((build/name).read_bytes(),board)
        image_app_digest((build/FILES[0]).read_bytes())
        provenance=json.loads((build/'provenance.json').read_text())
        if provenance!={'source_commit':commit,'source_sha256':source_fingerprint(),'board':board,'toolchain':'esp32:esp32@3.2.1;Adafruit NeoPixel@1.12.5','sha256':targets[board]['sha256']}:
            raise ValueError('Build provenance does not match this committed source. Rebuild both targets.')
    output.mkdir(parents=True)
    for board in TARGETS:
        build=builds/board;shutil.copytree(build,output/board,ignore=shutil.ignore_patterns('sketch','core','libraries','*.o','*.elf','*.map'))
        pkg=package(build/FILES[0],board,key,tag)
        (output/f'dragon-{board}.dragon.json').write_text(json.dumps(pkg,separators=(',',':')))
        (output/f'dragon-{board}.manifest').write_text(online_manifest(pkg,tag,key),encoding='ascii')
        shutil.copyfile(build/FILES[0],output/f'dragon-{board}.bin')
    info={'schema':1,'contract':2,'firmware_tag':tag,'source_commit':commit,'source_sha256':source_fingerprint(),'toolchain':'esp32:esp32@3.2.1;Adafruit NeoPixel@1.12.5','saved_schema':1,'capabilities':1,'targets':targets}
    info['signature']=key.sign(canonical(info),padding.PKCS1v15(),hashes.SHA256()).hex()
    (output/'current-set.json').write_text(json.dumps(info,indent=2))
    return info

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--builds',type=Path,default=ROOT/'build');p.add_argument('--output',type=Path,required=True);p.add_argument('--key',type=Path,required=True);p.add_argument('--tag',required=True)
    a=p.parse_args();prepare(a.builds,a.output,a.key,a.tag)
