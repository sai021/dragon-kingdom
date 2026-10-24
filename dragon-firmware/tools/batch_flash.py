#!/usr/bin/env python3
"""Build once per target and flash mixed Dragon Kingdom ESP32-S3/C3 batches."""
import argparse
from datetime import datetime
import json
import queue
import re
import shutil
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

from dev import ROOT
from recovery import prepared_release
from board_targets import TARGETS, detect_board
from palettes import generate as generate_palettes
from embed_web import generate as generate_web
from flash_support import CACHE, FILES, save_bundle, load_bundle, check_startup, serial_modules, compiler_lock, save_release, source_fingerprint


def serial_ports(payload):
    """Accept current and older Arduino CLI discovery JSON shapes."""
    entries = payload if isinstance(payload, list) else payload.get('detected_ports', [])
    return sorted({entry['port']['address'] for entry in entries
                   if entry.get('port', {}).get('protocol') == 'serial'
                   and entry['port'].get('address')})


class Flasher:
    def __init__(self, window, cli):
        self.window, self.cli = window, cli
        self.events = queue.Queue()
        self.busy = False
        self.ready = False
        self.count = 0
        self.checked = 0
        self.last_port = None
        self.scanning = False
        self.known_ports = set()
        self.scan_generation = 0
        self.auto_initial = False
        self.auto_wait_disconnect = False
        self.auto_background = set()
        self.auto_absent_scans = 0
        self.auto_settle_until = 0
        self.operation_started = 0
        self.operation_label = ''
        self.session = CACHE / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        self.session.mkdir(parents=True)
        self.builds = {}
        for board in TARGETS:
            try:
                self.builds[board] = load_bundle(cache=CACHE, board=board)
            except (OSError, ValueError, KeyError, TypeError):
                pass
        self.ready = bool(self.builds)
        cache_message = self.bundle_summary()
        self.window.title('Dragon Kingdom — automatic S3 / C3 batch flasher')
        self.window.geometry('820x720')
        frame = ttk.Frame(window, padding=16)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Dragon Kingdom developer flasher - NOT production acceptance', font=('', 18, 'bold')).pack(anchor='w')
        ttk.Label(frame, text='Laptop USB only. Disconnect external/main power before connecting USB.',
                  foreground='#b00020').pack(anchor='w', pady=8)
        ttk.Label(frame, text='Saved firmware is ready to flash. Build only after changing the sources.\n'
                  '1. Connect one board; its port is detected automatically.\n'
                  '2. Click Flash this ESP32, or enable Auto mode for a batch.\n'
                  '3. Wait for DEVELOPER CHECK, unplug, then wait for Auto ready before the next board.').pack(anchor='w')
        row = ttk.Frame(frame)
        row.pack(fill='x', pady=12)
        self.build_button = ttk.Button(row, text='Build firmware', command=self.compile)
        self.build_button.pack(side='left')
        self.refresh_button = ttk.Button(row, text='Refresh ports', command=self.refresh)
        self.refresh_button.pack(side='left', padx=8)
        self.port = ttk.Combobox(row, state='readonly', width=16)
        self.port.pack(side='left')
        self.flash_button = ttk.Button(row, text='Flash this ESP32', command=self.flash, state='normal' if self.ready else 'disabled')
        self.flash_button.pack(side='left', padx=8)
        self.check_button = ttk.Button(frame, text='Check startup (no flash)', command=self.check)
        self.check_button.pack(anchor='w')
        self.auto_mode = tk.BooleanVar(value=False)
        self.auto_button = ttk.Checkbutton(frame, text='Auto mode — flash on connection',
                                           variable=self.auto_mode, command=self.toggle_auto)
        self.auto_button.pack(anchor='w', pady=(8, 0))
        self.auto_status = tk.StringVar(value='Auto off. Enable to flash connected boards using the saved firmware.')
        ttk.Label(frame, textvariable=self.auto_status, wraplength=760).pack(anchor='w')
        ttk.Label(frame, text='If connection fails: hold BOOT → press and release RESET → release BOOT.\n'
                  'Wait for the port to update (the COM number may change), then retry.\n'
                  'After flashing: release BOOT; press RESET if asked during the startup check.\n'
                  'Close serial monitors. Do not unplug or press buttons while writing.').pack(anchor='w', pady=10)
        self.firmware = tk.StringVar(value=cache_message)
        ttk.Label(frame, textvariable=self.firmware, wraplength=760).pack(anchor='w')
        self.status = tk.StringVar(value='Connect a board. Uploads: 0. Startup passes: 0.')
        ttk.Label(frame, textvariable=self.status, wraplength=760).pack(anchor='w', pady=5)
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=4)
        self.log = tk.Text(frame, height=18, wrap='word', state='disabled')
        self.log.pack(fill='both', expand=True)
        ttk.Label(frame, text='Startup checks firmware responses on the bare board; LEDs, sensors and Wi-Fi are not tested.').pack(anchor='w', pady=6)
        window.protocol('WM_DELETE_WINDOW', self.close)
        window.after(100, self.poll)
        window.after(100, self.auto_refresh)

    def run(self, *args):
        upload_port = None
        with subprocess.Popen([self.cli, *args], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                              errors='replace', creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)) as proc:
            with (self.session / 'uploader.log').open('a', encoding='utf-8') as capture:
                for line in proc.stdout:
                    capture.write(line)
                    capture.flush()
                    self.events.put(('log', line))
                    match = re.search(r'New upload port: (\S+)', line)
                    if match:
                        upload_port = match[1]
            if proc.wait() != 0:
                raise RuntimeError('Command failed. See the output above.')
        return upload_port

    def start(self, label, work, kind):
        if self.busy:
            return
        self.busy = True
        self.scan_generation += 1
        self.operation_started = time.monotonic()
        self.operation_label = label
        self.progress.start(50)
        self.status.set(label)
        for button in (self.build_button, self.refresh_button, self.flash_button, self.check_button):
            button.configure(state='disabled')
        self.port.configure(state='disabled')
        def worker():
            try:
                result = work()
                self.events.put(('done', (kind, result)))
            except Exception as error:
                self.events.put(('error', str(error)))
        threading.Thread(target=worker, daemon=True).start()

    def bundle_summary(self):
        return 'Saved firmware: ' + ', '.join(
            board.upper() + ': ' + (self.builds[board].name if board in self.builds else 'build required')
            for board in TARGETS)

    def compile(self):
        if self.busy:
            return
        self.stop_auto('Build firmware, then enable Auto mode again when ready.')
        def work():
            with compiler_lock(CACHE):
                self.compile_targets()
        self.start('Building S3 and C3 firmware…', work, 'build')

    def compile_targets(self):
        generate_palettes()
        generate_web()
        source_hash=source_fingerprint()
        staged={}
        for board, fqbn in TARGETS.items():
            candidate = CACHE / (datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '-' + board)
            candidate.mkdir(parents=True)
            # Reuse object files; publish a separate immutable upload bundle only on success.
            workspace = CACHE / ('work-' + board)
            self.events.put(('stage', 'Building ' + board.upper() + ' firmware (first build can take several minutes)…'))
            self.run('compile', '--verbose', '--fqbn', fqbn, '--build-path', str(workspace), str(ROOT / 'DragonPrototype'))
            for name in (*FILES, 'build.options.json'):
                shutil.copy2(workspace / name, candidate / name)
            staged[board] = candidate
        if source_fingerprint()!=source_hash:
            raise RuntimeError('Sources changed during compilation. Previous saved firmware kept; build again.')
        save_release(staged, cache=CACHE, source_sha256=source_hash)
        self.builds = staged

    def refresh(self):
        if self.busy or self.scanning:
            return
        self.scanning = True
        generation = self.scan_generation
        def worker():
            try:
                result = subprocess.run([self.cli, 'board', 'list', '--format', 'json'],
                                        capture_output=True, text=True, check=True, timeout=10,
                                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                self.events.put(('ports', (generation, serial_ports(json.loads(result.stdout)))))
            except Exception as error:
                self.events.put(('scan_error', (generation, str(error))))
        threading.Thread(target=worker, daemon=True).start()

    def auto_refresh(self):
        self.refresh()
        self.window.after(2000, self.auto_refresh)

    def update_ports(self, ports):
        previous = self.port.get()
        added = set(ports) - self.known_ports
        self.known_ports = set(ports)
        self.port.configure(values=ports)
        if len(ports) == 1:
            selected = ports[0]
        elif len(added) == 1:
            selected = next(iter(added))
        else:
            selected = previous if previous in ports else ''
        self.port.set(selected)
        self.maybe_auto_flash(set(ports), added)

    def stop_auto(self, reason):
        self.auto_mode.set(False)
        self.auto_status.set('Auto off. ' + reason)

    def toggle_auto(self):
        # Require a fresh discovery after the user's change of mode.
        self.scan_generation += 1
        if not self.auto_mode.get():
            self.auto_status.set('Auto off. Any current operation will finish normally.')
            return
        if not self.ready:
            self.stop_auto('Build firmware first, then enable Auto mode.')
            return
        self.auto_initial = True
        # Preserve the unplug latch when toggled during/after an operation.
        self.auto_status.set('Auto on — checking ports. A single connected board will flash automatically.')
        self.refresh()

    def wait_for_disconnect(self, port):
        # Treat all other current ports as background devices. Any new port may
        # be this board re-enumerating from ROM to firmware, so it also blocks
        # rearming until an actual unplug has been observed.
        self.auto_background = self.known_ports - {port}
        self.auto_wait_disconnect = True
        self.auto_absent_scans = 0
        self.auto_initial = False
        if self.auto_mode.get():
            self.auto_status.set('Auto on — processing this board. Wait for DEVELOPER CHECK before unplugging.')

    def maybe_auto_flash(self, ports, added):
        if not self.auto_mode.get() or self.busy or not self.ready:
            return
        if self.auto_wait_disconnect:
            if time.monotonic() < self.auto_settle_until:
                return
            self.auto_absent_scans = self.auto_absent_scans + 1 if ports <= self.auto_background else 0
            if self.auto_absent_scans < 2:
                self.auto_status.set('Auto on — unplug the finished board, then wait for Auto ready.')
                return
            self.auto_wait_disconnect = False
            self.auto_initial = False
            self.auto_status.set('Auto ready — connect the next ESP32 to flash automatically.')
            return
        candidates = ports if self.auto_initial else added
        self.auto_initial = False
        if len(candidates) > 1:
            self.stop_auto('Several ports appeared. Select the board and click Flash this ESP32, or reconnect one board at a time.')
        elif candidates:
            self.port.set(next(iter(candidates)))
            self.flash()
        else:
            self.auto_status.set('Auto ready — connect an ESP32 to flash automatically.')

    def flash(self):
        if self.busy:
            return
        port = self.port.get()
        if not self.ready or not port:
            messagebox.showinfo('Before flashing', 'Build firmware and connect the board. If several ports are present, select its port.')
            return
        self.wait_for_disconnect(port)
        def work():
            prepared_release(CACHE) # Same signed compatibility/hash/layout gate as recovery, even for developer uploads.
            serial_modules()  # Check dependency before uploading.
            # Recheck presence immediately before upload. Never erase the whole flash/NVS.
            result = subprocess.run([self.cli, 'board', 'list', '--format', 'json'],
                                    capture_output=True, text=True, check=True, timeout=10,
                                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            if port not in serial_ports(json.loads(result.stdout)):
                raise RuntimeError('Selected port disappeared. Refresh ports and select the board again.')
            self.events.put(('log', '\nReading chip identity on ' + port + '…\n'))
            board = detect_board(self.cli, port)
            self.events.put(('log', 'Detected ESP32-' + board.upper() + '.\n'))
            if board not in self.builds:
                raise RuntimeError('No saved ' + board.upper() + ' firmware. Click Build firmware, then retry. Nothing was written.')
            if load_bundle(board=board) != self.builds[board]:
                raise RuntimeError('Saved firmware changed. Reopen the flasher before uploading.')
            self.events.put(('log', 'Uploading matching ' + board.upper() + ' firmware to ' + port + '\n'))
            runtime_port = self.run('upload', '--fqbn', TARGETS[board], '--port', port,
                     '--input-dir', str(self.builds[board]), str(ROOT / 'DragonPrototype'))
            runtime_port = runtime_port or port
            self.events.put(('uploaded', runtime_port))
            return self.verify(runtime_port)
        self.start('Writing firmware — keep USB connected…', work, 'flash')

    def verify(self, port):
        self.events.put(('checking', None))
        def emit(line):
            with (self.session / 'startup.log').open('a', encoding='utf-8') as capture:
                capture.write(line)
            self.events.put(('log', line))
        result=check_startup(port, emit)
        return 'DEVELOPER CHECK ONLY: '+result+' Use Recover Dragon with a signed release for production.'

    def check(self):
        if self.busy:
            return
        port = self.port.get() or self.last_port
        if not port:
            messagebox.showinfo('Connect a board', 'Connect the ESP32 and wait for its port to appear.')
            return
        self.wait_for_disconnect(port)
        self.start('Checking startup…', lambda: self.verify(port), 'check')

    def poll(self):
        try:
            # Verbose compiler output must not starve Tk's redraw/timer events.
            for _ in range(100):
                kind, value = self.events.get_nowait()
                if kind == 'stage':
                    self.operation_label = value
                    self.events.put(('log', '\n' + value + '\n'))
                    continue
                if kind == 'uploaded':
                    self.count += 1
                    self.last_port = value
                    continue
                if kind == 'checking':
                    self.status.set('Upload/check: waiting for Dragon Kingdom. Release BOOT and press RESET now if needed. Keep USB connected (up to 45 seconds).')
                    continue
                if kind in ('ports', 'scan_error'):
                    self.scanning = False
                    # Discard discovery started before an upload/build began.
                    generation, discovery = value
                    if not self.busy and generation == self.scan_generation:
                        if kind == 'ports':
                            self.update_ports(discovery)
                        elif self.auto_mode.get():
                            # A failed discovery is not evidence of unplugging.
                            self.stop_auto('Port discovery failed. Refresh ports and enable Auto mode again. ' + discovery)
                    continue
                if kind == 'log':
                    self.log.configure(state='normal')
                    self.log.insert('end', value[:1200] + ('…\n' if len(value)>1200 else ''))
                    if int(self.log.index('end-1c').split('.')[0]) > 800:
                        self.log.delete('1.0', '200.0')
                    self.log.see('end')
                    self.log.configure(state='disabled')
                    continue
                self.busy = False
                self.auto_settle_until = time.monotonic() + 3
                self.progress.stop()
                self.ready = bool(self.builds)
                self.firmware.set(self.bundle_summary())
                if kind == 'error':
                    self.stop_auto('Operation failed. Resolve the error; retry manually or unplug and enable Auto mode again.')
                    self.status.set(value + f' Uploads: {self.count}. Startup passes: {self.checked}.')
                else:
                    action, result = value
                    if action == 'build':
                        self.ready = True
                        self.status.set('Firmware ready. Connect a board; its port will appear automatically. If several are present, select one.')
                    elif action in ('flash', 'check'):
                        self.checked += 1
                        self.status.set(f'DEVELOPER CHECK — not production acceptance; unplug before swapping. Uploads: {self.count}. Startup passes: {self.checked}.')
                        if self.auto_mode.get():
                            self.auto_status.set('Auto on — unplug the finished board, then wait for Auto ready.')
                self.build_button.configure(state='normal')
                self.refresh_button.configure(state='normal')
                self.check_button.configure(state='normal')
                self.port.configure(state='readonly')
                self.flash_button.configure(state='normal' if self.ready else 'disabled')
        except queue.Empty:
            pass
        if self.busy and self.operation_label.startswith('Building'):
            elapsed = int(time.monotonic() - self.operation_started)
            self.status.set(self.operation_label + f' Elapsed {elapsed // 60}:{elapsed % 60:02d}. Compiler output appears below.')
        self.window.after(100, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo('Operation in progress', 'Wait for the current operation to finish before closing.')
        else:
            self.window.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', default=str(ROOT / '.tools' / 'arduino-cli' / 'arduino-cli.exe')
                        if (ROOT / '.tools' / 'arduino-cli' / 'arduino-cli.exe').exists() else 'arduino-cli')
    args = parser.parse_args()
    cli = shutil.which(args.cli)
    if not cli:
        parser.error('Arduino CLI not found. Use --cli PATH; run tools/dev.py setup first.')
    Flasher(tk.Tk(), cli).window.mainloop()


if __name__ == '__main__':
    main()
