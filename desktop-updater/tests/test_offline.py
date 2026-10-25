import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import updater_core as c
from test_updater import KEY,fixtures


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.key_patch=patch.object(c,'trust_key',return_value=KEY.public_key()); self.key_patch.start()
        self.download_patch=patch.object(c.Release,'package',lambda self,d: fixtures(d.board,c.legacy(d.firmware))[1]);self.download_patch.start()
        self.temp=tempfile.TemporaryDirectory();self.folder=Path(self.temp.name)
        self.release=c.Release('v0.3.1',fixtures()[0])
    def tearDown(self):
        self.download_patch.stop();self.key_patch.stop();self.temp.cleanup()
    def test_prepare_restart_load_all_boards_formats_without_internet(self):
        prepared=c.prepare_offline(self.release,self.folder)
        self.assertEqual(prepared.tag,'v0.3.1')
        with patch.object(c,'download_json',side_effect=AssertionError('Internet is unavailable')):
            loaded=c.PreparedRelease.load(self.folder)
            for board in ('s3','c3'):
                for tag,fmt in (('v0.3.0-beta.3',1),('v0.3.0-beta.9',2)):
                    d=c.Device('http://192.168.4.1','Dragon-Kingdom-aabbcc',board,tag)
                    self.assertEqual(loaded.package(d)['format'],fmt)
    def test_interrupted_download_keeps_previous_complete_cache(self):
        c.prepare_offline(self.release,self.folder)
        before=(self.folder/'offline-release.json').read_bytes()
        with patch.object(c.Release,'package',side_effect=c.UpdateError('Connection lost')):
            with self.assertRaises(c.UpdateError):c.prepare_offline(self.release,self.folder)
        self.assertEqual((self.folder/'offline-release.json').read_bytes(),before)
        self.assertEqual(c.PreparedRelease.load(self.folder).tag,'v0.3.1')
    def test_altered_missing_truncated_cache_fails_closed(self):
        c.prepare_offline(self.release,self.folder)
        path=self.folder/'offline-release.json';good=json.loads(path.read_text())
        damaged=copy.deepcopy(good);damaged['packages']['c3-normal']['image']='00'
        missing=copy.deepcopy(good);del missing['packages']['s3-bridge']
        contract=copy.deepcopy(good);contract['release']['capabilities']=0
        for value in (damaged,missing,contract):
            path.write_text(json.dumps(value))
            with self.assertRaises(c.UpdateError):c.PreparedRelease.load(self.folder)
        path.write_text('{')
        with self.assertRaises(c.UpdateError):c.PreparedRelease.load(self.folder)
    def test_missing_cache_requests_download_without_network(self):
        with patch.object(c,'download_json',side_effect=AssertionError('No automatic network fallback')):
            with self.assertRaisesRegex(c.UpdateError,'choose a firmware file'):c.PreparedRelease.load(self.folder)

if __name__=='__main__':unittest.main()
