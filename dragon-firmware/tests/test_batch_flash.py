"""Batch flasher checks without an attached board."""
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from flash_support import FILES, FQBN, StartupEvidence, load_bundle, save_bundle
from flash_support import check_startup
from flash_support import compiler_lock
from board_targets import TARGETS, parse_chip, detect_board
from batch_flash import Flasher


def destroy_window(window):
    # Cancel Tcl callbacks before destroying a root; subsequent test roots share
    # the event dispatcher and must not receive callbacks from a closed window.
    for callback in window.tk.call('after', 'info'):
        window.after_cancel(callback)
    window.destroy()


class BatchFlashTests(unittest.TestCase):
    def test_build_window_finishes_reuses_workspace_and_preserves_saved_images(self):
        import tkinter as tk
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            paths = []
            def compile_command(*args):
                self.assertIn('--verbose', args)
                build = Path(args[args.index('--build-path') + 1])
                paths.append(build)
                build.mkdir(exist_ok=True)
                for name in FILES:
                    (build / name).write_bytes(b'valid firmware')
                (build / 'build.options.json').write_text(json.dumps({'fqbn': args[args.index('--fqbn') + 1]}))
            window = tk.Tk()
            window.withdraw()
            try:
                with patch('batch_flash.CACHE', cache), patch.object(Flasher, 'refresh'), \
                        patch('batch_flash.generate_palettes'), patch('batch_flash.generate_web'):
                    app = Flasher(window, 'unused')
                    app.run = compile_command
                    def wait_done():
                        deadline = time.monotonic() + 5
                        while app.busy and time.monotonic() < deadline:
                            window.update()
                            time.sleep(.01)
                        self.assertFalse(app.busy, app.status.get())
                    app.compile()
                    wait_done()
                    self.assertIn('Firmware ready', app.status.get())
                    self.assertEqual(set(app.builds), {'s3', 'c3'})
                    original = dict(app.builds)
                    app.compile()
                    wait_done()
                    self.assertEqual(paths[:2], paths[2:])
                    for board in TARGETS:
                        self.assertNotEqual(original[board], app.builds[board])
                        self.assertEqual(load_bundle(cache, board), app.builds[board])
                    original = dict(app.builds)
                    def fail(*args):
                        (paths[0] / FILES[0]).write_bytes(b'partial failed build')
                        raise RuntimeError('simulated compiler failure')
                    app.run = fail
                    app.compile()
                    wait_done()
                    self.assertIn('simulated compiler failure', app.status.get())
                    self.assertEqual(app.builds, original)
                    self.assertEqual(str(app.flash_button['state']), 'normal')
                    for board in TARGETS:
                        self.assertEqual(load_bundle(cache, board), original[board])
                    def fail_second(*args):
                        if args[args.index('--fqbn')+1]==TARGETS['c3']:
                            raise RuntimeError('C3 compiler failure after S3 success')
                        compile_command(*args)
                    app.run=fail_second
                    previous=(cache/'current-set.json').read_bytes()
                    app.compile();wait_done()
                    self.assertIn('C3 compiler failure',app.status.get())
                    self.assertEqual(app.builds,original)
                    self.assertEqual((cache/'current-set.json').read_bytes(),previous)
                    for board in TARGETS:self.assertEqual(load_bundle(cache,board),original[board])
            finally:
                destroy_window(window)

    def test_build_lock_rejects_concurrent_build_and_releases_after_error(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            with self.assertRaisesRegex(ValueError, 'failed'):
                with compiler_lock(cache):
                    with self.assertRaisesRegex(RuntimeError, 'Another flasher'):
                        with compiler_lock(cache):
                            self.fail('concurrent build allowed')
                    raise ValueError('failed')
            with compiler_lock(cache):
                pass

    def test_flash_selects_detected_target_and_blocks_missing_or_unknown(self):
        from unittest.mock import Mock
        for board in TARGETS:
            flasher = Flasher.__new__(Flasher)
            flasher.cli = 'arduino-cli'
            flasher.busy = False
            flasher.known_ports = {'COM7'}
            flasher.auto_mode = Mock(get=lambda: False)
            flasher.ready = True
            flasher.port = Mock(get=lambda: 'COM7')
            flasher.events = Mock()
            flasher.builds = {key: Path(key) for key in TARGETS}
            flasher.start = lambda label, work, kind: work()
            flasher.run = Mock(return_value=None)
            flasher.verify = Mock()
            discovery = SimpleNamespace(stdout=json.dumps([{'port': {'address': 'COM7', 'protocol': 'serial'}}]))
            with patch('batch_flash.serial_modules'), patch('batch_flash.subprocess.run', return_value=discovery), \
                    patch('batch_flash.detect_board', return_value=board), \
                    patch('batch_flash.load_bundle', return_value=Path(board)):
                flasher.flash()
            command = flasher.run.call_args.args
            self.assertEqual(command[command.index('--fqbn') + 1], TARGETS[board])
            self.assertEqual(command[command.index('--input-dir') + 1], board)
            flasher.verify.assert_called_once_with('COM7')
            flasher.run.reset_mock()
            flasher.builds = {}
            with patch('batch_flash.serial_modules'), patch('batch_flash.subprocess.run', return_value=discovery), \
                    patch('batch_flash.detect_board', return_value=board):
                with self.assertRaisesRegex(RuntimeError, 'Nothing was written'):
                    flasher.flash()
            flasher.run.assert_not_called()
            with patch('batch_flash.serial_modules'), patch('batch_flash.subprocess.run', return_value=discovery), \
                    patch('batch_flash.detect_board', side_effect=RuntimeError('unsupported')):
                with self.assertRaisesRegex(RuntimeError, 'unsupported'):
                    flasher.flash()
            flasher.run.assert_not_called()

    def test_chip_identity_requires_supported_rom_banner(self):
        self.assertEqual(parse_chip('Chip is ESP32-S3 (QFN56) (revision v0.2)'), 's3')
        self.assertEqual(parse_chip('Chip type: ESP32-C3 (QFN32) (revision v0.4)'), 'c3')
        self.assertEqual(parse_chip('Chip is ESP32-C3FH4 (revision v0.4)'), 'c3')
        for output in ('USB JTAG ESP32-C3', 'Chip type: ESP32-C6', '',
                       'Chip is ESP32-C3\nChip is ESP32-S3'):
            with self.assertRaises(RuntimeError):
                parse_chip(output)

    def test_probe_reads_rom_without_flash_write(self):
        details = {'build_properties': ['runtime.tools.esptool_py.path=C:/tools',
                                        'tools.esptool_py.cmd=esptool.exe']}
        with patch('board_targets.subprocess.run', side_effect=[
                SimpleNamespace(stdout=json.dumps(details)),
                SimpleNamespace(returncode=0, stdout='Chip type: ESP32-C3 (QFN32)', stderr='')]) as run:
            self.assertEqual(detect_board('arduino-cli', 'COM7'), 'c3')
            command = run.call_args.args[0]
            self.assertEqual(command[-1], 'chip-id')
            self.assertIn('auto', command)
            self.assertIn('COM7', command)
            self.assertNotIn('write-flash', command)
        with patch('board_targets.subprocess.run', side_effect=[
                SimpleNamespace(stdout=json.dumps(details)),
                SimpleNamespace(returncode=2, stdout='connection failed', stderr='')]):
            with self.assertRaisesRegex(RuntimeError, 'Nothing was written'):
                detect_board('arduino-cli', 'COM7')

    def test_target_bundles_are_independent_and_reject_wrong_target(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            for board, fqbn in TARGETS.items():
                build = cache / board
                build.mkdir()
                for name in FILES:
                    (build / name).write_bytes(board.encode())
                (build / 'build.options.json').write_text(json.dumps({'fqbn': fqbn}))
                save_bundle(build, cache, board)
            for board in TARGETS:
                self.assertEqual(load_bundle(cache, board), cache / board)
            with self.assertRaises(ValueError):
                save_bundle(cache / 'c3', cache, 's3')
            self.assertEqual(load_bundle(cache, 's3'), cache / 's3')
            (cache / 'c3' / FILES[0]).write_bytes(b'corruption')
            with self.assertRaises(ValueError):
                load_bundle(cache, 'c3')
            self.assertEqual(load_bundle(cache, 's3'), cache / 's3')

    def test_startup_requires_computer_usb_ceiling(self):
        for status in ('session_max=2400mA computer_usb_cap=0',
                       'session_max=2400mA computer_usb_cap=1'):
            with self.assertRaisesRegex(RuntimeError, 'USB power ceiling'):
                StartupEvidence().observe('uptime_ms=10000 ' + status + ' voltage_sampling=stopped')

    def test_cache_restart_and_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            build = cache / 'build-1'
            build.mkdir()
            for name in FILES:
                (build / name).write_bytes(b'firmware')
            (build / 'build.options.json').write_text(json.dumps({'fqbn': FQBN}))
            save_bundle(build, cache)
            self.assertEqual(load_bundle(cache), build)
            # A failed replacement leaves the last successful selection intact.
            bad = cache / 'incomplete'
            bad.mkdir()
            with self.assertRaises(OSError):
                save_bundle(bad, cache)
            self.assertEqual(load_bundle(cache), build)
            (build / FILES[0]).write_bytes(b'changed')
            with self.assertRaises(ValueError):
                load_bundle(cache)

    def test_bare_board_status_needs_live_uptime(self):
        evidence = StartupEvidence()
        self.assertFalse(evidence.observe('library_ready=1 profile=0 profile_name=All'))
        self.assertFalse(evidence.observe('dragon=dragon1 name=Dragon One effects=0 presets=81 mode=0'))
        self.assertFalse(evidence.observe('uptime_ms=10000 session_max=0mA computer_usb_cap=1 voltage_sampling=stopped'))
        self.assertFalse(evidence.observe('uptime_ms=11000 session_max=0mA computer_usb_cap=1 voltage_sampling=stopped'))
        self.assertTrue(evidence.observe('uptime_ms=12000 session_max=0mA computer_usb_cap=1 voltage_sampling=stopped'))

    def test_crash_and_reboot_are_not_passes(self):
        with self.assertRaises(RuntimeError):
            StartupEvidence().observe("Guru Meditation Error: Core panic'ed")
        evidence = StartupEvidence()
        evidence.observe('uptime_ms=10000 session_max=0mA computer_usb_cap=1 voltage_sampling=stopped')
        with self.assertRaises(RuntimeError):
            evidence.observe('uptime_ms=100 session_max=0mA computer_usb_cap=1 voltage_sampling=stopped')

    def test_serial_check_redacts_credentials_and_closes_port(self):
        lines = iter([
            b'Dragon web: network=Dragon-test password=private login=parent\n',
            b'library_ready=1 profile=0 profile_name=All\n',
            b'dragon=dragon1 name=Dragon One effects=0 presets=81\n',
            b'uptime_ms=10000 session_max=0mA computer_usb_cap=1 voltage_sampling=stopped\n',
            b'uptime_ms=12000 session_max=0mA computer_usb_cap=1 voltage_sampling=stopped\n',
        ])
        from unittest.mock import Mock
        connection = Mock()
        connection.readline.side_effect = lambda: next(lines)
        serial = SimpleNamespace(Serial=Mock(return_value=connection), SerialException=OSError)
        ports = SimpleNamespace(comports=lambda: [SimpleNamespace(device='COM7', serial_number='device', vid=0x303A)])
        output = []
        with patch('flash_support.serial_modules', return_value=(serial, ports)):
            check_startup('COM7', output.append)
        self.assertNotIn('private', ''.join(output))
        connection.write.assert_called_with(b'status\n')
        self.assertTrue(connection.dtr)
        self.assertFalse(connection.rts)
        connection.close.assert_called_once()

    def test_missing_board_times_out(self):
        serial = SimpleNamespace(SerialException=OSError)
        ports = SimpleNamespace(comports=lambda: [])
        with patch('flash_support.serial_modules', return_value=(serial, ports)):
            with self.assertRaisesRegex(RuntimeError, 'NOT confirmed'):
                check_startup('COM7', lambda line: None, timeout=0)


class AutoFlashTests(unittest.TestCase):
    """Real Tk/worker event flow with discovery, ROM, upload and startup fakes."""

    def setUp(self):
        import tkinter as tk
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        cache_patch = patch('batch_flash.CACHE', Path(directory.name))
        cache_patch.start()
        self.addCleanup(cache_patch.stop)
        refresh_patch = patch.object(Flasher, 'refresh')
        refresh_patch.start()
        self.addCleanup(refresh_patch.stop)
        self.window = tk.Tk()
        self.window.withdraw()
        self.addCleanup(destroy_window, self.window)
        self.app = Flasher(self.window, 'unused')
        self.app.builds = {board: Path(board) for board in TARGETS}
        self.app.ready = True
        self.app.run = Mock(return_value='COM8')
        self.app.verify = Mock()
        discovery = SimpleNamespace(stdout=json.dumps([
            {'port': {'address': 'COM7', 'protocol': 'serial'}}]))
        for mock_patch in (
                patch('batch_flash.serial_modules'),
                patch('batch_flash.subprocess.run', return_value=discovery),
                patch('batch_flash.load_bundle', side_effect=lambda board: Path(board))):
            mock_patch.start()
            self.addCleanup(mock_patch.stop)
        chip_patch = patch('batch_flash.detect_board', return_value='c3')
        self.detect = chip_patch.start()
        self.addCleanup(chip_patch.stop)

    def enable(self):
        self.app.auto_mode.set(True)
        self.app.toggle_auto()

    def finish(self):
        deadline = time.monotonic() + 5
        while self.app.busy and time.monotonic() < deadline:
            self.window.update()
            time.sleep(.01)
        self.assertFalse(self.app.busy, self.app.status.get())
        self.app.auto_settle_until = 0

    def test_opt_in_mixed_batch_and_no_reflash_on_usb_renumber(self):
        self.app.update_ports(['COM7'])
        self.app.run.assert_not_called()
        self.assertFalse(self.app.auto_mode.get())
        self.enable()
        self.app.update_ports(['COM7'])
        self.finish()
        self.assertIn(TARGETS['c3'], self.app.run.call_args.args)
        self.assertIn('STARTUP PASS', self.app.status.get())
        self.app.verify.assert_called_once_with('COM8')
        for ports in (['COM7'], ['COM8'], [], ['COM8'], ['COM8']):
            self.app.update_ports(ports)
        self.assertEqual(self.app.run.call_count, 1)
        self.app.update_ports([])
        self.app.update_ports([])
        self.assertIn('Auto ready', self.app.auto_status.get())
        self.detect.return_value = 's3'
        self.app.update_ports(['COM7'])
        self.finish()
        self.assertIn(TARGETS['s3'], self.app.run.call_args.args)
        self.assertEqual(self.app.count, 2)
        self.assertEqual(self.app.checked, 2)

    def test_waits_for_connection_and_ignores_stale_discovery(self):
        old_generation = self.app.scan_generation
        self.enable()
        self.app.events.put(('ports', (old_generation, ['COM7'])))
        self.app.poll()
        self.app.run.assert_not_called()
        self.app.update_ports([])
        self.assertIn('Auto ready', self.app.auto_status.get())
        self.app.update_ports(['COM7'])
        self.finish()
        self.assertEqual(self.app.run.call_count, 1)
        # A scan started before uploading cannot undo the unplug latch.
        self.app.events.put(('ports', (old_generation, [])))
        self.app.poll()
        self.assertEqual(self.app.auto_absent_scans, 0)

    def test_ambiguous_connections_and_missing_firmware_do_not_flash(self):
        self.enable()
        self.app.update_ports(['COM7', 'COM8'])
        self.assertFalse(self.app.auto_mode.get())
        self.assertIn('Several ports', self.app.auto_status.get())
        self.app.run.assert_not_called()
        self.app.ready = False
        self.enable()
        self.assertFalse(self.app.auto_mode.get())
        self.assertIn('Build firmware first', self.app.auto_status.get())

    def test_background_port_does_not_prevent_next_board(self):
        self.enable()
        self.app.update_ports([])
        # An already known unrelated port is not a connection event.
        self.app.known_ports = {'COM1'}
        self.app.update_ports(['COM1', 'COM7'])
        self.finish()
        self.app.update_ports(['COM1'])
        self.app.update_ports(['COM1'])
        self.assertIn('Auto ready', self.app.auto_status.get())
        self.app.update_ports(['COM1', 'COM7'])
        self.finish()
        self.assertEqual(self.app.run.call_count, 2)

    def test_errors_stop_auto_without_retrying(self):
        for failing_step in (self.detect, self.app.run, self.app.verify):
            with self.subTest(step=failing_step):
                self.app.auto_wait_disconnect = False
                failing_step.side_effect = RuntimeError('simulated failure')
                self.enable()
                self.app.update_ports(['COM7'])
                self.finish()
                self.assertFalse(self.app.auto_mode.get())
                self.assertIn('simulated failure', self.app.status.get())
                calls = self.detect.call_count
                self.app.update_ports([])
                self.app.update_ports(['COM7'])
                self.assertEqual(self.detect.call_count, calls)
                failing_step.side_effect = None

    def test_discovery_error_is_not_an_unplug(self):
        self.app.update_ports(['COM7'])
        self.enable()
        self.app.events.put(('scan_error', (self.app.scan_generation, 'discovery failed')))
        self.app.poll()
        self.assertFalse(self.app.auto_mode.get())
        self.assertEqual(self.app.known_ports, {'COM7'})
        self.app.run.assert_not_called()

    def test_switching_off_during_upload_finishes_without_another_flash(self):
        self.enable()
        self.app.update_ports(['COM7'])
        self.app.auto_mode.set(False)
        self.app.toggle_auto()
        self.finish()
        self.assertIn('STARTUP PASS', self.app.status.get())
        self.app.update_ports([])
        self.app.update_ports([])
        self.app.update_ports(['COM7'])
        self.assertEqual(self.app.run.call_count, 1)

    def test_busy_and_settling_cannot_rearm_or_start_another_upload(self):
        self.enable()
        self.app.update_ports(['COM7'])
        self.assertTrue(self.app.busy)
        self.app.flash()
        self.app.update_ports(['COM9'])
        self.finish()
        self.assertEqual(self.app.run.call_count, 1)
        self.app.auto_settle_until = time.monotonic() + 30
        self.app.update_ports([])
        self.app.update_ports([])
        self.assertTrue(self.app.auto_wait_disconnect)
        self.assertEqual(self.app.auto_absent_scans, 0)

    def test_toggle_does_not_reflash_the_finished_board(self):
        self.enable()
        self.app.update_ports(['COM7'])
        self.finish()
        self.app.auto_mode.set(False)
        self.app.toggle_auto()
        self.enable()
        self.app.update_ports(['COM8'])
        self.app.update_ports(['COM8'])
        self.assertEqual(self.app.run.call_count, 1)
        self.assertTrue(self.app.auto_wait_disconnect)


if __name__ == '__main__':
    unittest.main()
