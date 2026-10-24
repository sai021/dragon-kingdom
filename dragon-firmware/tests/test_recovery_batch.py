import sys,unittest,time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from recovery_batch import BatchGate
import recovery
import recovery_gui


class BatchTests(unittest.TestCase):
    def test_reenumeration_and_disconnect_before_next_board(self):
        b=BatchGate();self.assertIsNone(b.choose({'COM1'}));b.arm()
        self.assertEqual(b.choose({'COM1'},now=0),'COM1');self.assertIsNone(b.choose({'COM2'},busy=True,now=1))
        b.finished(now=10);self.assertIsNone(b.choose(set(),now=11));self.assertIsNone(b.choose({'COM2'},now=12))
        self.assertIsNone(b.choose({'COM2'},now=14));self.assertTrue(b.waiting)
        self.assertIsNone(b.choose(set(),now=15));self.assertIsNone(b.choose(set(),now=16));self.assertFalse(b.waiting)
        self.assertEqual(b.choose({'COM3'},now=17),'COM3')
    def test_ambiguous_ports_stop_auto(self):
        b=BatchGate();b.arm()
        with self.assertRaises(ValueError):b.choose({'COM1','COM2'})
        self.assertFalse(b.enabled)
    def test_version_order_including_beta_to_release(self):
        tags=['v0.2.4','v0.3.0-beta.1','v0.3.0-beta.2','v0.3.0-beta.10','v0.3.0','v0.3.1-beta.1','v1.0.0']
        self.assertEqual(sorted(tags,key=recovery.firmware_version),tags)
        for tag in ('','garbage','v0.3.0-candidate'):
            with self.assertRaises(ValueError):recovery.firmware_version(tag)
    def test_same_or_newer_board_is_identified_checked_and_never_written(self):
        for tag in ('v0.3.0-beta.2',):
            with patch.object(recovery,'prepared_release',return_value={'firmware_tag':'v0.3.0-beta.2'}),patch.object(recovery,'read_running_version',return_value=tag),patch.object(recovery,'release_image_digest',return_value='a'*64),patch.object(recovery,'recover') as flash,patch.object(recovery,'check_startup') as startup,patch.object(recovery.subprocess,'run',return_value=SimpleNamespace(stdout='Chip type: ESP32-C3',stderr='')) as run:
                recovery.update_if_newer('cli','COM-test',True,lambda text:None,tool=Path('tool'))
                flash.assert_not_called();self.assertEqual(run.call_count,2);startup.assert_called_once_with('COM-test',unittest.mock.ANY,timeout=75,expected_firmware=tag,require_validation=True,expected_board='c3',production=True,expected_image_sha256='a'*64)
                self.assertTrue(all('write-flash' not in call.args[0] for call in run.call_args_list))
    def test_newer_than_selected_release_is_not_production_accepted(self):
        with patch.object(recovery,'prepared_release',return_value={'firmware_tag':'v0.3.0-beta.2'}),patch.object(recovery,'read_running_version',return_value='v0.3.0'),patch.object(recovery,'release_image_digest',return_value='a'*64),patch.object(recovery,'recover') as flash,patch.object(recovery,'check_startup') as startup:
            with self.assertRaises(ValueError):recovery.update_if_newer('cli','COM-test',True,lambda text:None,tool=Path('tool'))
            flash.assert_not_called();startup.assert_not_called()
    def test_older_and_legacy_boards_use_verified_recovery(self):
        for tag in ('v0.3.0-beta.1',None):
            with patch.object(recovery,'prepared_release',return_value={'firmware_tag':'v0.3.0-beta.2'}),patch.object(recovery,'read_running_version',return_value=tag),patch.object(recovery,'recover') as flash:
                recovery.update_if_newer('cli','COM-test',True,lambda text:None,tool=Path('tool'))
                flash.assert_called_once()
    def test_unknown_version_and_missing_power_confirmation_never_flash(self):
        with patch.object(recovery,'prepared_release',return_value={'firmware_tag':'v0.3.0-beta.2'}),patch.object(recovery,'read_running_version',return_value='future-custom-build'),patch.object(recovery,'recover') as flash:
            with self.assertRaises(ValueError):recovery.update_if_newer('cli','COM-test',False,tool=Path('tool'))
            with self.assertRaises(ValueError):recovery.update_if_newer('cli','COM-test',True,lambda text:None,tool=Path('tool'))
            flash.assert_not_called()
    def test_unresponsive_board_is_not_treated_as_legacy(self):
        with patch.object(recovery,'serial_modules',return_value=(None,None)):
            with self.assertRaisesRegex(RuntimeError,'Could not read'):recovery.read_running_version('COM-test',timeout=0)
    def test_gui_auto_requires_power_confirmation_and_runs_once(self):
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        listing=SimpleNamespace(comports=lambda:[SimpleNamespace(device='COM-test',vid=0x303a)])
        with patch.object(recovery_gui,'prepared_release',return_value={'firmware_tag':'v0.3.0-beta.2'}),patch.object(recovery_gui,'installed_esptool',return_value=Path(__file__)),patch.object(recovery_gui,'serial_modules',return_value=(None,listing)),patch.object(recovery_gui,'update_if_newer',return_value='Verified') as update:
            w=recovery_gui.create_window(visible=False,bundle_path=Path("simulated-bundle"))
            try:
                widgets=list(descendants(w));checks=[x for x in widgets if x.winfo_class()=='TCheckbutton'];safety=checks[0];auto=checks[1]
                auto.invoke();self.assertFalse(auto.instate(['selected']));update.assert_not_called()
                safety.invoke();auto.invoke();self.assertTrue(auto.instate(['selected']))
                deadline=time.monotonic()+3
                while not update.called and time.monotonic()<deadline:w.update();time.sleep(.01)
                self.assertTrue(update.called)
                deadline=time.monotonic()+1.2
                while time.monotonic()<deadline:w.update();time.sleep(.01)
                update.assert_called_once();self.assertTrue(safety.instate(['selected']));self.assertTrue(auto.instate(['selected']))
            finally:w.destroy()


if __name__=='__main__':unittest.main()
