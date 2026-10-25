"""Port discovery is independent of signed-bundle readiness and never flashes."""
import gc
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import recovery_gui


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


class RecoveryPortTests(unittest.TestCase):
    def test_ports_visible_without_selected_or_valid_bundle(self):
        for bundle_path in (None, Path('invalid-bundle')):
            with self.subTest(bundle=bundle_path), \
                 patch.object(recovery_gui, 'prepared_release', side_effect=ValueError('Bad signature')), \
                 patch.object(recovery_gui, 'serial_modules', return_value=(None, SimpleNamespace(comports=lambda: [SimpleNamespace(device='COM17')]))), \
                 patch.object(recovery_gui, 'recover') as flash:
                window = recovery_gui.create_window(visible=False, bundle_path=bundle_path)
                try:
                    widgets = list(descendants(window))
                    ports = next(w for w in widgets if w.winfo_class() == 'TCombobox')
                    self.assertEqual(tuple(ports['values']), ('COM17',))
                    self.assertEqual(ports.get(), 'COM17')
                    update = next(w for w in widgets if w.winfo_class() == 'TButton' and w['text'] == 'Update / recover firmware')
                    self.assertTrue(update.instate(['disabled']))
                    flash.assert_not_called()
                finally:
                    window.update_idletasks()
                    window.destroy()
            del widgets, ports, update, window
            gc.collect()

    def test_idle_hotplug_refreshes_and_clears_power_confirmation_without_flashing(self):
        detected = [SimpleNamespace(device='COM17', vid=0x303a)]
        listing = SimpleNamespace(comports=lambda: list(detected))
        with patch.object(recovery_gui, 'prepared_release', return_value={'firmware_tag': 'v0.3.1'}), \
             patch.object(recovery_gui, 'installed_esptool', return_value=Path(__file__)), \
             patch.object(recovery_gui, 'serial_modules', return_value=(None, listing)), \
             patch.object(recovery_gui, 'recover') as flash, \
             patch.object(recovery_gui, 'update_if_newer') as auto_flash:
            window = recovery_gui.create_window(visible=False, bundle_path=Path('signed-bundle'))
            try:
                widgets = list(descendants(window))
                ports = next(w for w in widgets if w.winfo_class() == 'TCombobox')
                safety = next(w for w in widgets if w.winfo_class() == 'TCheckbutton')
                safety.invoke()
                self.assertTrue(safety.instate(['selected']))
                detected[:] = [SimpleNamespace(device='COM18', vid=0x303a)]
                deadline = time.monotonic() + 2.5
                while ports.get() != 'COM18' and time.monotonic() < deadline:
                    window.update()
                    time.sleep(.01)
                self.assertEqual(ports.get(), 'COM18')
                self.assertFalse(safety.instate(['selected']))
                detected.clear()
                deadline = time.monotonic() + 2.5
                while ports.get() and time.monotonic() < deadline:
                    window.update()
                    time.sleep(.01)
                self.assertEqual(ports.get(), '')
                self.assertFalse(ports['values'])
                flash.assert_not_called()
                auto_flash.assert_not_called()
            finally:
                window.update_idletasks()
                window.destroy()
        del widgets, ports, safety, window
        gc.collect()

    def test_discovery_failure_can_be_retried_without_firmware_bundle(self):
        listing = Mock()
        listing.comports.side_effect = [OSError('Discovery unavailable'), [SimpleNamespace(device='COM17')]]
        with patch.object(recovery_gui, 'serial_modules', return_value=(None, listing)):
            window = recovery_gui.create_window(visible=False)
            try:
                widgets = list(descendants(window))
                ports = next(w for w in widgets if w.winfo_class() == 'TCombobox')
                self.assertFalse(ports.get())
                refresh = next(w for w in widgets if w.winfo_class() == 'TButton' and w['text'] == 'Refresh ports')
                refresh.invoke()
                self.assertEqual(ports.get(), 'COM17')
            finally:
                window.update_idletasks()
                window.destroy()
        del widgets, ports, refresh, window
        gc.collect()
