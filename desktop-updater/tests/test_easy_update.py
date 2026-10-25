import sys
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
        self.root.destroy()

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
