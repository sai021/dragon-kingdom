import sys
import gc
from pathlib import Path
import tkinter as tk
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import App
import updater_core as core


class EasyUpdateTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = App(self.root, online=False)

    def tearDown(self):
        for callback in self.root.tk.call('after', 'info'):
            self.root.after_cancel(callback)
        self.root.destroy()
        del self.app
        del self.root
        # Tk objects must be collected here, never by later HTTP server threads.
        gc.collect()

    def test_launch_defaults_and_editable_password(self):
        self.assertTrue(self.app.is_direct())
        self.assertEqual(self.app.password.get(), 'dragon123')
        self.assertEqual(str(self.app.password['state']), 'normal')
        self.app.password.delete(0, 'end')
        self.app.password.insert(0, 'different-password')
        self.app.mode.set('Home Wi-Fi')
        self.app.change_mode()
        self.assertEqual(self.app.password.get(), 'different-password')

    def test_one_update_click_uses_default_or_edited_password(self):
        for password in ('dragon123', 'different-password'):
            with self.subTest(password=password):
                self.app.password.delete(0, 'end')
                self.app.password.insert(0, password)
                device = core.Device('http://192.168.4.1', 'Dragon-Kingdom-aabbcc', 's3', 'v0.3.0-beta.3')
                self.app.show_devices([device])
                self.app.release = SimpleNamespace(tag='v0.3.1')
                result = dict(firmware='v0.3.1', backup='private-backup', address=device.address)
                with patch('main.messagebox.askokcancel', side_effect=AssertionError('Extra confirmation')), \
                     patch('main.messagebox.showinfo'), \
                     patch('main.core.update', return_value=result) as update, \
                     patch.object(self.app, 'run', side_effect=lambda job, done: done(job())):
                    self.app.install_selected()
                self.assertEqual(update.call_args.args[2], password)
                self.assertTrue(update.call_args.kwargs['direct'])
                self.assertEqual(self.app.password.get(), password)
                self.assertEqual(self.app.devices[0].firmware, 'v0.3.1')

    def test_startup_refresh_downloads_without_installing(self):
        latest = SimpleNamespace(tag='v0.3.1', info={})
        with patch.object(self.app, 'run', side_effect=lambda job, done: done(job())), \
             patch('main.core.PreparedRelease.load', side_effect=core.UpdateError('No cache')), \
             patch('main.core.Release.latest', return_value=latest), \
             patch('main.core.prepare_offline', return_value=latest) as prepare, \
             patch('main.core.update') as update, patch('main.wifi.controller') as controller:
            self.app.startup_refresh()
        prepare.assert_called_once()
        update.assert_not_called()
        controller.assert_not_called()
        self.assertIs(self.app.prepared, latest)

    def test_startup_offline_retains_verified_cache(self):
        cached = SimpleNamespace(tag='v0.3.1', info={})
        with patch.object(self.app, 'run', side_effect=lambda job, done: done(job())), \
             patch('main.core.PreparedRelease.load', return_value=cached), \
             patch('main.core.Release.latest', side_effect=core.UpdateError('Offline')), \
             patch('main.core.prepare_offline') as prepare:
            self.app.startup_refresh()
        prepare.assert_not_called()
        self.assertIs(self.app.prepared, cached)
        self.assertIn('may not be the newest', self.app.status.get())

    def test_startup_does_not_redownload_complete_current_release(self):
        cached = SimpleNamespace(tag='v0.3.1', info={})
        with patch.object(self.app, 'run', side_effect=lambda job, done: done(job())), \
             patch('main.core.PreparedRelease.load', return_value=cached), \
             patch('main.core.Release.latest', return_value=cached), \
             patch('main.core.prepare_offline') as prepare:
            self.app.startup_refresh()
        prepare.assert_not_called()

    def test_failed_startup_download_preserves_previous_complete_release(self):
        cached = SimpleNamespace(tag='v0.3.1', info={})
        latest = SimpleNamespace(tag='v0.3.2', info={})
        with patch.object(self.app, 'run', side_effect=lambda job, done: done(job())), \
             patch('main.core.PreparedRelease.load', return_value=cached), \
             patch('main.core.Release.latest', return_value=latest), \
             patch('main.core.prepare_offline', side_effect=core.UpdateError('Download interrupted')):
            self.app.startup_refresh()
        self.assertIs(self.app.prepared, cached)
        self.assertIn('may not be the newest', self.app.status.get())

    def test_result_rows_remain_safe_for_manual_update_selection(self):
        import batch_update
        device = core.Device('http://192.168.4.1', 'Dragon-Kingdom-aabbcc', 's3', 'v0.3.1')
        self.app.release = SimpleNamespace(tag='v0.3.1')
        self.app.show_batch_result(batch_update.Result('Dragon-Kingdom-000000', 'Needs attention', 'Unavailable'))
        unknown = self.app.tree.get_children()[0]
        self.app.tree.selection_set(unknown)
        with patch('main.messagebox.showinfo'):
            self.app.install_selected()
        self.app.show_batch_result(batch_update.Result(device.hostname, 'Already current', 'Skipped', device))
        self.assertEqual(self.app.devices[0], device)
        self.assertEqual(self.app.tree.item('0')['values'][0], device.hostname)

    def test_batch_button_runs_all_without_selection_dialog(self):
        self.app.prepared = core.PreparedRelease('v0.3.1', {}, {})
        self.app.wifi_session = SimpleNamespace(changed=False)
        with patch.object(self.app, 'run', side_effect=lambda job, done: done(job())), \
             patch('main.batch.run', return_value=[]) as run, \
             patch('main.messagebox.showinfo') as info:
            self.app.find_devices()
        run.assert_called_once()
        self.assertEqual(run.call_args.args[2], 'dragon123')
        info.assert_not_called()

    def test_usb_auto_requires_batch_power_and_prepared_bundle(self):
        self.app.mode.set('USB cable'); self.app.change_mode()
        self.app.usb_auto.set(True)
        with patch.object(self.app, 'prepare_usb') as prepare:
            self.app.toggle_usb_auto()
        prepare.assert_not_called()
        self.assertFalse(self.app.usb_gate.enabled)
        self.app.usb_power.set(True); self.app.usb_auto.set(True)
        with patch.object(self.app, 'prepare_usb', side_effect=lambda after: after()):
            self.app.toggle_usb_auto()
        self.assertTrue(self.app.usb_gate.enabled)
        self.app.request_stop()
        self.assertFalse(self.app.usb_gate.enabled)

    def test_usb_auto_runs_once_then_waits_for_unplug(self):
        self.app.mode.set('USB cable'); self.app.change_mode()
        self.app.usb_power.set(True); self.app.usb_auto.set(True); self.app.usb_gate.arm()
        port = SimpleNamespace(device='COM17', vid=0x303a)
        def installing(automatic):
            self.assertTrue(automatic)
            self.app.usb_gate.finished(now=0)
        with patch('main.usb.ports', return_value=[port]), patch.object(self.app, 'install_usb', side_effect=installing) as update:
            self.app.usb_tick(); self.app.usb_tick()
        update.assert_called_once()
