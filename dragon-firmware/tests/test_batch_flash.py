"""Batch flasher checks without an attached board."""
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from flash_support import FILES, FQBN, StartupEvidence, load_bundle, save_bundle
from flash_support import check_startup
from flash_support import compiler_lock
from board_targets import TARGETS, parse_chip, detect_board
from batch_flash import Flasher


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
                window.destroy()

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


if __name__ == '__main__':
    unittest.main()
