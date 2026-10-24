import hashlib, json, struct, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import recovery
import sign_update
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa,padding

def partition_table():
    entries=[('nvs',1,2,0x9000,0x5000),('otadata',1,0,0xe000,0x2000),('app0',0,0x10,0x10000,0x180000),('app1',0,0x11,0x190000,0x180000)]
    return b''.join(struct.pack('<HBBII16sI',0x50aa,t,sub,at,size,name.encode(),0) for name,t,sub,at,size in entries)+b'\xff'*32

class ReleaseTests(unittest.TestCase):
    def test_real_rsa_signature_binds_board_size_and_image_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            image=Path(temp)/'image.bin';image.write_bytes(b'firmware image')
            key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
            pkg=sign_update.package(image,'s3',key);signature=bytes.fromhex(pkg['signature'])
            key.public_key().verify(signature,sign_update.canonical('s3',pkg['size'],pkg['sha256']),padding.PKCS1v15(),hashes.SHA256())
            for board,size,digest in [('c3',pkg['size'],pkg['sha256']),('s3',pkg['size']+1,pkg['sha256']),('s3',pkg['size'],'0'*64)]:
                with self.assertRaises(InvalidSignature):key.public_key().verify(signature,sign_update.canonical(board,size,digest),padding.PKCS1v15(),hashes.SHA256())
            self.assertEqual(hashlib.sha256(bytes.fromhex(pkg['image'])).hexdigest(),pkg['sha256'])
    def test_online_signature_binds_release_tag(self):
        key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        pkg={'board':'s3','size':512,'sha256':'0'*64}
        manifest=sign_update.online_manifest(pkg,'v0.3.1',key)
        fields=manifest.splitlines();message='\n'.join(fields[:5])+'\n';signature=bytes.fromhex(fields[5])
        key.public_key().verify(signature,message.encode(),padding.PKCS1v15(),hashes.SHA256())
        with self.assertRaises(InvalidSignature):key.public_key().verify(signature,message.replace('v0.3.1','v0.3.2').encode(),padding.PKCS1v15(),hashes.SHA256())
        with self.assertRaises(ValueError):sign_update.online_manifest(pkg,'../../other',key)
    def test_partition_layout_preserves_nvs_and_two_slots(self):
        self.assertEqual(recovery.validate_partitions(partition_table())['nvs'],(1,2,0x9000,0x5000))
        recovery.validate_current_nvs(partition_table())
        with self.assertRaises(ValueError):recovery.validate_current_nvs(b'\xff'*4096)
        old=struct.pack('<HBBII16sI',0x50aa,0,0,0x10000,0x180000,b'app0',0)
        with self.assertRaises(ValueError):recovery.validate_partitions(old)
    def test_no_probe_without_usb_only_confirmation(self):
        with patch.object(recovery,'detect_board') as detect:
            with self.assertRaises(ValueError):recovery.recover('cli','COM-test',False)
            detect.assert_not_called()
    def test_recovery_reads_and_verifies_nvs_without_writing_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);build=root/'bundle';build.mkdir()
            for f in recovery.FILES:(build/f).write_bytes(b'app')
            (build/recovery.FILES[2]).write_bytes(partition_table());calls=[]
            original=bytes(range(256))*80
            def run(args,**kwargs):
                calls.append(args)
                if 'read-flash' in args:Path(args[-1]).write_bytes(partition_table() if args[args.index('read-flash')+1]=='0x8000' else original)
                return type('Result',(),{'returncode':0,'stderr':''})()
            with patch.object(recovery,'ROOT',root),patch.object(recovery,'detect_board',return_value='c3'),patch.object(recovery,'load_bundle',return_value=build),patch.object(recovery,'esptool_path',return_value=Path('esptool')),patch.object(recovery.subprocess,'run',side_effect=run),patch.object(recovery,'check_startup') as startup:
                session=recovery.recover('cli','COM-test',True,lambda text:None)
            write=next(c for c in calls if 'write-flash' in c)
            self.assertEqual(write[write.index('write-flash')+1::2],['0x0','0x8000','0xe000','0x10000'])
            self.assertEqual((session/'nvs-before.bin').read_bytes(),(session/'nvs-after.bin').read_bytes())
            startup.assert_called_once()
if __name__=='__main__':unittest.main()
