"""Signed USB release contract. No serial access or private-key discovery."""
import json
import re
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

ROOT = Path(__file__).resolve().parents[1]

def canonical(info):
    return json.dumps({k:v for k,v in info.items() if k!='signature'},sort_keys=True,separators=(',',':')).encode('ascii')

def public_key():
    header=(ROOT/'DragonPrototype/UpdatePublicKey.h').read_text()
    pem=re.search(r'-----BEGIN PUBLIC KEY-----.*?-----END PUBLIC KEY-----',header,re.S)
    if not pem:raise ValueError('Missing existing trust root')
    return serialization.load_pem_public_key(pem[0].encode())

def verify(info):
    public_key().verify(bytes.fromhex(info['signature']),canonical(info),padding.PKCS1v15(),hashes.SHA256())
    if info.get('contract')!=2 or info.get('saved_schema')!=1 or info.get('capabilities',0)&1!=1:
        raise ValueError('USB service requires signed calibration-aware schema-1 firmware, including when current calibration is unknown.')
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-beta\.\d+)?',info.get('firmware_tag','')):
        raise ValueError('Missing expected firmware tag')
    if not re.fullmatch('[0-9a-f]{40}',info.get('source_commit','')):raise ValueError('Missing source commit')
    return info
