"""Desktop entry point. Startup downloads only; installation needs a user click."""
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import updater_core as core
import wifi_control as wifi
import batch_update as batch
import usb_update as usb


class App:
    def __init__(self, root, online=True):
        self.root, self.events = root, queue.Queue()
        self.devices, self.release, self.live_release, self.prepared = [], None, None, None
        self.busy, self.installing, self.finalizing = False, False, False
        self.cancel = threading.Event()
        self.wifi_session = None
        self.usb_writing = False
        self.usb_gate = usb.gate()
        self.usb_auto = tk.BooleanVar(value=False)
        self.usb_records = []
        self.usb_fresh = tk.BooleanVar(value=False)
        from workshop_ui import build
        build(self, root)
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.drain)
        self.change_mode()
        root.after(1000, self.usb_tick)
        if online:
            self.startup_refresh()

    def startup_refresh(self):
        self.status.set('Checking for the latest stable firmware; saved files remain available offline...')
        def job():
            try: cached = core.PreparedRelease.load()
            except core.UpdateError: cached = None
            try:
                latest = core.Release.latest()
                if cached and core.version(cached.tag) >= core.version(latest.tag) and (cached.tag != latest.tag or cached.info == latest.info):
                    return cached, ''
                return core.prepare_offline(latest, progress=lambda text, percent: self.events.put(('progress', text, percent))), ''
            except Exception:
                return cached, 'Could not refresh the stable release. ' + ('Using the verified saved copy; it may not be the newest release.' if cached else 'Connect to internet and choose Download for offline use before updating.')
        def done(result):
            self.prepared, warning = result
            self.release = self.prepared
            self.live_release = self.prepared
            self.offered.set('Verified offline firmware: ' + self.prepared.tag if self.prepared else 'No verified firmware downloaded yet.')
            self.status.set(warning or 'Latest stable firmware ready: ' + self.prepared.tag + '. Choose Find & update all dragons.')
        self.run(job, done)

    def is_direct(self):
        return self.mode.get() == 'Dragon setup Wi-Fi (offline)'

    def is_usb(self):
        return self.mode.get() == 'USB cable'

    def change_mode(self):
        if not self.is_direct() and self.wifi_session and self.wifi_session.changed:
            self.restore_wifi(after=self.change_mode); return
        self.release = self.prepared if self.is_direct() or self.is_usb() else self.live_release
        self.show_devices([])
        self.usb_fresh.set(False)
        self.usb_gate.stop(); self.usb_auto.set(False)
        from workshop_ui import TEAL, CARD, FOREST
        for value, button in self.mode_buttons:
            selected = self.mode.get() == value
            button.configure(background=TEAL if selected else CARD, foreground='white' if selected else FOREST)
        if self.is_usb():
            self.usb_group.pack(fill='x', before=self.devices_frame)
            self.auth.pack_forget()
        else:
            self.usb_group.pack_forget()
            self.auth.pack(fill='x', pady=(2, 8), before=self.actions)
        if self.is_usb():
            self.find.configure(text='Find USB dragons')
            self.add.configure(text='USB ports listed at left')
            self.check.configure(text='Download USB files')
            self.instructions.set('Disconnect external/product power before connecting laptop USB to the internal ESP32. Choose Update to keep saved dragons, or Fresh install for an empty/reused board. Enable Auto, then connect one board at a time. Keep USB Tools with the app.')
            self.status.set('USB discovery lists ports without opening or resetting the board. Use Auto or choose a port to update manually.')
        elif self.is_direct():
            self.find.configure(text='Find & update all dragons')
            self.add.configure(text='Manual connection')
            self.check.configure(text='Return to original Wi-Fi')
            self.instructions.set('Find & update all dragons scans nearby Dragon-Kingdom setup networks, connects to each and updates older firmware automatically. Current/newer lamps are skipped. Only use it where all nearby dragons are yours to update. Allow OS Wi-Fi/location permission if asked.\nFor lamps already connected to home Wi-Fi, choose Home Wi-Fi mode instead; their setup network closes after 15 seconds.')
            self.status.set('Ready to scan nearby dragon Wi-Fi networks. Automatic connection temporarily disconnects this computer from its current Wi-Fi.')
        else:
            self.find.configure(text='Find dragons')
            self.add.configure(text='Add address')
            self.check.configure(text='Check for updates')
            self.instructions.set('Connect the lamp and this computer to the same home network. Choose Check for updates, then Find dragons.\nFor a lamp without home Wi-Fi, choose Dragon setup Wi-Fi (offline) above.')
            self.status.set('Ready. Check for updates and find your dragon.')
        self.offered.set(('Prepared offline firmware: ' if self.is_direct() else 'Main firmware available: ') + self.release.tag if self.release else 'No verified offline download yet.' if self.is_direct() else 'Choose Check for updates while connected to internet.')
        if self.is_usb():
            self.address.pack_forget(); self.add.pack_forget()
        elif self.is_direct():
            self.address.pack_forget()
            self.add.pack(side='left', padx=8, before=self.check)
        else:
            self.address.pack(side='left', padx=(10,5), before=self.check)
            self.add.pack(side='left', before=self.check)
        self.controls(False)

    def controls(self, busy):
        self.busy = busy
        for widget in (self.find, self.add, self.check, self.install, self.address, self.password, self.prepare):
            widget.configure(state='disabled' if busy else 'normal')
        for choice in self.fresh_choices: choice.configure(state='disabled' if busy else 'normal')
        for value, button in self.mode_buttons: button.configure(state='disabled' if busy else 'normal')
        self.mode_picker.configure(state='disabled' if busy else 'readonly')
        if self.is_usb():
            self.add.configure(state='disabled')
            self.address.configure(state='disabled')
            self.password.configure(state='disabled')
        if self.is_direct():
            self.address.configure(state='disabled')
        self.usb_auto_button.configure(state='disabled' if busy else 'normal')
        if self.usb_gate.enabled:
            for widget in (self.find, self.add, self.check, self.prepare, self.install): widget.configure(state='disabled')
            self.mode_picker.configure(state='disabled')
            for choice in self.fresh_choices: choice.configure(state='disabled')
            for value, button in self.mode_buttons: button.configure(state='disabled')
        self.stop.configure(text='Stop after this dragon' if self.finalizing or self.usb_writing else 'Stop', state='normal' if (busy and self.installing) or self.usb_gate.enabled else 'disabled')

    def run(self, job, done):
        if self.busy: return
        self.cancel.clear(); self.finalizing = False; self.bar['value'] = 0
        self.controls(True)
        if self.usb_writing:
            self.bar.configure(mode='indeterminate'); self.bar.start(25)
        else:
            self.bar.configure(mode='determinate')
        def worker():
            try: self.events.put(('done', done, job()))
            except Exception as error: self.events.put(('error', str(error)))
        threading.Thread(target=worker, daemon=True).start()

    def drain(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == 'progress':
                    self.status.set(event[1]); self.bar['value'] = event[2]
                    if self.installing:
                        self.finalizing = event[2] >= 88
                        self.stop.configure(text='Stop after this dragon' if self.finalizing else 'Stop', state='normal')
                elif event[0] == 'backup_prompt':
                    self.show_backup_prompt(event[1], event[2], event[3])
                elif event[0] == 'batch_result':
                    self.show_batch_result(event[1])
                elif event[0] == 'done':
                    self.installing = False; self.controls(False); event[1](event[2])
                else:
                    self.installing = False
                    if self.usb_writing:
                        self.usb_records.append(batch.Result(self.usb_port, 'Needs attention', event[1]))
                    self.usb_writing = False; self.usb_gate.stop(); self.usb_auto.set(False); self.bar.stop(); self.bar.configure(mode='determinate'); self.controls(False); self.status.set(event[1])
                    messagebox.showerror('Update not completed', event[1], parent=self.root)
        except queue.Empty: pass
        self.root.after(100, self.drain)

    def show_devices(self, devices):
        self.devices = devices
        for item in self.tree.get_children(): self.tree.delete(item)
        for index, d in enumerate(devices): self.tree.insert('', 'end', iid=str(index), values=(d.hostname, d.board.upper(), d.firmware, d.address))
        if devices: self.tree.selection_set('0')
        self.status.set(f'Found {len(devices)} dragon(s). Select yours.' if devices else 'No dragons found. Check home Wi-Fi, or enter the lamp address and choose Add address.')

    def find_devices(self):
        if self.is_usb():
            def done(ports):
                self.show_devices([core.Device(p.device, p.description or p.device, 'usb', 'Read on update') for p in ports])
                self.status.set('Select the USB port, confirm USB-only power and choose Update selected dragon.' if ports else 'No USB ports found. Check the data cable and ESP32 connector; try BOOT/RESET if needed.')
            self.run(usb.ports, done)
            return
        if self.is_direct():
            try:
                if self.wifi_session is None:self.wifi_session = wifi.Session(wifi.controller())
            except Exception as error:
                messagebox.showerror('Automatic Wi-Fi unavailable', str(error) + '\nYou can still join the dragon Wi-Fi yourself and choose Manual connection.', parent=self.root); return
            if not self.password.get():
                messagebox.showinfo('Parent password needed', 'Enter the parent password before updating.', parent=self.root); return
            password = self.password.get()
            self.show_devices([])
            self.installing = True
            def job():
                if not self.prepared:
                    raise core.UpdateError('No verified firmware is ready. Connect to internet and choose Download for offline use first.')
                return batch.run(self.wifi_session, self.prepared, password, self.cancel,
                    progress=lambda text, percent: self.events.put(('progress', text, percent)),
                    on_result=lambda result: self.events.put(('batch_result', result)))
            def done(results):
                if not results:
                    self.status.set('No dragon setup networks found. For lamps already on home Wi-Fi, use Home Wi-Fi mode.'); return
                counts = {status: sum(r.status == status for r in results) for status in dict.fromkeys(r.status for r in results)}
                self.status.set('Finished: ' + ', '.join(f'{number} {status.lower()}' for status, number in counts.items()))
                self.show_batch_report(results)
            self.status.set('Scanning and updating nearby dragons. Keep normal lamp power connected.')
            self.run(job, done)
            return
        self.status.set('Finding dragons on this computer\'s local network...')
        self.run(lambda: core.discover(self.cancel), self.show_devices)

    def add_address(self):
        if self.is_direct():
            if not self.prepared:
                messagebox.showinfo('Download first', 'Prepare signed files while on internet, then join the dragon Wi-Fi and try Manual connection.', parent=self.root); return
            self.run(lambda: [core.Device.probe('192.168.4.1',timeout=4)],self.show_devices)
            return
        address = self.address.get().strip()
        self.run(lambda: core.Device.probe(address, timeout=4), lambda d: self.show_devices([x for x in self.devices if x.hostname != d.hostname] + [d]))

    def check_release(self):
        if self.is_usb():
            self.prepare_usb(); return
        if self.is_direct():
            self.restore_wifi(); return
        def done(release):
            self.release = self.live_release = release
            self.offered.set('Main firmware available: ' + release.tag)
            self.status.set('Choose Find dragons, or add the address from its webpage.')
        self.run(core.Release.latest, done)

    def prepare_offline(self):
        if self.is_usb():
            self.prepare_usb(); return
        def progress(text, percent): self.events.put(('progress', text, percent))
        def done(release):
            self.prepared = release
            if self.is_direct(): self.release = release
            self.offered.set('Offline firmware ready: ' + release.tag + ' (both board types)')
            self.status.set('Download verified and saved. Choose Dragon setup Wi-Fi (offline), then Find & update all dragons. You can close and reopen this app offline.')
        self.run(lambda: core.prepare_offline(progress=progress), done)

    def request_stop(self):
        if self.is_usb():
            self.usb_gate.stop(); self.usb_auto.set(False)
            self.controls(self.busy)
            self.status.set('USB Auto stopped. Any current USB update will finish verification; keep its cable connected.')
            if not self.busy and self.usb_records: self.show_batch_report(self.usb_records)
        else:
            self.cancel.set()

    def backup_decision(self, message):
        decision = {'continue': False}
        answered = threading.Event()
        self.events.put(('backup_prompt', message, decision, answered))
        answered.wait()
        return decision['continue']

    def show_backup_prompt(self, message, decision, answered):
        from workshop_ui import PAPER
        dialog = tk.Toplevel(self.root); dialog.title('Backup unavailable')
        dialog.configure(background=PAPER); dialog.transient(self.root)
        ttk.Label(dialog, text='The backup could not be made', style='Section.TLabel').pack(anchor='w', padx=24, pady=(20,10))
        ttk.Label(dialog, text=message, wraplength=620).pack(anchor='w', padx=24, pady=(0,18))
        row = ttk.Frame(dialog, padding=(24,0,24,20)); row.pack(fill='x')
        def answer(continue_without):
            decision['continue'] = continue_without
            dialog.destroy(); answered.set()
        abort = ttk.Button(row, text='Abort', command=lambda: answer(False)); abort.pack(side='left')
        ttk.Button(row, text='Continue without backup', command=lambda: answer(True)).pack(side='right')
        dialog.protocol('WM_DELETE_WINDOW', lambda: answer(False))
        dialog.bind('<Escape>', lambda event: answer(False)); dialog.bind('<Return>', lambda event: answer(False))
        abort.focus_set(); dialog.grab_set()

    def fresh_changed(self):
        self.controls(self.busy)
        self.status.set('Fresh install replaces existing firmware and saved data. Backup runs automatically; you are only prompted if it cannot be made.' if self.usb_fresh.get() else 'Update mode preserves saved dragons. Empty boards are initialized only after verifying the entire flash is erased.')

    def toggle_usb_auto(self):
        if not self.usb_auto.get():
            self.request_stop(); return
        if self.busy:
            self.usb_auto.set(False); return
        def arm():
            self.usb_records = []
            self.usb_gate.arm()
            self.controls(False)
            self.status.set('USB Auto ready. Connect one ESP32 at a time; keep external power disconnected.')
        self.prepare_usb(after=arm)

    def usb_tick(self):
        if self.is_usb() and self.usb_gate.enabled and not self.busy:
            try:
                current = {p.device for p in usb.ports() if p.vid == 0x303a}
                waiting = self.usb_gate.waiting
                chosen = self.usb_gate.choose(current)
                if chosen:
                    self.show_devices([core.Device(chosen, 'USB dragon', 'usb', 'Read on update')])
                    self.install_usb(automatic=True)
                elif waiting and not self.usb_gate.waiting:
                    self.status.set('USB Auto ready. Connect the next board. Completed: ' + str(len(self.usb_records)))
            except Exception as error:
                self.usb_gate.stop(); self.usb_auto.set(False); self.controls(False)
                self.status.set('USB Auto stopped: ' + str(error))
        self.root.after(1000, self.usb_tick)

    def usb_release(self):
        candidates = [r for r in (self.prepared, self.live_release, self.release) if r]
        if candidates:
            return max(candidates, key=lambda r: core.version(r.tag))
        try: return usb.cached_release()
        except core.UpdateError: return None

    def prepare_usb(self, after=None):
        def job():
            release = self.usb_release() or core.Release.latest()
            return release, usb.prepare(release)
        def done(result):
            self.release, folder = result
            self.offered.set('Verified USB firmware ready: ' + self.release.tag)
            self.status.set('USB files saved for offline use. Enable USB Auto or select a port to update manually.')
            if after: after()
        self.run(job, done)

    def install_usb(self, automatic=False):
        selected = self.tree.selection()
        if not selected or not selected[0].isdigit():
            messagebox.showinfo('Choose a USB port', 'Choose Find USB dragons, then select the connected board.', parent=self.root); return
        fresh = self.usb_fresh.get()
        port = self.devices[int(selected[0])].address
        release = self.usb_release()
        self.usb_port = port
        self.usb_writing = True
        self.status.set('Preparing signed USB firmware. Keep laptop USB connected throughout recovery and verification.')
        def job():
            target = release or core.Release.latest()
            folder = usb.prepare(target)
            result = usb.update(port, target, folder, True, emit=lambda text: self.events.put(('progress', str(text), 0)), fresh=fresh, backup_decision=self.backup_decision)
            return result
        def done(result):
            self.usb_writing = False
            self.bar.stop(); self.bar.configure(mode='determinate')
            self.usb_records.append(batch.Result(port, 'Updated' if result.startswith('Updated') else 'Skipped', result))
            self.bar['value'] = 100
            if automatic:
                self.usb_gate.finished()
                if self.usb_gate.enabled:
                    self.status.set(result + ' Unplug this board and wait for USB Auto ready before the next.')
                else:
                    self.status.set(result + ' USB Auto stopped.')
                    self.show_batch_report(self.usb_records)
            else:
                self.status.set(result)
                messagebox.showinfo('USB update result', result + '\nDisconnect laptop USB before restoring normal product power. Check normal lighting and touch afterward.', parent=self.root)
            self.controls(False)
        self.run(job, done)

    def show_batch_result(self, result):
        device = result.device
        item = str(len(self.devices)) if device else None
        if device:
            self.devices.append(device)
        self.tree.insert('', 'end', iid=item, values=(result.ssid, device.board.upper() if device else '',
            device.firmware if device else '', device.address if device else '', result.status))
        self.status.set(result.ssid + ': ' + result.status + '. ' + result.detail)

    def show_batch_report(self, results):
        dialog = tk.Toplevel(self.root)
        dialog.title('Easy Update results')
        dialog.geometry('760x480')
        from tkinter.scrolledtext import ScrolledText
        text = ScrolledText(dialog, wrap='word', padx=14, pady=14)
        text.pack(fill='both', expand=True)
        text.insert('end', '\n\n'.join(r.ssid + ' — ' + r.status + '\n' + r.detail for r in results))
        text.insert('end', '\n\nCheck normal lighting and touch controls on updated lamps. If a lamp needs attention, check its installed version before retrying.')
        text.configure(state='disabled')
        ttk.Button(dialog, text='Close', command=dialog.destroy).pack(pady=10)

    def restore_wifi(self,after=None):
        if not self.wifi_session or not self.wifi_session.changed:
            if after:after()
            else:self.status.set('The app has not changed your Wi-Fi connection.')
            return
        self.status.set('Returning to the original Wi-Fi connection...')
        def done(value):
            self.status.set('Original Wi-Fi restored. You can scan another dragon or use Home Wi-Fi mode.')
            if after:after()
        self.run(self.wifi_session.restore,done)

    def install_selected(self):
        if self.is_usb():
            self.install_usb(); return
        selected = self.tree.selection()
        if not selected or not selected[0].isdigit() or not self.release:
            messagebox.showinfo('Choose a dragon and release', 'Find and select your lamp, then check for updates.', parent=self.root); return
        device, release = self.devices[int(selected[0])], self.release
        try:
            if core.version(release.tag) <= core.version(device.firmware):
                raise core.UpdateError('This lamp already has the offered firmware or newer.')
            core.legacy(device.firmware)
        except core.UpdateError as error:
            messagebox.showinfo('No installation', str(error), parent=self.root); return
        password = self.password.get()
        if not password:
            messagebox.showinfo('Parent password needed', 'Enter the existing parent password (normally dragon123).', parent=self.root); return
        direct = self.is_direct()
        automatic=direct and self.wifi_session and self.wifi_session.changed
        self.status.set('Saving a backup and updating ' + device.hostname + '. Keep lamp power and Wi-Fi connected until verification finishes.')
        self.installing = True
        def progress(text, percent):
            if direct and percent == 88:
                text += ' Reconnecting automatically; waiting up to five minutes.' if automatic else ' Rejoin dragon Wi-Fi after restart if needed; waiting up to five minutes.'
            self.events.put(('progress', text, percent))
        def done(result):
            self.status.set('Update verified: ' + result['firmware'] + '. Backup: ' + result['backup'])
            self.bar['value'] = 100
            updated = core.Device(result['address'], device.hostname, device.board, result['firmware'])
            self.devices[int(selected[0])] = updated
            self.tree.item(selected[0], values=(updated.hostname, updated.board.upper(), updated.firmware, updated.address))
            extra='\n'+result['wifiWarning'] if result.get('wifiWarning') else ''
            messagebox.showinfo('Your dragon is updated', 'Startup was validated and saved settings match the backup. Reopen the lamp webpage and check normal lighting and touch controls.'+extra, parent=self.root)
        def job():
            try:
                result=core.update(device, release, password, progress, self.cancel,
                    reboot_timeout=300 if direct else 180,direct=direct,
                    reconnect=self.wifi_session.reconnect if direct and self.wifi_session and self.wifi_session.changed else None)
            except Exception as error:
                if self.wifi_session and self.wifi_session.changed:
                    try:self.wifi_session.restore()
                    except Exception:raise core.UpdateError(str(error)+' Rejoin your original Wi-Fi through the computer menu.') from error
                raise
            if self.wifi_session and self.wifi_session.changed:
                try:self.wifi_session.restore()
                except Exception:result['wifiWarning']='Firmware is verified, but the original Wi-Fi could not be restored. Rejoin it through the computer Wi-Fi menu.'
            return result
        self.run(job, done)

    def close(self):
        if self.busy:
            messagebox.showinfo('Please wait', 'Let the current check finish. Use Stop to finish safely. After finalization, the current restart check finishes before stopping.', parent=self.root); return
        if not self.wifi_session or not self.wifi_session.changed:
            self.root.destroy();return
        def job():
            try:self.wifi_session.restore();return True
            except Exception:return False
        def done(restored):
            if restored or messagebox.askyesno('Close updater?', 'The original Wi-Fi could not be restored. You can reconnect through the computer Wi-Fi menu. Close the app anyway?', parent=self.root):
                self.root.destroy()
        self.run(job,done)


if __name__ == '__main__':
    if '--release-test' in sys.argv:
        # Catch failures: a windowed PyInstaller exception dialog would hang CI.
        from pathlib import Path
        import traceback
        try:
            release = core.Release.latest()
            import tempfile
            with tempfile.TemporaryDirectory() as folder:
                core.prepare_offline(release, folder)
                downloader = core.download_json
                def blocked(*args, **kwargs): raise AssertionError('Offline mode attempted an internet download')
                core.download_json = blocked
                try:
                    saved = core.PreparedRelease.load(folder)
                    for board in ('s3', 'c3'):
                        for firmware in ('v0.3.0-beta.3', 'v0.3.0-beta.9'):
                            saved.package(core.Device('http://192.168.4.1', 'Dragon-Kingdom-000000', board, firmware))
                finally: core.download_json = downloader
                usb.prepare(release, cache=Path(folder) / 'usb')
                usb.prepare(release, cache=Path(folder) / 'usb')
            result = 'PASS: packaged HTTPS, signed main release ' + release.tag + ', persistent offline reload and all four packages without internet'
            code = 0
        except Exception:
            result, code = traceback.format_exc(), 1
        at = sys.argv.index('--release-test')
        if len(sys.argv) > at + 1: Path(sys.argv[at + 1]).write_text(result, encoding='utf-8')
        if sys.stdout: print(result)
        sys.exit(code)
    elif '--self-test' in sys.argv:
        from pathlib import Path
        import traceback
        try:
            core.trust_key()
            core.tls_context()
            import psutil, zeroconf
            wifi.native_self_test()
            root = tk.Tk(); root.withdraw(); app = App(root, online=False)
            assert app.password.get() == 'dragon123'
            assert root.title() == 'Dragon Kingdom Easy Update'
            assert app.is_direct() and str(app.address['state']) == 'disabled'
            app.mode.set('Home Wi-Fi'); app.change_mode()
            assert not app.is_direct() and str(app.check['state']) == 'normal'
            app.mode.set('USB cable'); app.change_mode()
            assert app.is_usb() and not app.usb_auto.get()
            assert str(app.password['state']) == 'disabled'
            usb.service() # Packaged shared recovery imports, no device I/O.
            root.update(); root.destroy()
            usb.ports() # Enumerate only; never opens a serial port.
            result, code = 'PASS: GUI modes, public key, TLS, USB service and port bindings', 0
        except Exception:
            result, code = traceback.format_exc(), 1
        at = sys.argv.index('--self-test')
        if len(sys.argv) > at + 1: Path(sys.argv[at + 1]).write_text(result, encoding='utf-8')
        if sys.stdout: print(result)
        sys.exit(code)
    else:
        root = tk.Tk(); App(root); root.mainloop()
