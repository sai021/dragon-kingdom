import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import wifi_control as w
import updater_core as c


class Adapter:
    def __init__(self):self.ssid='test-original';self.actions=[];self.available=[];self.fail=False
    def current(self,interface):return self.ssid,'existing-profile'
    def snapshot(self,interface):return self.current(interface)
    def scan(self):return self.available
    def join(self,network):
        self.actions.append(('join',network.ssid))
        if self.fail:raise c.UpdateError('Connection denied')
        self.ssid=network.ssid
    def restore(self,interface,snapshot):
        self.actions.append(('restore',snapshot[0]));self.ssid=snapshot[0]


class Tests(unittest.TestCase):
    def setUp(self):
        self.adapter=Adapter();self.session=w.Session(self.adapter)
        self.network=w.Network('Dragon-Kingdom-aabbcc',80,'interface')
    def test_profile_temporary_wpa2_and_strict_ssid(self):
        xml=w.profile_xml(self.network.ssid)
        self.assertIn('<authentication>WPA2PSK</authentication>',xml)
        self.assertIn('<encryption>AES</encryption>',xml)
        self.assertIn('<connectionMode>manual</connectionMode>',xml)
        for bad in ('Neighbour Wi-Fi','Dragon-Kingdom-123','Dragon-Kingdom-123456.evil','Dragon-Kingdom-123456</name>',None):
            with self.subTest(name=bad),self.assertRaises(c.UpdateError):w.profile_xml(bad)
    def test_selected_join_then_original_connection_restored(self):
        self.session.join(self.network)
        self.assertTrue(self.session.changed)
        self.assertEqual(self.adapter.ssid,self.network.ssid)
        self.session.restore()
        self.assertFalse(self.session.changed)
        self.assertEqual(self.adapter.ssid,'test-original')
    def test_switch_to_second_dragon_restores_original_before_join(self):
        self.session.join(self.network)
        second=w.Network('Dragon-Kingdom-112233',60,'interface')
        self.session.join(second)
        self.assertEqual(self.adapter.actions,[('join',self.network.ssid),('restore','test-original'),('join',second.ssid)])
        self.session.restore();self.assertEqual(self.adapter.ssid,'test-original')
    def test_reconnect_same_dragon_after_reboot(self):
        self.session.join(self.network);self.adapter.ssid='';self.adapter.available=[self.network]
        self.session.reconnect();self.assertEqual(self.adapter.ssid,self.network.ssid)
    def test_reboot_ap_gone_returns_original_network(self):
        self.session.join(self.network);self.adapter.ssid='';self.adapter.available=[]
        self.session.reconnect();self.assertEqual(self.adapter.ssid,'test-original')
    def test_no_network_switch_when_already_joined(self):
        self.session.join(self.network);count=len(self.adapter.actions)
        self.session.reconnect();self.assertEqual(len(self.adapter.actions),count)
    def test_failed_join_retains_restore_information(self):
        self.adapter.fail=True
        with self.assertRaises(c.UpdateError):self.session.join(self.network)
        self.session.restore();self.assertEqual(self.adapter.ssid,'test-original')
    def test_foreign_network_rejected_without_any_connection_change(self):
        with self.assertRaises(c.UpdateError):self.session.join(w.Network('Not a dragon',100,'interface'))
        self.assertFalse(self.adapter.actions)
    def test_native_bindings(self):w.native_self_test()


if __name__=='__main__':unittest.main()
