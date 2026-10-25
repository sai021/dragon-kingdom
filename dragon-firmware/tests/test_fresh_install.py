"""Fresh-board/reuse flow with real backup files and a simulated USB flasher."""
from pathlib import Path
import sys
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import recovery


class FreshInstallTests(unittest.TestCase):
    def exercise(self, content, replacement=False, damaged_backup=False, dirty_nvs=False, size='4MB', backup_decision=None):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary); build = folder/'build'; build.mkdir()
            for name in recovery.FILES: (build/name).write_bytes(b'signed image fixture')
            commands = []
            def run(argv, **kwargs):
                commands.append(argv)
                if 'flash-id' in argv:
                    return SimpleNamespace(returncode=0, stdout='Chip type: ESP32-S3\nDetected flash size: '+size, stderr='')
                if 'read-flash' in argv:
                    offset = argv[argv.index('read-flash')+1]
                    target = Path(argv[-1])
                    if offset == '0':
                        target.write_bytes(content if not damaged_backup or target.name!='flash-verify.bin' else b'bad')
                    else: target.write_bytes((b'\0' if dirty_nvs else b'\xff')*0x5000)
                return SimpleNamespace(returncode=0, stdout='', stderr='')
            with patch.object(recovery,'ROOT',folder), patch.object(recovery,'prepared_release',return_value={'firmware_tag':'v0.3.1'}), \
                 patch.object(recovery,'load_bundle',return_value=build), patch.object(recovery,'validate_partitions'), \
                 patch.object(recovery,'validate_image_target'), patch.object(recovery,'release_image_digest',return_value='a'*64), \
                 patch.object(recovery,'check_startup') as startup, patch.object(recovery.subprocess,'run',side_effect=run):
                try:
                    result = recovery.install_fresh('COM17',True,replacement,lambda message:None,cache=folder,tool=Path('helper'),backup_decision=backup_decision)
                    return result, commands, startup.call_args, None
                except Exception as error:
                    return None, commands, startup.call_args, error

    def test_empty_board_initializes_without_whole_flash_erase(self):
        result, commands, startup, error = self.exercise(b'\xff'*(4*1024*1024))
        self.assertIsNone(error)
        self.assertIn('empty board', result)
        self.assertFalse(any('erase-flash' in c for c in commands))
        self.assertTrue(any('write-flash' in c for c in commands))
        self.assertTrue(startup.kwargs['require_validation'])
        self.assertEqual(startup.kwargs['expected_image_sha256'], 'a'*64)

    def test_used_board_is_backed_up_but_never_erased_without_replacement(self):
        result, commands, startup, error = self.exercise(b'old firmware' + b'\0'*(4*1024*1024-12))
        self.assertIsInstance(error, ValueError)
        self.assertIn('aborted before erasing', str(error))
        self.assertFalse(any('erase-flash' in c or 'write-flash' in c for c in commands))
        self.assertIsNone(startup)

    def test_unidentified_existing_firmware_prompts_instead_of_requesting_installation_mode(self):
        for proceed in (False,True):
            prompts=[]
            def decide(message):prompts.append(message);return proceed
            with self.subTest(proceed=proceed):
                result, commands, startup, error=self.exercise(b'\0'*(4*1024*1024),backup_decision=decide)
                self.assertEqual(len(prompts),1)
                self.assertIn('not recognized',prompts[0])
                if proceed:
                    self.assertIsNone(error)
                    self.assertTrue(any('write-flash' in c for c in commands))
                    self.assertIsNotNone(startup)
                else:
                    self.assertFalse(any('erase-flash' in c or 'write-flash' in c for c in commands))
                    self.assertIsNotNone(error)

    def test_explicit_replacement_erases_only_after_two_complete_reads(self):
        result, commands, startup, error = self.exercise(b'\0'*(4*1024*1024),replacement=True)
        self.assertIsNone(error)
        erase = next(i for i,c in enumerate(commands) if 'erase-flash' in c)
        self.assertEqual(sum('read-flash' in c for c in commands[:erase]),2)
        self.assertIn('fresh installation', result)
        self.assertIsNotNone(startup)

    def test_incomplete_or_different_backup_cannot_erase_even_with_confirmation(self):
        result, commands, startup, error = self.exercise(b'\0'*(4*1024*1024),replacement=True,damaged_backup=True)
        self.assertIsNotNone(error)
        self.assertFalse(any('erase-flash' in c or 'write-flash' in c for c in commands))

    def test_backup_failure_waits_for_abort_or_continue_before_any_write(self):
        for proceed in (False, True):
            prompts=[]
            def decide(message):
                prompts.append(message)
                return proceed
            with self.subTest(proceed=proceed):
                result, commands, startup, error = self.exercise(
                    b'\0'*(4*1024*1024), damaged_backup=True, backup_decision=decide)
                self.assertEqual(len(prompts), 1)
                self.assertIn('replace the existing firmware and saved data', prompts[0])
                writes=[c for c in commands if 'erase-flash' in c or 'write-flash' in c]
                if proceed:
                    self.assertIsNone(error)
                    self.assertEqual(len(writes), 2)
                    self.assertIsNotNone(startup)
                    self.assertIn('without a verified backup', result)
                    self.assertFalse(any('0x9000' in c for c in commands))
                else:
                    self.assertIn('aborted before erasing or writing', str(error))
                    self.assertFalse(writes)
                    self.assertIsNone(startup)

    def test_wrong_size_or_dirty_new_nvs_cannot_receive_startup_pass(self):
        for options in ({'size':'2MB'}, {'dirty_nvs':True}):
            with self.subTest(options=options):
                result, commands, startup, error = self.exercise(b'\xff'*(4*1024*1024),**options)
                self.assertIsNotNone(error)
                self.assertIsNone(startup)

    def test_power_gate_precedes_bundle_and_device_access(self):
        with patch.object(recovery,'prepared_release') as prepared:
            with self.assertRaises(ValueError): recovery.install_fresh('COM17',False,True)
        prepared.assert_not_called()


class PreservationBackupFailureTests(unittest.TestCase):
    def test_abort_prevents_writes_and_continue_still_excludes_saved_data(self):
        entries=[('nvs',1,2,0x9000,0x5000),('otadata',1,0,0xe000,0x2000),('app0',0,0x10,0x10000,0x180000),('app1',0,0x11,0x190000,0x180000)]
        table=b''.join(struct.pack('<HBBII16sI',0x50aa,t,sub,at,size,name.encode(),0) for name,t,sub,at,size in entries)
        for proceed in (False,True):
            with self.subTest(proceed=proceed), tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary);build=root/'bundle';build.mkdir();calls=[];prompts=[]
                for name in recovery.FILES:(build/name).write_bytes(b'image fixture')
                def run(argv,**kwargs):
                    calls.append(argv)
                    if 'read-flash' in argv:
                        if argv[argv.index('read-flash')+1]=='0x8000':Path(argv[-1]).write_bytes(table)
                        else:raise RuntimeError('Cannot read saved data')
                    return SimpleNamespace(returncode=0,stdout='',stderr='')
                def decide(message):
                    self.assertFalse(any('write-flash' in c or 'erase-flash' in c for c in calls))
                    prompts.append(message)
                    return proceed
                with patch.object(recovery,'ROOT',root),patch.object(recovery,'prepared_release',return_value={'firmware_tag':'v0.3.1','saved_schema':1}), \
                     patch.object(recovery,'check_source_compatibility'),patch.object(recovery,'detect_board',return_value='s3'), \
                     patch.object(recovery,'load_bundle',return_value=build),patch.object(recovery,'validate_partitions'), \
                     patch.object(recovery,'validate_image_target'),patch.object(recovery,'esptool_path',return_value=Path('helper')), \
                     patch.object(recovery,'release_image_digest',return_value='a'*64),patch.object(recovery,'check_startup') as startup, \
                     patch.object(recovery.subprocess,'run',side_effect=run):
                    if proceed:
                        session=recovery.recover('cli','COM17',True,lambda text:None,backup_decision=decide)
                        self.assertTrue((session/'backup-unavailable.json').exists())
                        write=next(c for c in calls if 'write-flash' in c)
                        self.assertEqual(write[write.index('write-flash')+1::2],['0x0','0x8000','0xe000','0x10000'])
                        self.assertFalse(any('erase-flash' in c for c in calls))
                        startup.assert_called_once()
                    else:
                        with self.assertRaisesRegex(RuntimeError,'aborted before writing'):
                            recovery.recover('cli','COM17',True,lambda text:None,backup_decision=decide)
                        self.assertFalse(any('write-flash' in c or 'erase-flash' in c for c in calls))
                        startup.assert_not_called()
                self.assertEqual(len(prompts),1)
