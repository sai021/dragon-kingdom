import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from provision_wifi import join_command, provision


class ProvisionTests(unittest.TestCase):
    def test_does_not_accept_old_connection_while_new_join_is_pending(self):
        connection=Mock()
        connection.readline.side_effect=[
            b'network_status connected=1 configured=1 ip=192.0.2.1 joining=0 join_saved=0\n',
            b'Wi-Fi request accepted; credentials are not echoed.\n',
            b'network_status connected=1 configured=1 ip=192.0.2.1 joining=1 join_saved=0\n',
            b'network_status connected=1 configured=1 ip=192.0.2.2 joining=0 join_saved=1\n',
        ]
        output=[]
        serial=SimpleNamespace(Serial=Mock(return_value=connection))
        command=join_command('Family','sample123')
        with patch('provision_wifi.serial_modules',return_value=(serial,None)):
            result=provision('COM7',command,emit=output.append)
        self.assertEqual(result['ip'],'192.0.2.2')
        self.assertNotIn('sample123',''.join(output))
        self.assertTrue(connection.dtr);self.assertFalse(connection.rts)
        connection.close.assert_called_once()

    def test_framing_preserves_spaces_and_utf8(self):
        command = join_command('Family Wi-Fi', 'sample password')
        prefix, action, ssid, password = command.decode().split()
        self.assertEqual((prefix, action), ('wifi', 'join'))
        self.assertEqual(bytes.fromhex(ssid).decode(), 'Family Wi-Fi')
        self.assertEqual(bytes.fromhex(password).decode(), 'sample password')
        self.assertNotIn(b'sample password', command)
        self.assertTrue(join_command('Open', '').endswith(b' -\n'))

    def test_limits_are_encoded_byte_limits(self):
        for ssid, password in [('', 'sample123'), ('x' * 33, 'sample123'),
                               ('\0', 'sample123'), ('test', 'short'),
                               ('test', 'x' * 64), ('test', 'sample\0key')]:
            with self.assertRaises(ValueError):
                join_command(ssid, password)
        self.assertLess(len(join_command('x' * 32, 'a' * 64)), 256)


if __name__ == '__main__':
    unittest.main()
