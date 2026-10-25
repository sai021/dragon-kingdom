"""Sequential direct-Wi-Fi updates after one explicit user action."""
from dataclasses import dataclass
import time

import updater_core as core
import wifi_control as wifi


@dataclass
class Result:
    ssid: str
    status: str
    detail: str
    device: object = None


def probe_network(network, cancel, timeout=25):
    deadline = time.monotonic() + timeout
    while True:
        if cancel.is_set():
            raise core.Cancelled('Stopped before installation.')
        try:
            device = core.Device.probe('192.168.4.1', timeout=3)
            break
        except core.UpdateError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(1)
    if device.hostname.casefold() != network.ssid.casefold():
        raise core.UpdateError('Lamp identity does not match its Wi-Fi network. Nothing installed.')
    return device


def run(session, release, password, cancel, progress=lambda text, percent: None,
        on_result=lambda result: None):
    # A complete, verified release is required before any connection changes.
    if not isinstance(release, core.PreparedRelease):
        raise core.UpdateError('Download verified offline firmware before scanning.')
    if not password:
        raise core.UpdateError('Enter the parent password before scanning.')
    if session.changed:
        session.restore()
    progress('Scanning for dragon setup networks...', 0)
    networks = {}
    for network in session.adapter.scan():
        wifi.dragon_name(network.ssid)
        networks.setdefault(network.ssid.casefold(), network)
    results = []
    stopped = False
    for index, network in enumerate(networks.values(), 1):
        if cancel.is_set() or stopped:
            result = Result(network.ssid, 'Not attempted', 'Batch stopped before this lamp.')
        else:
            device = None
            try:
                progress(f'{index}/{len(networks)}: connecting to {network.ssid}...', 0)
                session.join(network)
                device = probe_network(network, cancel)
                installed, offered = core.version(device.firmware), core.version(release.tag)
                if installed >= offered:
                    result = Result(network.ssid, 'Already current' if installed == offered else 'Newer installed',
                                    'No installation needed; no downgrade performed.', device)
                else:
                    def step(text, percent):
                        progress(f'{index}/{len(networks)} · {network.ssid}: {text}', percent)
                    verified = core.update(device, release, password, step, cancel,
                                           direct=True, reconnect=session.reconnect, reboot_timeout=300)
                    device = core.Device(verified['address'], device.hostname, device.board, verified['firmware'])
                    result = Result(network.ssid, 'Updated', 'Startup and settings verified. Backup: ' + verified['backup'], device)
            except core.Cancelled as error:
                cancel.set()
                result = Result(network.ssid, 'Stopped', str(error), device)
            except Exception as error:
                result = Result(network.ssid, 'Needs attention', str(error), device)
            finally:
                try:
                    session.restore()
                except Exception:
                    # Do not risk capturing a dragon AP as the next "original".
                    stopped = True
                    result.detail += ' Original Wi-Fi could not be restored; batch stopped. Rejoin it using the computer Wi-Fi menu.'
        results.append(result)
        on_result(result)
    return results
