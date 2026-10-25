"""Import signed firmware from a local PC without accessing the internet."""
import io
import json
from pathlib import Path
import tempfile
import zipfile
import updater_core as core
import usb_update as usb

LIMIT = core.MAX_PACKAGE * 4 + 8 * 1024 * 1024 + 65536


def create_file(path, prepared_folder, usb_folder):
    """Maker utility: combine already verified Wi-Fi and USB files for families."""
    prepared = core.PreparedRelease.load(prepared_folder)
    usb.validate(Path(usb_folder), prepared)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(Path(prepared_folder)/'offline-release.json', 'offline-release.json')
        for name in ['current-set.json'] + [board+'/'+name for board in ('s3','c3') for name in usb.FILES]:
            archive.write(Path(usb_folder)/name, 'usb/'+name)
    return Path(path)


def load(path):
    path = Path(path)
    if not 0 < path.stat().st_size <= LIMIT:
        raise core.UpdateError('Choose a valid signed firmware file (up to 22 MB).')
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        if path.suffix.lower() == '.json':
            (folder / 'offline-release.json').write_bytes(path.read_bytes())
            prepared = core.PreparedRelease.load(folder)
            return core.prepare_offline(prepared), None
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if 'offline-release.json' not in names:
                destination = usb.store_archive(path.read_bytes())
                info = usb.service().prepared_release(destination)
                return None, core.Release(info['firmware_tag'], info)
            expected = {'offline-release.json', 'usb/current-set.json'} | {
                'usb/' + board + '/' + name for board in ('s3', 'c3') for name in usb.FILES}
            if len(names) != len(set(names)) or set(names) != expected:
                raise core.UpdateError('Unexpected contents in the firmware file.')
            if sum(x.file_size for x in archive.infolist()) > LIMIT:
                raise core.UpdateError('Expanded firmware file is too large.')
            entry = archive.getinfo('offline-release.json')
            if not 0 < entry.file_size <= core.MAX_PACKAGE * 4 + 65536:
                raise core.UpdateError('Invalid offline firmware size.')
            (folder / entry.filename).write_bytes(archive.read(entry))
            prepared = core.PreparedRelease.load(folder)
            raw = io.BytesIO()
            with zipfile.ZipFile(raw, 'w', zipfile.ZIP_DEFLATED) as bundle:
                for name in sorted(expected - {'offline-release.json'}):
                    entry = archive.getinfo(name)
                    maximum = core.MAX_IMAGE if name.endswith('.bin') else 16384
                    if not 0 < entry.file_size <= maximum:
                        raise core.UpdateError('Invalid USB firmware file size.')
                    bundle.writestr(name[4:], archive.read(entry))
            usb.store_archive(raw.getvalue(), prepared)
            return core.prepare_offline(prepared), core.Release(prepared.tag, prepared.info)
