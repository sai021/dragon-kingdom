"""USB adapter for the existing signed, NVS-preserving recovery implementation."""
import io
import json
from pathlib import Path
import sys
import tempfile
import urllib.request
import zipfile

import updater_core as core

FILES = ('DragonPrototype.ino.bin', 'DragonPrototype.ino.bootloader.bin', 'DragonPrototype.ino.partitions.bin')


def service():
    try:
        from usb_service import recovery
    except ImportError:
        from prepare_usb_service import prepare
        sys.path.insert(0, str(prepare()))
        from usb_service import recovery
    return recovery


def bundle_folder():
    return core.cache_folder() / 'USB'


def gate():
    service()
    from usb_service.recovery_batch import BatchGate
    return BatchGate()


def validate(folder, release):
    recovery = service()
    info = recovery.prepared_release(folder)
    if info != release.info or info['firmware_tag'] != release.tag:
        raise core.UpdateError('USB bundle differs from the selected signed stable release.')
    return folder


def cached_release():
    candidates = []
    for path in bundle_folder().glob('v*/current-set.json'):
        try:
            if path.stat().st_size > 16384:
                continue
            info = core.verify_contract(json.loads(path.read_text(encoding='utf-8')))
            tag = info['firmware_tag']
            if tag != path.parent.name or not core.version(tag)[3]:
                continue
            release = core.Release(tag, info)
            validate(path.parent, release)
            candidates.append(release)
        except Exception:
            continue
    if not candidates:
        raise core.UpdateError('No verified USB firmware is saved. Download USB files on internet first.')
    return max(candidates, key=lambda r: core.version(r.tag))


def prepare(release, cache=None):
    """Download one signed, immutable USB set, preserving older complete sets."""
    core.verify_contract(release.info)
    if release.tag != release.info['firmware_tag'] or not core.version(release.tag)[3]:
        raise core.UpdateError('USB requires the signed stable release.')
    destination = (Path(cache) if cache else bundle_folder()) / release.tag
    if destination.exists():
        return validate(destination, release)
    url = f'https://github.com/{core.REPO}/releases/download/{release.tag}/dragon-usb-recovery-bundle.zip'
    request = urllib.request.Request(url, headers={'User-Agent': 'Dragon-Kingdom-Easy-Update/' + core.APP_VERSION})
    limit = 8 * 1024 * 1024
    with urllib.request.build_opener(urllib.request.HTTPSHandler(context=core.tls_context()), core.PublicRedirect()).open(request, timeout=30) as response:
        raw = response.read(limit + 1)
    if len(raw) > limit:
        raise core.UpdateError('USB download is too large.')
    expected = {'current-set.json'} | {board + '/' + name for board in ('s3', 'c3') for name in FILES}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix='.download-') as temporary:
        folder = Path(temporary) / 'bundle'
        folder.mkdir()
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or set(names) - expected - {'README.txt'} or not expected.issubset(names):
                raise core.UpdateError('Unexpected USB bundle contents.')
            for name in expected:
                entry = archive.getinfo(name)
                maximum = core.MAX_IMAGE if name.endswith('.bin') else 16384
                if not 0 < entry.file_size <= maximum:
                    raise core.UpdateError('Invalid USB bundle file size.')
                target = folder / name
                target.parent.mkdir(exist_ok=True)
                target.write_bytes(archive.read(entry))
        validate(folder, release)
        # All files and both board images are verified before publication.
        folder.rename(destination)
    return destination


def ports():
    from serial.tools import list_ports
    return sorted(list_ports.comports(), key=lambda port: port.device)


def helper():
    # The standalone GPL tool is distributed alongside the GUI, not imported by it.
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
        if sys.platform == 'darwin':
            base = base.parents[2]  # ZIP directory beside Easy Update.app
        path = base / 'USB Tools' / ('dragon-usb-tool.exe' if sys.platform == 'win32' else 'dragon-usb-tool')
        if not path.is_file():
            raise core.UpdateError('USB Tools is missing. Extract the complete Easy Update ZIP and keep its folders together.')
        return path
    # Source runs use a small executable wrapper supplied by the build step.
    path = Path(__file__).parent / '.tools/usb-helper/dist/dragon-usb-tool' / ('dragon-usb-tool.exe' if sys.platform == 'win32' else 'dragon-usb-tool')
    if not path.is_file():
        raise core.UpdateError('Build the bundled USB helper with package.py before USB source testing.')
    return path


def update(port, release, folder, usb_only, emit=lambda text: None, fresh=False, backup_decision=None):
    if not usb_only:
        raise core.UpdateError('Disconnect external/main power. Laptop USB must be the only power input.')
    validate(folder, release)
    if port not in {item.device for item in ports()}:
        raise core.UpdateError('USB port disappeared. Find USB dragons again.')
    recovery = service()
    tool = helper()
    if fresh:
        return recovery.install_fresh(port,True,replace_existing=True,emit=emit,cache=folder,tool=tool,backup_decision=backup_decision)
    # Existing service gate refuses unknown schemas and preserves/read-verifies NVS.
    try:current = recovery.read_running_version(port)
    except RuntimeError:current = None
    if current is None:
        return recovery.install_fresh(port,True,replace_existing=False,emit=emit,cache=folder,tool=tool,backup_decision=backup_decision)
    if current is not None and recovery.firmware_version(current) > recovery.firmware_version(release.tag):
        return 'Newer firmware is installed; no downgrade or flash write performed.'
    try:
        result = recovery.update_if_newer('', port, True, emit, cache=folder, tool=tool,backup_decision=backup_decision)
    except Exception as error:
        if 'schema is unknown' in str(error) or 'Cannot establish source schema' in str(error):
            raise core.UpdateError('Update mode could not confirm the saved-data format and left the board unchanged. Choose Fresh install if you want to replace its firmware and erase saved data; a full backup will be saved first.') from error
        raise core.UpdateError(str(error) + ' USB service files: ' + str(recovery.ROOT / '.tools/recovery')) from error
    return result + (' USB NVS backups: ' + str(recovery.ROOT / '.tools/recovery') if result.startswith('Updated') and 'without a verified backup' not in result else '')
