"""Create signed offline Dragon update packages; private keys stay in ignored local storage."""
import argparse, hashlib, json, re
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
ROOT=Path(__file__).resolve().parents[1]
def canonical(board,size,digest,tag=None,capabilities=1,schema=1):
    if board not in ('s3','c3') or not 0<size<=0x180000 or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Invalid board, image size or SHA-256')
    if tag is None: # Deliberate legacy bridge only, never the normal signing path.
        return f'dragon-update-v1\n{board}\n{size}\n{digest}\n'.encode()
    if not re.fullmatch(r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-beta\.(0|[1-9][0-9]*))?',tag) or len(tag)>48:
        raise ValueError('Invalid release tag')
    if not isinstance(capabilities,int) or not 0<=capabilities<=1000000 or schema!=1:
        raise ValueError('Unsupported compatibility contract')
    return f'dragon-update-v2\n{board}\n{tag}\n{size}\n{digest}\n{capabilities}\n{schema}\n'.encode()

def package(image,board,key,tag=None,capabilities=1,schema=1):
    content=image.read_bytes();digest=hashlib.sha256(content).hexdigest()
    signature=key.sign(canonical(board,len(content),digest,tag,capabilities,schema),padding.PKCS1v15(),hashes.SHA256())
    result={'format':2 if tag else 1,'board':board,'size':len(content),'sha256':digest,'signature':signature.hex(),'image':content.hex()}
    if tag:result.update(tag=tag,capabilities=capabilities,schema=schema)
    return result

def online_manifest(pkg,tag,key):
    message=canonical(pkg['board'],pkg['size'],pkg['sha256'],tag,pkg.get('capabilities',1),pkg.get('schema',1))
    return message.decode()+key.sign(message,padding.PKCS1v15(),hashes.SHA256()).hex()+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['keygen','sign']);p.add_argument('--key',type=Path,required=True);p.add_argument('--board',choices=['s3','c3']);p.add_argument('--image',type=Path);p.add_argument('--output',type=Path);p.add_argument('--tag',help='Also write online manifest and raw binary for this GitHub release tag');p.add_argument('--legacy-bridge',action='store_true',help='Explicit offline v1 bridge for older firmware; use only a calibration-aware image');a=p.parse_args()
    # Key creation is deliberately separate from builds: never silently change the trust root.
    if a.action=='keygen':
        if a.key.exists():p.error('Key already exists; refusing to replace it')
        key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        a.key.parent.mkdir(parents=True,exist_ok=True)
        a.key.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
        public=key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        (ROOT/'DragonPrototype/UpdatePublicKey.h').write_text('#pragma once\n// Public release verification key. Private key is never shipped.\nstatic const char DRAGON_UPDATE_PUBLIC_KEY[]=R"KEY('+public+')KEY";\n')
    else:
        if not(a.board and a.image and a.output and a.tag):p.error('sign requires --board, --image, --output and --tag')
        key=serialization.load_pem_private_key(a.key.read_bytes(),password=None)
        from release_contract import public_key
        if key.public_key().public_numbers()!=public_key().public_numbers():p.error('Signing key differs from the installed trust root')
        a.output.parent.mkdir(parents=True,exist_ok=True);pkg=package(a.image,a.board,key,None if a.legacy_bridge else a.tag);a.output.write_text(json.dumps(pkg,separators=(',',':')))
        if a.tag and not a.legacy_bridge:
            (a.output.parent/f'dragon-{a.board}.manifest').write_text(online_manifest(pkg,a.tag,key),encoding='ascii')
            (a.output.parent/f'dragon-{a.board}.bin').write_bytes(a.image.read_bytes())
if __name__=='__main__':main()
