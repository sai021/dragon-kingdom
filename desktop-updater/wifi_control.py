"""OS Wi-Fi adapters. Only explicitly selected Dragon SSIDs can be joined.

No saved home password is read. Original connection details stay in memory.
Windows uses a temporary WPA2 profile; Mac uses CoreWLAN and OS-managed return.
"""
import ctypes as C
import dataclasses
import re
import subprocess
import sys
import time
from xml.sax.saxutils import escape
from updater_core import UpdateError

DRAGON = re.compile(r'Dragon-Kingdom-[0-9a-f]{6}', re.I)


@dataclasses.dataclass
class Network:
    ssid: str
    signal: int
    interface: object
    native: object = None


def dragon_name(name):
    if not isinstance(name, str) or not DRAGON.fullmatch(name):
        raise UpdateError('Only a selected Dragon-Kingdom-XXXXXX network can be joined.')
    return name


def profile_xml(name):
    name = dragon_name(name)
    return ('<?xml version="1.0"?><WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">'
        f'<name>{escape(name)}</name><SSIDConfig><SSID><hex>{name.encode("ascii").hex()}</hex>'
        f'<name>{escape(name)}</name></SSID></SSIDConfig><connectionType>ESS</connectionType>'
        '<connectionMode>manual</connectionMode><MSM><security><authEncryption>'
        '<authentication>WPA2PSK</authentication><encryption>AES</encryption><useOneX>false</useOneX>'
        '</authEncryption><sharedKey><keyType>passPhrase</keyType><protected>false</protected>'
        '<keyMaterial>dragon123</keyMaterial></sharedKey></security></MSM></WLANProfile>')


U32=C.c_uint32
class GUID(C.Structure):
    _fields_=[('a',U32),('b',C.c_uint16),('c',C.c_uint16),('d',C.c_ubyte*8)]
class SSID(C.Structure):
    _fields_=[('length',U32),('data',C.c_ubyte*32)]
class Interface(C.Structure):
    _fields_=[('guid',GUID),('description',C.c_wchar*256),('state',U32)]
class Available(C.Structure):
    _fields_=[('profile',C.c_wchar*256),('ssid',SSID),('bss',U32),('bssids',U32),
        ('connectable',C.c_int32),('reason',U32),('phys',U32),('phy_types',U32*8),
        ('more',C.c_int32),('signal',U32),('security',C.c_int32),('auth',U32),('cipher',U32),('flags',U32),('reserved',U32)]
class Association(C.Structure):
    _fields_=[('ssid',SSID),('bss',U32),('bssid',C.c_ubyte*6),('phy',U32),('quality',U32),('rx',U32),('tx',U32)]
class Connection(C.Structure):
    _fields_=[('state',U32),('mode',U32),('profile',C.c_wchar*256),('association',Association)]
class Parameters(C.Structure):
    _fields_=[('mode',U32),('profile',C.c_wchar_p),('ssid',C.c_void_p),('bssids',C.c_void_p),('bss',U32),('flags',U32)]


def ssid_text(value):
    if value.length > 32: return ''
    return bytes(value.data[:value.length]).decode('utf-8', errors='replace')


class WindowsWifi:
    def __init__(self,open_handle=True):
        self.api=C.WinDLL('wlanapi.dll')
        signatures={
            'WlanOpenHandle':[U32,C.c_void_p,C.POINTER(U32),C.POINTER(C.c_void_p)],
            'WlanCloseHandle':[C.c_void_p,C.c_void_p],
            'WlanEnumInterfaces':[C.c_void_p,C.c_void_p,C.POINTER(C.c_void_p)],
            'WlanGetAvailableNetworkList':[C.c_void_p,C.POINTER(GUID),U32,C.c_void_p,C.POINTER(C.c_void_p)],
            'WlanScan':[C.c_void_p,C.POINTER(GUID),C.c_void_p,C.c_void_p,C.c_void_p],
            'WlanQueryInterface':[C.c_void_p,C.POINTER(GUID),U32,C.c_void_p,C.POINTER(U32),C.POINTER(C.c_void_p),C.POINTER(U32)],
            'WlanConnect':[C.c_void_p,C.POINTER(GUID),C.POINTER(Parameters),C.c_void_p],
            'WlanDisconnect':[C.c_void_p,C.POINTER(GUID),C.c_void_p],
        }
        for name,args in signatures.items():
            function=getattr(self.api,name);function.argtypes=args;function.restype=U32
        self.api.WlanFreeMemory.argtypes=[C.c_void_p];self.api.WlanFreeMemory.restype=None
        self.handle=C.c_void_p(); version=U32()
        if open_handle:self.check(self.api.WlanOpenHandle(2,None,C.byref(version),C.byref(self.handle)))
    @staticmethod
    def check(code):
        if code==5:
            raise UpdateError('Windows denied Wi-Fi access. Allow location/Wi-Fi access in Windows Settings > Privacy & security > Location, then scan again, or use manual connection. Organisation policy may prevent access.')
        if code: raise UpdateError(f'Windows Wi-Fi request failed ({code}). Check Wi-Fi is enabled, or use manual connection.')
    def close(self):
        if self.handle: self.api.WlanCloseHandle(self.handle,None);self.handle=None
    def interfaces(self):
        p=C.c_void_p();self.check(self.api.WlanEnumInterfaces(self.handle,None,C.byref(p)))
        try:
            count=U32.from_address(p.value).value
            if count>64: raise UpdateError('Unexpected Wi-Fi adapter list.')
            return [Interface.from_buffer_copy(C.string_at(p.value+8+i*C.sizeof(Interface),C.sizeof(Interface))).guid for i in range(count)]
        finally:self.api.WlanFreeMemory(p)
    def current(self, interface):
        size,kind=U32(),U32();p=C.c_void_p()
        code=self.api.WlanQueryInterface(self.handle,C.byref(interface),7,None,C.byref(size),C.byref(p),C.byref(kind))
        if code==5023:return ('','') # Not currently associated.
        self.check(code)
        try:
            if size.value<C.sizeof(Connection):raise UpdateError('Unexpected Windows connection response.')
            value=Connection.from_buffer_copy(C.string_at(p.value,C.sizeof(Connection)))
            return ssid_text(value.association.ssid),value.profile
        finally:self.api.WlanFreeMemory(p)
    def scan(self):
        interfaces=self.interfaces()
        if not interfaces:raise UpdateError('No Wi-Fi adapter is available. Home-network mode can also use Ethernet.')
        for interface in interfaces:self.check(self.api.WlanScan(self.handle,C.byref(interface),None,None,None))
        time.sleep(4) # Native WlanScan is asynchronous; never block the UI thread.
        networks={}
        for interface in interfaces:
            p=C.c_void_p();self.check(self.api.WlanGetAvailableNetworkList(self.handle,C.byref(interface),0,None,C.byref(p)))
            try:
                count=U32.from_address(p.value).value
                if count>2048:raise UpdateError('Unexpected Wi-Fi scan response.')
                for i in range(count):
                    value=Available.from_address(p.value+8+i*C.sizeof(Available));name=ssid_text(value.ssid)
                    if DRAGON.fullmatch(name) and value.security and value.auth==7 and value.cipher==4:
                        candidate=Network(name,int(value.signal),interface)
                        if name not in networks or candidate.signal>networks[name].signal:networks[name]=candidate
            finally:self.api.WlanFreeMemory(p)
        return sorted(networks.values(),key=lambda n:(-n.signal,n.ssid))
    def snapshot(self, interface):
        ssid,profile=self.current(interface)
        return (ssid,profile)
    def join(self,network):
        text=profile_xml(network.ssid)
        params=Parameters(1,text,None,None,1,0) # Temporary XML profile; do not save/overwrite a user profile.
        self.check(self.api.WlanConnect(self.handle,C.byref(network.interface),C.byref(params),None))
    def restore(self,interface,snapshot):
        ssid,profile=snapshot
        if not ssid:
            self.check(self.api.WlanDisconnect(self.handle,C.byref(interface),None));return
        if not profile:raise UpdateError('The original Wi-Fi connection has no saved profile. Rejoin it in the computer Wi-Fi menu.')
        params=Parameters(0,profile,None,None,1,0)
        self.check(self.api.WlanConnect(self.handle,C.byref(interface),C.byref(params),None))


class MacWifi:
    def __init__(self):
        import CoreWLAN,CoreLocation
        self.wlan,self.location=CoreWLAN,CoreLocation
        self.client=CoreWLAN.CWWiFiClient.sharedWiFiClient()
        # Create/request on the main GUI thread. The worker waits for consent.
        self.manager=CoreLocation.CLLocationManager.alloc().init()
        if CoreLocation.CLLocationManager.authorizationStatus()==0:self.manager.requestWhenInUseAuthorization()
    def scan(self):
        deadline=time.monotonic()+30
        while self.location.CLLocationManager.authorizationStatus()==0 and time.monotonic()<deadline:time.sleep(.25)
        if self.location.CLLocationManager.authorizationStatus() not in (3,4):
            raise UpdateError('Allow Location Services for Dragon Kingdom Updater in System Settings > Privacy & Security, then scan again, or use manual connection.')
        interfaces=self.client.interfaces() or []
        if not interfaces:raise UpdateError('No Wi-Fi adapter is available.')
        networks={}
        for interface in interfaces:
            values,error=interface.scanForNetworksWithName_error_(None,None)
            if error:raise UpdateError('Mac Wi-Fi scan failed. Check Wi-Fi and location permission, or use manual connection.')
            for value in values or []:
                name=value.ssid()
                if name and DRAGON.fullmatch(name) and value.supportsSecurity_(self.wlan.kCWSecurityWPA2Personal):
                    candidate=Network(str(name),max(0,min(100,2*(int(value.rssiValue())+100))),interface,value)
                    if name not in networks or candidate.signal>networks[name].signal:networks[name]=candidate
        return sorted(networks.values(),key=lambda n:(-n.signal,n.ssid))
    def current(self,interface):return (str(interface.ssid() or ''),'')
    def snapshot(self,interface):return self.current(interface)
    def join(self,network):
        dragon_name(network.ssid)
        if network.native is None:raise UpdateError('Scan again before joining this network.')
        result,error=network.interface.associateToNetwork_password_error_(network.native,'dragon123',None)
        if not result or error:raise UpdateError('Mac could not join the dragon Wi-Fi. Check it is still available, or use manual connection.')
    def restore(self,interface,snapshot):
        name=snapshot[0]
        if not name:interface.disassociate();return
        # Reuse macOS's saved connection/keychain; never read the home password.
        try:result=subprocess.run(['/usr/sbin/networksetup','-setairportnetwork',str(interface.interfaceName()),name],capture_output=True,timeout=25)
        except (OSError,subprocess.TimeoutExpired) as e:raise UpdateError('Mac could not restore the original network. Rejoin it in the computer Wi-Fi menu.') from e
        if result.returncode or b'Error' in result.stdout:
            raise UpdateError('Mac could not restore the original network. Rejoin it in the computer Wi-Fi menu.')


def controller():
    if sys.platform=='win32':return WindowsWifi()
    if sys.platform=='darwin':return MacWifi()
    raise UpdateError('Automatic Wi-Fi connection is supported on Windows and Mac. Use manual connection here.')


class Session:
    def __init__(self,adapter):
        self.adapter=adapter;self.network=None;self.original=None
        self.changed=False;self.last_reconnect=0
    def join(self,network,timeout=35):
        dragon_name(network.ssid)
        if self.changed:self.restore()
        self.original=self.adapter.snapshot(network.interface)
        self.network=network
        # Mark before the native call: even a lost reply may have changed Wi-Fi.
        self.changed=True
        self.adapter.join(network)
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            if self.adapter.current(network.interface)[0].casefold()==network.ssid.casefold():return
            time.sleep(.5)
        raise UpdateError('Could not confirm connection to the selected dragon. Its AP may have closed after joining home Wi-Fi. Return to the original network and use Home Wi-Fi mode.')
    def reconnect(self):
        if not self.changed or time.monotonic()-self.last_reconnect<15:return
        self.last_reconnect=time.monotonic()
        if self.adapter.current(self.network.interface)[0].casefold()==self.network.ssid.casefold():return
        matches=[n for n in self.adapter.scan() if n.ssid.casefold()==self.network.ssid.casefold()]
        if matches:self.adapter.join(matches[0])
        elif self.original[0]:self.adapter.restore(self.network.interface,self.original)
    def restore(self,timeout=30):
        if not self.changed:return
        self.adapter.restore(self.network.interface,self.original)
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            if self.adapter.current(self.network.interface)[0]==self.original[0]:
                self.changed=False;return
            time.sleep(.5)
        raise UpdateError('Original Wi-Fi could not be confirmed. Rejoin it in your computer Wi-Fi menu.')


def native_self_test():
    if sys.platform=='win32':
        assert C.sizeof(GUID)==16 and C.sizeof(SSID)==36 and C.sizeof(Interface)==532
        assert C.sizeof(Available)==628 and C.sizeof(Parameters)==40
        adapter=WindowsWifi(open_handle=False);adapter.close() # No service, scan, permission or association in CI.
    elif sys.platform=='darwin':
        import CoreWLAN,CoreLocation
        assert hasattr(CoreWLAN.CWInterface,'scanForNetworksWithName_error_')
        assert hasattr(CoreWLAN.CWInterface,'associateToNetwork_password_error_')
        assert hasattr(CoreLocation.CLLocationManager,'requestWhenInUseAuthorization')
