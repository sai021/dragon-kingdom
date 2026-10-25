"""Local-Wi-Fi firmware updates. No USB, shell, unsigned firmware or cloud backups."""
import concurrent.futures
import dataclasses
import datetime
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import ssl
import sys
import threading
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import certifi

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

APP_VERSION = '1.1.0'
REPO = 'sai021/dragon-kingdom'
GUIDE = 'https://sai021.github.io/dragon-kingdom/update/'
MAX_IMAGE = 0x180000
MAX_PACKAGE = 3200000
NAME = re.compile(r'dragon-kingdom-[0-9a-f]{6}', re.I)


class UpdateError(Exception):
    pass


class Cancelled(UpdateError):
    pass


class RPCError(UpdateError):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def version(tag):
    m = re.fullmatch(r'v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-beta\.(0|[1-9]\d*))?', tag or '')
    if not m:
        raise UpdateError('Unrecognised firmware version. Use the update guide or contact the maker.')
    a, b, c, beta = m.groups()
    return int(a), int(b), int(c), beta is None, int(beta or 0)


def legacy(tag):
    v = version(tag)
    if v < version('v0.3.0-beta.1'):
        raise UpdateError('This older firmware needs the maker\'s USB migration, not a Wi-Fi update.')
    return v <= version('v0.3.0-beta.3') or tag == 'v0.3.0'


def trust_key():
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    return serialization.load_pem_public_key((base / 'release-public-key.pem').read_bytes())


def verify_contract(info, key=None):
    key = key or trust_key()
    try:
        message = json.dumps({k: v for k, v in info.items() if k != 'signature'}, sort_keys=True, separators=(',', ':')).encode('ascii')
        key.verify(bytes.fromhex(info['signature']), message, padding.PKCS1v15(), hashes.SHA256())
        version(info['firmware_tag'])
        if info['contract'] != 2 or info['saved_schema'] != 1 or info['capabilities'] & 1 != 1:
            raise ValueError('Unsupported compatibility contract')
        if set(info['targets']) != {'s3', 'c3'} or not re.fullmatch('[0-9a-f]{40}', info['source_commit']):
            raise ValueError('Invalid release identity')
        for board in ('s3', 'c3'):
            if not re.fullmatch('[0-9a-f]{64}', info['targets'][board]['sha256']['DragonPrototype.ino.bin']):
                raise ValueError('Invalid image digest')
    except Exception as e:
        raise UpdateError('Release signature or compatibility check failed. Nothing was installed.') from e
    return info


def verify_package(pkg, info, board, old, key=None):
    key = key or trust_key()
    try:
        size, digest = pkg['size'], pkg['sha256']
        if pkg['board'] != board or type(size) is not int or not 0 < size <= MAX_IMAGE:
            raise ValueError('Wrong board or size')
        if digest != info['targets'][board]['sha256']['DragonPrototype.ino.bin']:
            raise ValueError('Different signed release image')
        if pkg['format'] != (1 if old else 2) or not re.fullmatch('[0-9a-f]+', pkg['image']) or len(pkg['image']) != size * 2:
            raise ValueError('Invalid package')
        image = bytes.fromhex(pkg['image'])
        if hashlib.sha256(image).hexdigest() != digest:
            raise ValueError('Image hash mismatch')
        if old:
            message = f'dragon-update-v1\n{board}\n{size}\n{digest}\n'
        else:
            if pkg['tag'] != info['firmware_tag'] or pkg['capabilities'] != info['capabilities'] or pkg['schema'] != info['saved_schema']:
                raise ValueError('Different compatibility fields')
            message = f'dragon-update-v2\n{board}\n{pkg["tag"]}\n{size}\n{digest}\n{pkg["capabilities"]}\n{pkg["schema"]}\n'
        key.verify(bytes.fromhex(pkg['signature']), message.encode('ascii'), padding.PKCS1v15(), hashes.SHA256())
    except Exception as e:
        raise UpdateError('Firmware board, signature, size or image check failed. Nothing was installed.') from e
    return pkg


def public_url(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != 'https' or p.username or p.password or p.port not in (None, 443):
        return False
    if p.hostname == 'api.github.com':
        return p.path.startswith('/repos/' + REPO + '/')
    if p.hostname == 'github.com':
        return p.path.startswith('/' + REPO + '/releases/')
    return p.hostname in ('release-assets.githubusercontent.com', 'objects.githubusercontent.com')


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not public_url(newurl):
            raise UpdateError('Download redirected outside the trusted HTTPS release hosts.')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def tls_context():
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=certifi.where())
    return context


def download_json(url, limit=MAX_PACKAGE):
    if not public_url(url):
        raise UpdateError('Untrusted release address.')
    request = urllib.request.Request(url, headers={'User-Agent': 'Dragon-Kingdom-Updater/' + APP_VERSION})
    try:
        with urllib.request.build_opener(urllib.request.HTTPSHandler(context=tls_context()), PublicRedirect()).open(request, timeout=25) as r:
            if int(r.headers.get('Content-Length', '0')) > limit:
                raise UpdateError('Download exceeded its size limit.')
            raw = r.read(limit + 1)
            if len(raw) > limit:
                raise UpdateError('Download exceeded its size limit.')
            return json.loads(raw)
    except UpdateError:
        raise
    except Exception as e:
        raise UpdateError('Could not download the release. Check computer internet access; the update guide has alternatives.') from e


@dataclasses.dataclass
class Release:
    tag: str
    info: dict

    @classmethod
    def latest(cls):
        # Use the same public latest-download pointer as the lamp. No GitHub
        # API account/token or shared anonymous API rate allowance is needed.
        info = verify_contract(download_json(f'https://github.com/{REPO}/releases/latest/download/current-set.json', 16384))
        tag = info['firmware_tag']
        if not version(tag)[3]:
            raise UpdateError('No main release was offered.')
        return cls(tag, info)

    def package(self, device):
        old = legacy(device.firmware)
        suffix = '-legacy-bridge' if old else ''
        pkg = download_json(f'https://github.com/{REPO}/releases/download/{self.tag}/dragon-{device.board}{suffix}.dragon.json')
        return verify_package(pkg, self.info, device.board, old)


def cache_folder():
    return backup_folder().parent / 'Firmware'


@dataclasses.dataclass
class PreparedRelease:
    """A complete signed release: package() never accesses the network."""
    tag: str
    info: dict
    packages: dict

    @classmethod
    def load(cls, folder=None):
        path = (Path(folder) if folder else cache_folder()) / 'offline-release.json'
        try:
            with path.open('rb') as f:
                raw = f.read(MAX_PACKAGE * 4 + 65537)
            if len(raw) > MAX_PACKAGE * 4 + 65536:
                raise ValueError('Oversized cache')
            data = json.loads(raw)
            info = verify_contract(data['release'])
            if not version(info['firmware_tag'])[3]:
                raise ValueError('Main releases only')
            expected = {f'{board}-{kind}' for board in ('s3', 'c3') for kind in ('bridge', 'normal')}
            if set(data['packages']) != expected:
                raise ValueError('Incomplete release')
            for board in ('s3', 'c3'):
                for old, kind in ((True, 'bridge'), (False, 'normal')):
                    verify_package(data['packages'][f'{board}-{kind}'], info, board, old)
            return cls(info['firmware_tag'], info, data['packages'])
        except Exception as e:
            raise UpdateError('No complete verified offline download is ready. Join internet Wi-Fi and choose Download for offline use first.') from e

    def package(self, device):
        old = legacy(device.firmware)
        kind = 'bridge' if old else 'normal'
        return verify_package(self.packages[f'{device.board}-{kind}'], self.info, device.board, old)


def prepare_offline(release=None, folder=None, progress=lambda text, percent: None):
    release = release or Release.latest()
    verify_contract(release.info)
    if release.tag != release.info['firmware_tag'] or not version(release.tag)[3]:
        raise UpdateError('Only a signed main release can be prepared.')
    packages = {}
    for board in ('s3', 'c3'):
        for old, kind in ((True, 'bridge'), (False, 'normal')):
            device = Device('http://192.168.4.1', 'Dragon-Kingdom-000000', board,
                            'v0.3.0-beta.3' if old else 'v0.3.0-beta.9')
            packages[f'{board}-{kind}'] = verify_package(release.package(device), release.info, board, old)
            progress('Downloading signed firmware for offline use...', len(packages) * 25)
    folder = Path(folder) if folder else cache_folder()
    folder.mkdir(parents=True, exist_ok=True)
    # One replacement publishes all four verified files together. An interrupted
    # download cannot replace a previously usable offline set with a partial one.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=folder, prefix='.download-', delete=False) as f:
            temporary = Path(f.name)
            json.dump({'release': release.info, 'packages': packages}, f, separators=(',', ':'))
            f.flush(); os.fsync(f.fileno())
        os.replace(temporary, folder / 'offline-release.json')
    finally:
        if temporary and temporary.exists(): temporary.unlink()
    return PreparedRelease.load(folder)


class NoLocalRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # Never forward a parent token/password to a redirected host.


def local_address(value, allow_loopback=False):
    p = urllib.parse.urlsplit(value if '://' in value else 'http://' + value)
    if p.scheme != 'http' or p.username or p.password or p.path not in ('', '/') or p.query or p.fragment:
        raise UpdateError('Enter the lamp\'s local IP address, without a page path.')
    try:
        host = p.hostname or ''
        ip = ipaddress.ip_address(socket.gethostbyname(host))
        port = p.port or 80
        if ip.version != 4 or not (ip.is_private or ip.is_link_local) or (ip.is_loopback and not allow_loopback):
            raise ValueError('Not a local IPv4 address')
        if port != 80 and not allow_loopback:
            raise ValueError('Not the lamp HTTP port')
    except Exception as e:
        raise UpdateError('Could not resolve a local lamp address. Use the numeric address shown on its page.') from e
    return f'http://{ip}' + (f':{port}' if port != 80 else '')


@dataclasses.dataclass
class Device:
    address: str
    hostname: str
    board: str
    firmware: str

    @classmethod
    def probe(cls, address, timeout=1, allow_loopback=False):
        client = Client(address, timeout, allow_loopback)
        s = client.call('/api/state')
        if not NAME.fullmatch(s.get('hostname', '')) or s.get('board') not in ('s3', 'c3'):
            raise UpdateError('This address did not identify a Dragon Kingdom lamp.')
        version(s.get('firmware', ''))
        return cls(client.address, s['hostname'], s['board'], s['firmware'])


class Client:
    def __init__(self, address, timeout=6, allow_loopback=False):
        self.address = local_address(address, allow_loopback)
        self.timeout, self.token = timeout, None
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoLocalRedirect())

    def call(self, path, data=None):
        headers = {'X-Dragon-Request': '1'}
        if self.token:
            headers['X-Dragon-Parent'] = self.token
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        request = urllib.request.Request(self.address + path, data=body, headers=headers)
        try:
            with self.opener.open(request, timeout=self.timeout) as r:
                raw = r.read(32769)
                if len(raw) > 32768:
                    raise UpdateError('Unexpectedly large lamp response.')
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            raise RPCError(e.code, f'Lamp rejected the request (HTTP {e.code}). Check the parent password, startup and other open updates.') from e
        except UpdateError:
            raise
        except Exception as e:
            raise UpdateError('Lamp did not respond. Check power and the shared home network.') from e

    def login(self, password):
        token = self.call('/api/parent/login', {'password': password})['token']
        if not re.fullmatch('[0-9a-f]{64}', token):
            raise UpdateError('Unexpected parent-session response.')
        self.token = token

    def logout(self):
        if self.token:
            try:
                self.call('/api/parent/logout', {})
            except UpdateError:
                pass
        self.token = None


def backup_bytes(value):
    try:
        data = bytes.fromhex(value['data'])
        if value['format'] != 'dragon-backup-v1' or len(data) != 908:
            raise ValueError('Unsupported backup')
        return data
    except Exception as e:
        raise UpdateError('Unrecognised saved-data backup. Contact the maker; nothing was installed.') from e


def same_settings(a, b):
    a, b = backup_bytes(a), backup_bytes(b)
    # The firmware snapshot includes volatile phone clock/timezone rules and CRC.
    return a[:832] == b[:832] and a[840:844] == b[840:844] and a[846] == b[846] and a[880:904] == b[880:904]


def backup_folder():
    if sys.platform == 'win32':
        return Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'Dragon Kingdom' / 'Backups'
    if sys.platform == 'darwin':
        return Path.home() / 'Library/Application Support/Dragon Kingdom/Backups'
    return Path.home() / '.local/share/dragon-kingdom/backups'


def discover(cancel=None, mdns_seconds=2, scan=True):
    import psutil
    from zeroconf import Zeroconf, ServiceBrowser, IPVersion
    cancel = cancel or threading.Event()
    candidates, networks, seen = set(), [], set()
    for interface, addrs in psutil.net_if_addrs().items():
        stats = psutil.net_if_stats().get(interface)
        if not stats or not stats.isup:
            continue
        for addr in addrs:
            if addr.family == socket.AF_INET:
                try:
                    ip = ipaddress.IPv4Address(addr.address)
                    if ip.is_private and not ip.is_loopback and not ip.is_link_local:
                        networks.append(ipaddress.IPv4Network(str(ip) + '/24', strict=False))
                        seen.add(str(ip))
                except ValueError:
                    pass
    zc = None
    try:
        zc = Zeroconf(ip_version=IPVersion.V4Only)
        def found(zeroconf, service_type, name, state_change):
            if 'dragon-kingdom-' not in name.lower():
                return
            info = zeroconf.get_service_info(service_type, name, timeout=500)
            if info:
                candidates.update(info.parsed_scoped_addresses(IPVersion.V4Only))
        browser = ServiceBrowser(zc, '_http._tcp.local.', handlers=[found])
        cancel.wait(mdns_seconds)
        browser.cancel()
    except Exception:
        pass  # Local subnet/manual-address fallback works without multicast.
    finally:
        if zc:
            zc.close()
    if scan:
        for net in list(dict.fromkeys(networks))[:2]:
            candidates.update(str(ip) for ip in net.hosts() if str(ip) not in seen)
    def probe(ip):
        if cancel.is_set():
            return None
        try:
            return Device.probe(ip, timeout=.6)
        except Exception:
            return None
    devices = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
        for device in pool.map(probe, sorted(candidates)[:512]):
            if device:
                devices[device.hostname] = device
    return sorted(devices.values(), key=lambda d: d.hostname)


def update(device, release, password, progress=lambda text, percent: None, cancel=None,
           backups=None, client_factory=Client, reboot_timeout=180, poll_interval=2):
    cancel = cancel or threading.Event()
    if version(release.tag) <= version(device.firmware):
        raise UpdateError('This lamp is already on the offered version or newer. No downgrade was performed.')
    old = legacy(device.firmware)
    progress('Verifying prepared firmware (no internet needed)...' if isinstance(release, PreparedRelease) else 'Downloading and verifying signed firmware...', 0)
    pkg = release.package(device)  # Verify completely before login, backup or erase.
    if cancel.is_set():
        raise Cancelled('Cancelled before installation.')
    client = client_factory(device.address)
    started, finalized = False, False
    backup_path = None
    try:
        state = client.call('/api/state')
        if (state.get('hostname'), state.get('board'), state.get('firmware')) != (device.hostname, device.board, device.firmware):
            raise UpdateError('Lamp identity/version changed. Find dragons again before updating.')
        resume_addresses = [client.address]
        if state.get('connected') and state.get('ip'):
            try:
                ip = ipaddress.IPv4Address(state['ip'])
                home = local_address(str(ip))
                if not ip.is_unspecified and home not in resume_addresses:
                    resume_addresses.append(home)
            except (ValueError, UpdateError):
                pass
        client.login(password)
        backup = client.call('/api/backup')
        backup_bytes(backup)
        folder = Path(backups) if backups else backup_folder()
        folder.mkdir(parents=True, exist_ok=True)
        filename = device.hostname + '-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json'
        backup_path = folder / filename
        fd = os.open(backup_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(backup, f, indent=2)
        status = client.call('/api/update')
        if status['board'] != device.board or status['active']:
            raise UpdateError('Another firmware upload is active. Finish or cancel it first.')
        if cancel.is_set():
            raise Cancelled('Cancelled. Backup saved; firmware unchanged.')
        fields = ('board', 'size', 'sha256', 'signature') if old else ('format', 'board', 'size', 'sha256', 'signature', 'tag', 'capabilities', 'schema')
        # An uncertain START may already own an erased inactive slot. Abort with
        # this token on all error exits, even if the first reply was lost.
        started = True
        try:
            result = client.call('/api/update/start', {k: pkg[k] for k in fields})
        except RPCError:
            raise
        except UpdateError:
            result = client.call('/api/update')
            if not result.get('active') or result.get('board') != device.board:
                raise UpdateError('Upload start could not be confirmed. Retry after checking the lamp.')
        if result.get('offset') != 0:
            raise UpdateError('Unexpected upload start offset.')
        last_progress = -1
        for offset in range(0, pkg['size'], 512):
            if cancel.is_set():
                raise Cancelled('Cancelled. Existing firmware kept; backup saved.')
            end = min(offset + 512, pkg['size'])
            for attempt in range(3):
                try:
                    result = client.call('/api/update/chunk', {'offset': offset, 'data': pkg['image'][offset * 2:end * 2]})
                    break
                except RPCError:
                    raise
                except UpdateError:
                    # Beta 3 rejects duplicate chunks: inspect offset before replay.
                    status = client.call('/api/update')
                    if status.get('board') != device.board or not status.get('active'):
                        raise UpdateError('Upload session ended. Find the lamp and retry; do not reset saved data.')
                    if status.get('offset') == end:
                        result = status
                        break
                    if status.get('offset') != offset or attempt == 2:
                        raise UpdateError('Upload progress is uncertain. Existing firmware was not finalized.')
            if result.get('offset') != end:
                raise UpdateError('Unexpected upload offset. Firmware was not finalized.')
            percent = end * 85 // pkg['size']
            if percent != last_progress:
                progress('Uploading to ' + device.hostname + '...', percent)
                last_progress = percent
        if cancel.is_set():
            raise Cancelled('Cancelled before final verification. Existing firmware kept.')
        progress('Verifying image and waiting for the lamp to restart. Do not disconnect power.', 88)
        try:
            result = client.call('/api/update/finish', {})
            if not result.get('restarting'):
                raise UpdateError('Unexpected final verification response.')
        except RPCError:
            raise
        except UpdateError:
            pass  # A lost final reply is ambiguous: never replay finish; check boot.
        finalized = True
        client.token = None
        deadline, last_discovery = time.monotonic() + reboot_timeout, time.monotonic()
        resume_index = 0
        while time.monotonic() < deadline:
            try:
                s = client.call('/api/state')
                if (s.get('hostname'), s.get('board')) != (device.hostname, device.board):
                    raise UpdateError('Different device at the old address.')
                if s.get('firmware') == release.tag:
                    client.login(password)
                    support = client.call('/api/support')
                    if support.get('validated') and support.get('otaState') == 2:
                        after = client.call('/api/backup')
                        if not same_settings(backup, after):
                            raise UpdateError('Firmware updated, but saved settings differ. Keep the backup and contact the maker.')
                        progress('Update verified. Saved settings match the backup.', 100)
                        return {'firmware': release.tag, 'address': client.address, 'backup': str(backup_path)}
            except RPCError:
                client.token = None
            except UpdateError as e:
                if str(e).startswith('Firmware updated, but'):
                    raise
                client.token = None
            # An AP-started update can boot onto saved home Wi-Fi. Try the
            # previously reported station address too, including routed LANs
            # where multicast/subnet discovery cannot reach that address.
            if len(resume_addresses) > 1:
                resume_index = (resume_index + 1) % len(resume_addresses)
                client = client_factory(resume_addresses[resume_index])
            if time.monotonic() - last_discovery > 25:
                for candidate in discover(scan=True):
                    if candidate.hostname == device.hostname and candidate.board == device.board:
                        client = client_factory(candidate.address)
                        break
                last_discovery = time.monotonic()
            time.sleep(poll_interval)
        raise UpdateError('Restart could not be verified. Keep power connected, reopen the lamp page and check its version before retrying. Your backup is saved.')
    finally:
        if started and not finalized:
            try:
                client.call('/api/update/abort', {})
            except UpdateError:
                pass
        client.logout()
