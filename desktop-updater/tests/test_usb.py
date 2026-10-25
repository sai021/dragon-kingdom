import copy
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import updater_core as core
import usb_update as usb
from test_updater import KEY
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def fixture():
    recovery = usb.service()
    targets, files = {}, {}
    partitions = b''.join(struct.pack('<HBBII16sI', 0x50aa, kind, sub, offset, size, name.encode(), 0)
        for name, kind, sub, offset, size in [('nvs', 1, 2, 0x9000, 0x5000), ('otadata', 1, 0, 0xe000, 0x2000),
            ('app0', 0, 0x10, 0x10000, 0x180000), ('app1', 0, 0x11, 0x190000, 0x180000)])
    for board, chip in [('s3', 9), ('c3', 5)]:
        raw = bytearray(64); raw[0] = 0xe9; raw[12:14] = chip.to_bytes(2, 'little'); raw[23] = 1
        image = bytes(raw) + hashlib.sha256(raw).digest()
        values = {usb.FILES[0]: image, usb.FILES[1]: image, usb.FILES[2]: partitions}
        files.update({board + '/' + name: value for name, value in values.items()})
        targets[board] = dict(directory=board, fqbn=recovery.TARGETS[board], sha256={k: hashlib.sha256(v).hexdigest() for k, v in values.items()})
    info = dict(schema=1, contract=2, firmware_tag='v0.3.1', source_commit='a'*40, saved_schema=1, capabilities=1, targets=targets)
    info['signature'] = KEY.sign(json.dumps(info, sort_keys=True, separators=(',', ':')).encode(), padding.PKCS1v15(), hashes.SHA256()).hex()
    files['current-set.json'] = json.dumps(info).encode()
    return core.Release('v0.3.1', info), files


def archive(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as z:
        for name, value in files.items(): z.writestr(name, value)
    return output.getvalue()


class UsbTests(unittest.TestCase):
    def setUp(self):
        self.key = patch.object(core, 'trust_key', return_value=KEY.public_key())
        self.key.start(); self.addCleanup(self.key.stop)
        self.release, self.files = fixture()
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name)

    def prepare(self, files=None):
        opener = Mock()
        opener.open.return_value = io.BytesIO(archive(self.files if files is None else files))
        with patch.object(usb.urllib.request, 'build_opener', return_value=opener):
            return usb.prepare(self.release, self.cache)

    def test_signed_two_board_download_and_offline_reuse(self):
        folder = self.prepare()
        with patch.object(usb.urllib.request, 'build_opener', side_effect=AssertionError('Offline')):
            self.assertEqual(usb.prepare(self.release, self.cache), folder)
        self.assertEqual(usb.service().prepared_release(folder), self.release.info)

    def test_tampered_or_extra_paths_never_publish(self):
        for change in ('image', 'traversal', 'signature'):
            bad = copy.deepcopy(self.files)
            if change == 'image': bad['s3/' + usb.FILES[0]] = b'bad image'
            elif change == 'traversal': bad['../outside'] = b'bad'
            else: bad['current-set.json'] = b'{}'
            with self.subTest(change=change), self.assertRaises(Exception): self.prepare(bad)
            self.assertFalse((self.cache / self.release.tag).exists())

    def test_power_confirmation_and_current_port_required_before_serial_access(self):
        folder = self.prepare()
        recovery = usb.service()
        with patch.object(recovery, 'read_running_version') as read, patch.object(usb, 'ports', return_value=[]):
            with self.assertRaises(core.UpdateError): usb.update('COM17', self.release, folder, False)
            with self.assertRaisesRegex(core.UpdateError, 'disappeared'): usb.update('COM17', self.release, folder, True)
            read.assert_not_called()

    def test_newer_usb_firmware_skips_without_reset_or_flash(self):
        folder = self.prepare(); recovery = usb.service()
        with patch.object(usb, 'ports', return_value=[SimpleNamespace(device='COM17')]), \
             patch.object(usb, 'helper', return_value=Path('helper')), \
             patch.object(recovery, 'read_running_version', return_value='v0.3.2'), \
             patch.object(recovery, 'update_if_newer') as update:
            result = usb.update('COM17', self.release, folder, True)
        self.assertIn('no downgrade', result)
        update.assert_not_called()

    def test_usb_uses_reviewed_recovery_with_explicit_bundle_and_helper(self):
        folder = self.prepare(); recovery = usb.service()
        with patch.object(usb, 'ports', return_value=[SimpleNamespace(device='COM17')]), \
             patch.object(usb, 'helper', return_value=Path('helper')), \
             patch.object(recovery, 'read_running_version', return_value='v0.3.0-beta.3'), \
             patch.object(recovery, 'update_if_newer', return_value='Updated') as update:
            self.assertTrue(usb.update('COM17', self.release, folder, True).startswith('Updated'))
        self.assertTrue(update.call_args.args[2])
        self.assertEqual(update.call_args.kwargs['cache'], folder)
        self.assertEqual(update.call_args.kwargs['tool'], Path('helper'))

    def test_reenumeration_does_not_start_another_usb_update(self):
        gate = usb.gate(); gate.arm()
        self.assertEqual(gate.choose({'COM17'}, now=0), 'COM17')
        gate.finished(now=1)
        self.assertIsNone(gate.choose({'COM18'}, now=5))
        self.assertIsNone(gate.choose({'COM18'}, now=6))
        self.assertTrue(gate.waiting)
        self.assertIsNone(gate.choose(set(), now=7))
        self.assertIsNone(gate.choose(set(), now=8))
        self.assertFalse(gate.waiting)
        self.assertEqual(gate.choose({'COM19'}, now=9), 'COM19')

    def test_fresh_selection_authorizes_replacement_and_propagates_backup_prompt(self):
        folder=self.prepare();recovery=usb.service();decision=Mock(return_value=True)
        with patch.object(usb,'ports',return_value=[SimpleNamespace(device='COM17')]), \
             patch.object(usb,'helper',return_value=Path('helper')), patch.object(recovery,'install_fresh',return_value='Updated') as fresh:
            usb.update('COM17',self.release,folder,True,fresh=True,backup_decision=decision)
        self.assertTrue(fresh.call_args.kwargs['replace_existing'])
        self.assertIs(fresh.call_args.kwargs['backup_decision'],decision)

    def test_missing_runtime_checks_for_fully_blank_flash_without_authorizing_erasure(self):
        folder=self.prepare();recovery=usb.service()
        with patch.object(usb,'ports',return_value=[SimpleNamespace(device='COM17')]), \
             patch.object(usb,'helper',return_value=Path('helper')), \
             patch.object(recovery,'read_running_version',side_effect=RuntimeError('No runtime')), \
             patch.object(recovery,'install_fresh',return_value='Updated empty board') as fresh:
            usb.update('COM17',self.release,folder,True)
        self.assertFalse(fresh.call_args.kwargs['replace_existing'])
