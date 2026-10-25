"""Verify local imports without network or hardware access."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import updater_core as core
import usb_update as usb
import firmware_files
from test_usb import fixture, archive
from test_updater import KEY


class FirmwareFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.addCleanup(patch.stopall)
        patch.object(core, 'trust_key', return_value=KEY.public_key()).start()
        patch.object(core, 'cache_folder', return_value=self.root/'cache').start()
        patch.object(usb, 'bundle_folder', return_value=self.root/'usb').start()
        patch.object(core, 'download_json', side_effect=AssertionError('Offline import accessed internet')).start()
        self.release, self.files = fixture()
        packages = {}
        for board in ('s3', 'c3'):
            image = self.files[board+'/'+usb.FILES[0]]
            digest = self.release.info['targets'][board]['sha256'][usb.FILES[0]]
            for old, kind in ((True, 'bridge'), (False, 'normal')):
                package = dict(format=1 if old else 2, board=board, size=len(image), sha256=digest, image=image.hex())
                if old:
                    message = f'dragon-update-v1\n{board}\n{len(image)}\n{digest}\n'
                else:
                    package.update(tag=self.release.tag, capabilities=1, schema=1)
                    message = f'dragon-update-v2\n{board}\n{self.release.tag}\n{len(image)}\n{digest}\n1\n1\n'
                package['signature'] = KEY.sign(message.encode(), padding.PKCS1v15(), hashes.SHA256()).hex()
                packages[board+'-'+kind] = package
        self.combined = {'usb/'+name: value for name, value in self.files.items()}
        self.combined['offline-release.json'] = json.dumps(dict(release=self.release.info, packages=packages)).encode()

    def file(self, files):
        path = self.root/'firmware.zip'; path.write_bytes(archive(files)); return path

    def test_complete_file_prepares_wifi_and_usb_without_network(self):
        prepared, release = firmware_files.load(self.file(self.combined))
        self.assertEqual(prepared.tag, self.release.tag)
        self.assertEqual(release.tag, self.release.tag)
        self.assertEqual(usb.cached_release().tag, self.release.tag)
        self.assertEqual(core.PreparedRelease.load().tag, self.release.tag)

    def test_usb_only_bundle_needs_no_internet(self):
        prepared, release = firmware_files.load(self.file(self.files))
        self.assertIsNone(prepared)
        self.assertEqual(release.tag, self.release.tag)

    def test_tampering_does_not_replace_existing_verified_cache(self):
        firmware_files.load(self.file(self.combined))
        before = (self.root/'cache/offline-release.json').read_bytes()
        bad = dict(self.combined); bad['usb/s3/'+usb.FILES[0]] = b'tampered'
        with self.assertRaises(Exception): firmware_files.load(self.file(bad))
        self.assertEqual((self.root/'cache/offline-release.json').read_bytes(), before)
        self.assertEqual(usb.cached_release().tag, self.release.tag)

    def test_unknown_or_duplicate_paths_are_rejected(self):
        bad = dict(self.combined); bad['../outside'] = b'bad'
        with self.assertRaises(core.UpdateError): firmware_files.load(self.file(bad))
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, 'w') as z:
            for name, value in self.combined.items(): z.writestr(name, value)
            z.writestr('usb/current-set.json', self.files['current-set.json'])
        path = self.root/'duplicate.zip'; path.write_bytes(raw.getvalue())
        with self.assertRaises(core.UpdateError): firmware_files.load(path)
        self.assertFalse((self.root/'cache').exists())
