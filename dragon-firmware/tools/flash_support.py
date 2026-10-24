"""Persistent firmware bundles and bare-board serial startup verification."""
import hashlib
from contextlib import contextmanager
import json
from pathlib import Path
import re
import sys
import time

from dev import ROOT, FQBN
from board_targets import TARGETS

FILES = ('DragonPrototype.ino.bin', 'DragonPrototype.ino.bootloader.bin',
         'DragonPrototype.ino.partitions.bin')
CACHE = ROOT / '.tools' / 'batch-flash'


@contextmanager
def compiler_lock(cache=CACHE):
    """Release automatically even if a flasher process exits unexpectedly."""
    cache.mkdir(parents=True, exist_ok=True)
    with (cache / 'compiler.lock').open('a+b') as handle:
        if handle.tell() == 0:
            handle.write(b'0')
        handle.flush()
        handle.seek(0)
        try:
            if sys.platform == 'win32':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise RuntimeError('Another flasher is building firmware. Wait for that build to finish.') from error
        try:
            yield
        finally:
            if sys.platform == 'win32':
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle_manifest(build, board='s3'):
    options = json.loads((build / 'build.options.json').read_text(encoding='utf-8'))
    fqbn = TARGETS[board]
    if options.get('fqbn') != fqbn:
        raise ValueError('Build has a different board configuration.')
    if not 0 < (build / FILES[0]).stat().st_size <= 0x180000:
        raise ValueError('Application is missing or exceeds the custom partition.')
    hashes = {}
    for name in FILES:
        if not (build / name).stat().st_size:
            raise ValueError('Empty firmware file: ' + name)
        hashes[name] = digest(build / name)
    return {'directory': build.name, 'fqbn': fqbn, 'sha256': hashes}


def save_bundle(build, cache=CACHE, board='s3'):
    # Legacy single-target format, retained for compatibility with saved bundles.
    manifest = bundle_manifest(build, board)
    filename = 'current.json' if board == 's3' else 'current-c3.json'
    temporary = cache / (filename + '.tmp')
    temporary.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    temporary.replace(cache / filename)


def source_fingerprint(root=ROOT):
    hasher=hashlib.sha256()
    for folder in ('DragonPrototype', 'web', 'presets', 'tools'):
        for path in sorted((root / folder).iterdir()):
            if path.is_file() and path.suffix in ('.h','.ino','.csv','.html','.js','.json','.py'):
                hasher.update(path.relative_to(root).as_posix().encode('utf-8')+b'\0')
                hasher.update(path.read_bytes()+b'\0')
    return hasher.hexdigest()


def save_release(builds, cache=CACHE, source_sha256=None, firmware_tag=None):
    if set(builds) != set(TARGETS):
        raise ValueError('Both S3 and C3 firmware are required before publication.')
    targets={board:bundle_manifest(build, board) for board,build in builds.items()}
    if any(build.parent.resolve()!=cache.resolve() for build in builds.values()):
        raise ValueError('Release bundles must be inside the firmware cache.')
    manifest={'schema':1,'source_sha256':source_sha256,'targets':targets}
    if firmware_tag:manifest['firmware_tag']=firmware_tag
    temporary=cache / 'current-set.json.tmp'
    temporary.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    # One atomic replacement publishes both targets, or neither of them.
    temporary.replace(cache / 'current-set.json')


def load_bundle(cache=CACHE, board='s3'):
    release=cache / 'current-set.json'
    if release.exists():
        data=json.loads(release.read_text(encoding='utf-8'))
        if data.get('schema')!=1 or set(data['targets'])!=set(TARGETS):
            raise ValueError('Invalid saved release set.')
        manifest=data['targets'][board]
    else:
        filename = 'current.json' if board == 's3' else 'current-c3.json'
        manifest = json.loads((cache / filename).read_text(encoding='utf-8'))
    name = manifest['directory']
    if Path(name).name != name or name in ('.', '..') or manifest['fqbn'] != TARGETS[board]:
        raise ValueError('Invalid saved firmware configuration.')
    build = cache / name
    for filename in FILES:
        if digest(build / filename) != manifest['sha256'][filename]:
            raise ValueError('Saved firmware checksum mismatch: ' + filename)
    if not 0 < (build / FILES[0]).stat().st_size <= 0x180000:
        raise ValueError('Invalid saved application size.')
    return build


def serial_modules():
    try:
        import serial
    except ImportError:
        sys.path.insert(0, str(ROOT / '.tools' / 'python-packages'))
        try:
            import serial
        except ImportError as error:
            raise RuntimeError('Startup check needs pyserial. Install with: python -m pip install pyserial') from error
    from serial.tools import list_ports
    return serial, list_ports


class StartupEvidence:
    def __init__(self):
        self.uptimes = []
        self.library = False
        self.dragon = False

    def observe(self, line):
        if re.search(r'^(Guru Meditation Error|panic\b|abort\(\)|ESP-ROM:.*panic)', line, re.IGNORECASE):
            raise RuntimeError('Firmware reported a crash during startup.')
        match = re.match(r'uptime_ms=(\d+) session_max=(\d+)mA computer_usb_cap=([01]) voltage_sampling=stopped', line)
        if match:
            if match[3] != '1' or int(match[2]) > 400:
                raise RuntimeError('Computer USB power ceiling was not detected. Startup check failed.')
            uptime = int(match[1])
            if self.uptimes and uptime < self.uptimes[-1]:
                raise RuntimeError('Board restarted during the startup check.')
            self.uptimes.append(uptime)
        self.library |= line.startswith('library_ready=1 ')
        self.dragon |= bool(re.match(r'dragon=\S+ name=.+ effects=\d+ presets=\d+', line))
        return (self.library and self.dragon and len(self.uptimes) >= 2
                and self.uptimes[-1] - self.uptimes[0] >= 2000)


def check_startup(port, emit, timeout=45, expected_firmware=None, require_validation=False):
    serial, list_ports = serial_modules()
    initial = list(list_ports.comports())
    identity = next((p.serial_number for p in initial if p.device == port), None)
    baseline = {p.device for p in initial if p.device != port}
    deadline = time.monotonic() + timeout
    connection = None
    evidence = StartupEvidence()
    last_request = 0
    version_ok = not expected_firmware
    validation_ok = not require_validation
    try:
        while time.monotonic() < deadline:
            if connection is None:
                ports = list(list_ports.comports())
                matches = [p.device for p in ports if identity and p.serial_number == identity]
                candidates = [p.device for p in ports if p.device not in baseline and p.vid == 0x303A]
                chosen = (matches[0] if len(matches) == 1 else
                          port if any(p.device == port for p in ports) else
                          candidates[0] if len(candidates) == 1 else None)
                if not chosen:
                    time.sleep(.2)
                    continue
                try:
                    connection = serial.Serial(port=None, baudrate=115200, timeout=.2, write_timeout=1)
                    # Enable native USB CDC output; leave RTS inactive (no reset pulse).
                    connection.dtr = True
                    connection.rts = False
                    connection.port = chosen
                    connection.open()
                    connection.reset_input_buffer()
                    evidence = StartupEvidence()
                    version_ok = not expected_firmware
                    validation_ok = not require_validation
                    last_request = 0
                    emit('Checking Dragon Kingdom on ' + chosen + '…\n')
                except (serial.SerialException, OSError):
                    if connection:
                        connection.close()
                    connection = None
                    time.sleep(.2)
                    continue
            try:
                if time.monotonic() - last_request >= 1:
                    connection.write(b'status\n')
                    last_request = time.monotonic()
                line = connection.readline().decode('utf-8', errors='replace').strip()
                # Display only expected status fields; never capture setup passwords.
                if line.startswith(('uptime_ms=', 'library_ready=', 'dragon=', 'firmware_version=', 'firmware_validation ')):
                    emit(line + '\n')
                if line.startswith('firmware_version='):
                    version_ok = line.split()[0] == 'firmware_version='+str(expected_firmware) if expected_firmware else True
                    if not version_ok:raise RuntimeError('The connected board is not running the prepared firmware version.')
                if line.startswith('firmware_validation '):
                    validation_ok = 'ready=1 ' in line and 'ota_state=2' in line
                if evidence.observe(line) and version_ok and validation_ok:
                    return 'Dragon Kingdom responded with increasing uptime and ready library.'
            except (serial.SerialException, OSError):
                connection.close()
                connection = None
        raise RuntimeError('Startup NOT confirmed. Release BOOT, press RESET, then click Check startup to retry without reflashing.')
    finally:
        if connection:
            connection.close()
