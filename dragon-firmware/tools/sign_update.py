"""Create signed offline Dragon update packages; private keys stay in ignored local storage."""
import argparse, hashlib, json
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
ROOT=Path(__file__).resolve().parents[1]
def canonical(board,size,digest):
    if board not in ('s3','c3') or not 0<size<=0x180000 or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Invalid board, image size or SHA-256')
    return f'dragon-update-v1\n{board}\n{size}\n{digest}\n'.encode()
def package(image,board,key):
    content=image.read_bytes();digest=hashlib.sha256(content).hexdigest()
    signature=key.sign(canonical(board,len(content),digest),padding.PKCS1v15(),hashes.SHA256())
    return {'format':1,'board':board,'size':len(content),'sha256':digest,'signature':signature.hex(),'image':content.hex()}
def online_manifest(pkg,tag,key):
    if not 1<=len(tag)<=48 or any(not(c.isascii() and (c.isalnum() or c in '._-')) for c in tag):raise ValueError('Invalid release tag')
    canonical(pkg['board'],pkg['size'],pkg['sha256'])
    message=f"dragon-online-v1\n{pkg['board']}\n{tag}\n{pkg['size']}\n{pkg['sha256']}\n".encode()
    signature=key.sign(message,padding.PKCS1v15(),hashes.SHA256()).hex()
    return message.decode()+signature+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['keygen','sign']);p.add_argument('--key',type=Path,required=True);p.add_argument('--board',choices=['s3','c3']);p.add_argument('--image',type=Path);p.add_argument('--output',type=Path);p.add_argument('--tag',help='Also write online manifest and raw binary for this GitHub release tag');a=p.parse_args()
    # Key creation is deliberately separate from builds: never silently change the trust root.
    if a.action=='keygen':
        if a.key.exists():p.error('Key already exists; refusing to replace it')
        key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        a.key.parent.mkdir(parents=True,exist_ok=True)
        a.key.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
        public=key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        (ROOT/'DragonPrototype/UpdatePublicKey.h').write_text('#pragma once\n// Public release verification key. Private key is never shipped.\nstatic const char DRAGON_UPDATE_PUBLIC_KEY[]=R"KEY('+public+')KEY";\n')
    else:
        if not(a.board and a.image and a.output):p.error('sign requires --board, --image and --output')
        key=serialization.load_pem_private_key(a.key.read_bytes(),password=None)
        a.output.parent.mkdir(parents=True,exist_ok=True);pkg=package(a.image,a.board,key);a.output.write_text(json.dumps(pkg,separators=(',',':')))
        if a.tag:
            (a.output.parent/f'dragon-{a.board}.manifest').write_text(online_manifest(pkg,a.tag,key),encoding='ascii')
            (a.output.parent/f'dragon-{a.board}.bin').write_bytes(a.image.read_bytes())
if __name__=='__main__':main()
