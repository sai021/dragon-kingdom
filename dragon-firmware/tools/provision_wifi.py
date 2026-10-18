"""Provision home Wi-Fi over trusted USB CDC without echoing credentials."""
import argparse
import getpass
import json
from pathlib import Path
import re
import time

from flash_support import serial_modules


def join_command(ssid, password):
    name, key = ssid.encode('utf-8'), password.encode('utf-8')
    valid_key = not key or 8 <= len(key) <= 63 or (
        len(key) == 64 and all(c in b'0123456789abcdefABCDEF' for c in key))
    if not 1 <= len(name) <= 32 or b'\0' in name or b'\0' in key or not valid_key:
        raise ValueError('Invalid Wi-Fi name or password length/format.')
    return ('wifi join ' + name.hex() + ' ' + (key.hex() or '-') + '\n').encode('ascii')


def provision(port, command, timeout=90, emit=print):
    serial, _ = serial_modules()
    connection = serial.Serial(port=None, baudrate=115200, timeout=.2, write_timeout=1)
    connection.dtr = True
    connection.rts = False
    connection.port = port
    deadline, last_poll, last_join = time.monotonic() + timeout, 0, 0
    accepted, ready, last_signature = False, False, None
    try:
        connection.open()
        connection.reset_input_buffer()
        while time.monotonic() < deadline:
            now = time.monotonic()
            if now - last_poll >= 1:
                connection.write(b'wifi status\n')
                last_poll = now
            if ready and not accepted and now - last_join >= 5:
                connection.write(command)
                last_join = now
            line = connection.readline().decode('utf-8', errors='replace').strip()
            if line.startswith('Wi-Fi request accepted'):
                accepted = True
                emit('Wi-Fi join accepted; credentials are not displayed.')
            if line.startswith('network_status '):
                ready = True
                state = dict(re.findall(r'(\w+)=([^ ]+)', line))
                signature = (state.get('connected'), state.get('configured'),
                             state.get('status'), state.get('disconnect_reason'))
                if signature != last_signature:
                    emit(line)
                    last_signature = signature
                # Confirm this join, rather than returning an older saved connection.
                if (accepted and state.get('connected') == state.get('configured') == '1'
                        and state.get('joining') == '0' and state.get('join_saved') == '1'):
                    return state
            if line.startswith(('Guru Meditation', 'panic', 'abort()')):
                raise RuntimeError('Firmware crash during Wi-Fi provisioning.')
        raise RuntimeError('Wi-Fi join was not confirmed. Check band, signal, router access and credentials.')
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True)
    parser.add_argument('--credentials-file', type=Path,
                        help='Ignored local JSON file containing ssid and password; never commit it.')
    parser.add_argument('--timeout', type=int, default=90)
    args = parser.parse_args()
    if args.credentials_file:
        values = json.loads(args.credentials_file.read_text(encoding='utf-8'))
        ssid, password = values['ssid'], values['password']
    else:
        ssid = input('Home Wi-Fi name: ')
        password = getpass.getpass('Home Wi-Fi password (not displayed): ')
    try:
        provision(args.port, join_command(ssid, password), args.timeout)
    except (ValueError, RuntimeError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
