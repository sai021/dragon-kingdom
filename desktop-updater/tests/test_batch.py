import sys
from pathlib import Path
import threading
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import batch_update as batch
import updater_core as core
from wifi_control import Network


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.networks = [Network('Dragon-Kingdom-00000' + str(i), 80, 'radio') for i in range(1, 5)]
        self.session = Mock(changed=False)
        self.session.adapter.scan.return_value = self.networks
        self.release = core.PreparedRelease('v0.3.1', {}, {})
        self.cancel = threading.Event()

    def device(self, network, version='v0.3.0-beta.3', board='s3'):
        return core.Device('http://192.168.4.1', network.ssid, board, version)

    def run_batch(self):
        return batch.run(self.session, self.release, 'dragon123', self.cancel)

    def test_mixed_boards_skip_current_newer_and_deduplicate(self):
        self.session.adapter.scan.return_value += [self.networks[0]]
        devices = [self.device(self.networks[0]), self.device(self.networks[1], board='c3'),
                   self.device(self.networks[2], 'v0.3.1'), self.device(self.networks[3], 'v0.3.2-beta.1')]
        def updated(device, *args, **kwargs):
            return dict(address=device.address, firmware='v0.3.1', backup='private-backup')
        with patch('batch_update.probe_network', side_effect=devices), patch('batch_update.core.update', side_effect=updated) as update:
            results = self.run_batch()
        self.assertEqual([r.status for r in results], ['Updated', 'Updated', 'Already current', 'Newer installed'])
        self.assertEqual(update.call_count, 2)
        self.assertEqual([c.args[0].board for c in update.call_args_list], ['s3', 'c3'])
        self.assertTrue(all(c.kwargs['direct'] for c in update.call_args_list))
        self.assertEqual(self.session.join.call_count, 4)
        self.assertEqual(self.session.restore.call_count, 4)

    def test_failure_continues_only_after_restoring_wifi(self):
        self.session.adapter.scan.return_value = self.networks[:2]
        with patch('batch_update.probe_network', side_effect=[core.UpdateError('Wrong identity'), self.device(self.networks[1], 'v0.3.1')]), patch('batch_update.core.update') as update:
            results = self.run_batch()
        self.assertEqual([r.status for r in results], ['Needs attention', 'Already current'])
        self.assertEqual(self.session.restore.call_count, 2)
        update.assert_not_called()

    def test_restore_failure_stops_remaining_lamps_but_keeps_verified_result(self):
        self.session.restore.side_effect = core.UpdateError('Restoration denied')
        with patch('batch_update.probe_network', return_value=self.device(self.networks[0])), patch('batch_update.core.update', return_value=dict(address='http://192.168.4.1', firmware='v0.3.1', backup='private')):
            results = self.run_batch()
        self.assertEqual(results[0].status, 'Updated')
        self.assertIn('batch stopped', results[0].detail)
        self.assertEqual([r.status for r in results[1:]], ['Not attempted'] * 3)
        self.session.join.assert_called_once()

    def test_stop_during_final_verification_finishes_current_and_skips_rest(self):
        def finalized(*args, **kwargs):
            self.cancel.set()
            return dict(address='http://192.168.4.1', firmware='v0.3.1', backup='private')
        with patch('batch_update.probe_network', return_value=self.device(self.networks[0])), patch('batch_update.core.update', side_effect=finalized):
            results = self.run_batch()
        self.assertEqual([r.status for r in results], ['Updated'] + ['Not attempted'] * 3)
        self.session.restore.assert_called_once()

    def test_cancel_before_finalization_restores_and_stops(self):
        with patch('batch_update.probe_network', return_value=self.device(self.networks[0])), patch('batch_update.core.update', side_effect=core.Cancelled('Aborted safely')):
            results = self.run_batch()
        self.assertEqual([r.status for r in results], ['Stopped'] + ['Not attempted'] * 3)
        self.session.restore.assert_called_once()

    def test_requires_offline_files_before_scanning_or_switching_wifi(self):
        self.release = Mock()
        with self.assertRaises(core.UpdateError): self.run_batch()
        self.session.adapter.scan.assert_not_called()
        self.session.join.assert_not_called()

    def test_probe_rejects_another_lamp_on_same_address(self):
        with patch('batch_update.core.Device.probe', return_value=self.device(self.networks[1])):
            with self.assertRaisesRegex(core.UpdateError, 'identity'):
                batch.probe_network(self.networks[0], self.cancel)
