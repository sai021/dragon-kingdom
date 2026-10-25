import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import updater_core as c
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
IMAGE = bytes(range(256)) * 5
DIGEST = hashlib.sha256(IMAGE).hexdigest()

def fixtures(board='s3', old=True):
    info = {'contract': 2, 'saved_schema': 1, 'capabilities': 1, 'source_commit': 'a'*40,
            'firmware_tag': 'v0.3.1', 'targets': {b: {'sha256': {'DragonPrototype.ino.bin': DIGEST}} for b in ('s3', 'c3')}}
    info['signature'] = KEY.sign(json.dumps(info, sort_keys=True, separators=(',', ':')).encode(), padding.PKCS1v15(), hashes.SHA256()).hex()
    pkg = {'format': 1 if old else 2, 'board': board, 'size': len(IMAGE), 'sha256': DIGEST, 'image': IMAGE.hex()}
    if old: message = f'dragon-update-v1\n{board}\n{len(IMAGE)}\n{DIGEST}\n'
    else:
        pkg.update(tag='v0.3.1', capabilities=1, schema=1)
        message = f'dragon-update-v2\n{board}\nv0.3.1\n{len(IMAGE)}\n{DIGEST}\n1\n1\n'
    pkg['signature'] = KEY.sign(message.encode(), padding.PKCS1v15(), hashes.SHA256()).hex()
    return info, pkg

class Lamp:
    def __init__(self, board='s3', old=True, fault=None):
        self.board, self.old, self.fault = board, old, fault
        self.firmware = 'v0.3.0-beta.3' if old else 'v0.3.0-beta.9'
        self.hostname = 'Dragon-Kingdom-aabbcc'
        self.active, self.offset, self.started, self.finished, self.aborted = False, 0, 0, 0, 0
        self.written = bytearray(); self.token = 'a'*64
        self.backup = {'format': 'dragon-backup-v1', 'data': ('00'*908)}
        self.paths = []

    def handle(self, path, data, token):
        self.paths.append(path)
        if path == '/api/state': return 200, dict(hostname=self.hostname, board=self.board, firmware=self.firmware,
            connected=self.fault=='ap-moves-home', ip='192.168.0.99' if self.fault=='ap-moves-home' else '')
        if path == '/api/parent/login':
            return (200, {'token': self.token}) if data.get('password') == 'correct' else (401, {})
        if token != self.token: return 401, {}
        if path == '/api/parent/logout': return 200, {}
        if path == '/api/backup':
            backup = copy.deepcopy(self.backup)
            if self.finished and self.fault == 'settings': backup['data'] = '01' + backup['data'][2:]
            return 200, backup
        if path == '/api/support': return 200, {'validated': True, 'otaState': 2}
        if path == '/api/update': return 200, dict(board=self.board, active=self.active, offset=self.offset)
        if path == '/api/update/start':
            if (self.old and 'format' in data) or (not self.old and data.get('format') != '2'): return 409, {}
            self.started += 1; self.active = True
            if self.fault == 'start-reply': self.fault = None; return None, None
            return 200, {'offset': 0}
        if path == '/api/update/chunk':
            at = int(data['offset']); raw = bytes.fromhex(data['data'])
            if at != self.offset: return 409, {}  # Beta 3 has no duplicate ACK support.
            if self.fault == 'before-chunk': self.fault = None; return None, None
            self.written.extend(raw); self.offset += len(raw)
            if self.fault == 'after-chunk': self.fault = None; return None, None
            return 200, {'offset': self.offset}
        if path == '/api/update/abort': self.aborted += 1; self.active = False; return 200, {}
        if path == '/api/update/finish':
            if self.offset != len(IMAGE): return 409, {}
            self.finished += 1; self.active = False
            if self.fault != 'rollback': self.firmware = 'v0.3.1'
            if self.fault == 'finish-reply': return None, None
            return 200, {'restarting': True}
        return 404, {}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self): self.process()
    def do_POST(self): self.process()
    def process(self):
        raw = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        data = {k: v[0] for k, v in parse_qs(raw.decode()).items()}
        status, body = self.server.lamp.handle(self.path, data, self.headers.get('X-Dragon-Parent'))
        if status is None:
            self.close_connection = True; return
        result = json.dumps(body).encode()
        self.send_response(status); self.send_header('Content-Length', str(len(result))); self.end_headers(); self.wfile.write(result)

class Tests(unittest.TestCase):
    def exercise(self, board='s3', old=True, fault=None, cancel_at=None, wrong_password=False, offline=False):
        lamp = Lamp(board, old, fault)
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler); server.lamp = lamp
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        address = f'http://127.0.0.1:{server.server_port}'
        self.lamp = lamp
        self.addresses = []
        def client_factory(addr):
            self.addresses.append(addr)
            class SimulatedAPClient(c.Client):
                def call(inner, path, data=None):
                    if fault=='ap-moves-home' and lamp.finished and addr==address:
                        raise c.UpdateError('Setup AP disappeared after restart')
                    return super().call(path,data)
            return SimulatedAPClient(address, timeout=1, allow_loopback=True)
        try:
            info, pkg = fixtures(board, old)
            release = c.Release('v0.3.1', info)
            if offline:
                packages = {f'{b}-{kind}': fixtures(b, old_format)[1] for b in ('s3','c3') for old_format,kind in ((True,'bridge'),(False,'normal'))}
                release = c.PreparedRelease('v0.3.1', info, packages)
            cancel = threading.Event()
            def progress(text, percent):
                if cancel_at is not None and percent >= cancel_at: cancel.set()
            with tempfile.TemporaryDirectory() as tmp, patch.object(c, 'trust_key', return_value=KEY.public_key()), patch.object(c, 'download_json', side_effect=AssertionError('No public network during offline transfer')), patch.object(c.Release, 'package', lambda self, d: c.verify_package(pkg, info, d.board, c.legacy(d.firmware), KEY.public_key())):
                result = c.update(c.Device.probe(address, allow_loopback=True), release,
                    'wrong' if wrong_password else 'correct', progress, cancel, backups=tmp,
                    client_factory=client_factory, reboot_timeout=.2, poll_interval=.01)
                self.assertTrue(Path(result['backup']).exists())
                self.assertEqual(json.loads(Path(result['backup']).read_text()), lamp.backup)
                self.assertEqual(bytes(lamp.written), IMAGE)
                self.assertEqual(lamp.finished, 1)
                return result
        finally: server.shutdown(); server.server_close(); thread.join()

    def test_beta3_both_boards(self):
        for board in ('s3', 'c3'):
            with self.subTest(board=board): self.exercise(board)
    def test_current_format_both_boards(self):
        for board in ('s3', 'c3'):
            with self.subTest(board=board): self.exercise(board, old=False)
    def test_offline_transfer_without_public_network_both_boards_formats(self):
        for board in ('s3','c3'):
            for old in (True,False):
                with self.subTest(board=board,old=old): self.exercise(board,old=old,offline=True)
    def test_direct_restart_follows_saved_home_address_if_ap_disappears(self):
        self.exercise(offline=True,fault='ap-moves-home')
        self.assertIn('http://192.168.0.99',self.addresses)
    def test_lost_ack_after_write_does_not_duplicate(self): self.exercise(fault='after-chunk')
    def test_lost_ack_before_write_retries(self): self.exercise(fault='before-chunk')
    def test_lost_start_reply_recovers(self): self.exercise(fault='start-reply')
    def test_lost_final_reply_checks_startup(self): self.exercise(fault='finish-reply')
    def test_cancel_last_chunk_prevents_finalization(self):
        with self.assertRaises(c.Cancelled): self.exercise(cancel_at=85)
        self.assertEqual(self.lamp.finished, 0); self.assertEqual(self.lamp.aborted, 1)
    def test_bad_password_never_starts(self):
        with self.assertRaises(c.RPCError): self.exercise(wrong_password=True)
        self.assertEqual(self.lamp.started, 0)
    def test_rollback_never_reports_success(self):
        with self.assertRaisesRegex(c.UpdateError, 'Restart could not'): self.exercise(fault='rollback')
    def test_settings_change_never_reports_success(self):
        with self.assertRaisesRegex(c.UpdateError, 'saved settings differ'): self.exercise(fault='settings')
    def test_signed_contract_and_packages(self):
        for old in (True, False):
            info, pkg = fixtures(old=old)
            c.verify_contract(info, KEY.public_key()); c.verify_package(pkg, info, 's3', old, KEY.public_key())
            for field, value in [('board', 'c3'), ('signature', '00'*256), ('image', 'ff'*len(IMAGE)), ('size', len(IMAGE)+1), ('format', 99)]:
                bad = dict(pkg, **{field: value})
                with self.subTest(old=old, field=field), self.assertRaises(c.UpdateError): c.verify_package(bad, info, 's3', old, KEY.public_key())
        bad = dict(info, capabilities=0)
        with self.assertRaises(c.UpdateError): c.verify_contract(bad, KEY.public_key())
    def test_version_policy(self):
        self.assertTrue(c.legacy('v0.3.0-beta.3')); self.assertFalse(c.legacy('v0.3.0-beta.9'))
        self.assertTrue(c.version('v0.3.1') > c.version('v0.3.0-beta.9'))
        with self.assertRaises(c.UpdateError): c.legacy('v0.2.4')
        device = c.Device('http://192.168.0.10', 'Dragon-Kingdom-aabbcc', 's3', 'v0.3.1')
        with patch.object(c.Release, 'package', side_effect=AssertionError('Must reject before downloading')):
            with self.assertRaises(c.UpdateError): c.update(device, c.Release('v0.3.1', {}), 'correct')
    def test_local_url_boundary_and_redirect(self):
        for value in ('https://192.168.0.1', 'http://8.8.8.8', '127.0.0.1', 'http://192.168.0.1:8080', 'http://user:secret@192.168.0.1', 'http://192.168.0.1/evil'):
            with self.subTest(value=value), self.assertRaises(c.UpdateError): c.local_address(value)
        self.assertIsNone(c.NoLocalRedirect().redirect_request(None, None, None, None, None, None))
        self.assertFalse(c.public_url('http://github.com/sai021/dragon-kingdom/releases/a'))
        self.assertFalse(c.public_url('https://github.com/other/repo/releases/a'))
        self.assertTrue(c.public_url('https://github.com/sai021/dragon-kingdom/releases/download/v0.3.1/a'))
    def test_installed_trust_root(self): self.assertEqual(c.trust_key().key_size, 2048)
    def test_tls_keeps_certificate_and_hostname_validation(self):
        import ssl
        context = c.tls_context()
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)
        self.assertGreater(len(context.get_ca_certs()), 50)

if __name__ == '__main__': unittest.main()
