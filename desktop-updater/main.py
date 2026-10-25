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


class App:
    def __init__(self, root, online=True):
        self.root, self.events = root, queue.Queue()
        self.devices, self.release, self.live_release, self.prepared = [], None, None, None
        self.busy, self.installing, self.finalizing = False, False, False
        self.cancel = threading.Event()
        self.wifi_session = None
        root.title('Dragon Kingdom Easy Update')
        root.geometry('860x790')
        root.minsize(800, 750)
        panel = ttk.Frame(root, padding=22)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='Dragon Kingdom Easy Update', font=('TkDefaultFont', 21, 'bold')).pack(anchor='w')
        ttk.Label(panel, text='Keep the lamp on its normal bottom USB-C supply. No laptop USB connection is needed.', wraplength=750).pack(anchor='w', pady=(9, 10))
        modes = ttk.Frame(panel); modes.pack(fill='x')
        ttk.Label(modes, text='Connection:').pack(side='left')
        self.mode = tk.StringVar(value='Dragon setup Wi-Fi (offline)')
        self.mode_picker = ttk.Combobox(modes, textvariable=self.mode, state='readonly', width=31,
            values=('Dragon setup Wi-Fi (offline)', 'Home Wi-Fi'))
        self.mode_picker.pack(side='left', padx=10)
        self.mode_picker.bind('<<ComboboxSelected>>', lambda event: self.change_mode())
        self.prepare = ttk.Button(modes, text='Download for offline use', command=self.prepare_offline)
        self.prepare.pack(side='right')
        self.instructions = tk.StringVar()
        ttk.Label(panel, textvariable=self.instructions, wraplength=750).pack(anchor='w', pady=(10, 12))
        toolbar = ttk.Frame(panel); toolbar.pack(fill='x')
        self.find = ttk.Button(toolbar, text='Find dragons', command=self.find_devices); self.find.pack(side='left')
        self.address = ttk.Entry(toolbar, width=24); self.address.pack(side='left', padx=(15, 6))
        self.add = ttk.Button(toolbar, text='Add address', command=self.add_address); self.add.pack(side='left')
        self.check = ttk.Button(toolbar, text='Check for updates', command=self.check_release); self.check.pack(side='right')
        self.tree = ttk.Treeview(panel, columns=('name', 'board', 'firmware', 'address', 'result'), show='headings', height=6, selectmode='browse')
        for name, label, width in [('name', 'Dragon', 190), ('board', 'Board', 50), ('firmware', 'Installed firmware', 135), ('address', 'Address', 130), ('result', 'Result', 180)]:
            self.tree.heading(name, text=label); self.tree.column(name, width=width)
        self.tree.pack(fill='both', expand=True, pady=16)
        self.offered = tk.StringVar(value='Choose Check for updates while connected to internet.')
        ttk.Label(panel, textvariable=self.offered, wraplength=790).pack(anchor='w')
        auth = ttk.Frame(panel); auth.pack(fill='x', pady=12)
        ttk.Label(auth, text='Parent password (filled in; edit only if needed)').pack(side='left')
        self.password = ttk.Entry(auth, show='*', width=20); self.password.pack(side='left', padx=10)
        self.password.insert(0, 'dragon123')
        actions = ttk.Frame(panel); actions.pack(fill='x')
        self.install = ttk.Button(actions, text='Update selected dragon', command=self.install_selected); self.install.pack(side='left')
        self.stop = ttk.Button(actions, text='Stop', command=self.cancel.set, state='disabled'); self.stop.pack(side='left', padx=10)
        ttk.Button(actions, text='Setup and update guide', command=lambda: webbrowser.open(core.GUIDE)).pack(side='right')
        self.bar = ttk.Progressbar(panel, maximum=100); self.bar.pack(fill='x', pady=(16, 7))
        self.status = tk.StringVar(value='Ready. Choose Find dragons.')
        ttk.Label(panel, textvariable=self.status, wraplength=790).pack(anchor='w')
        ttk.Label(panel, text='Backups stay on this computer: ' + str(core.backup_folder()), wraplength=790).pack(anchor='w', pady=(12, 0))
        ttk.Label(panel, text='Easy Update ' + core.APP_VERSION + ' · Signed firmware · Startup downloads only').pack(anchor='w', pady=(8, 0))
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.drain)
        self.change_mode()
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

    def change_mode(self):
        if not self.is_direct() and self.wifi_session and self.wifi_session.changed:
            self.restore_wifi(after=self.change_mode); return
        self.release = self.prepared if self.is_direct() else self.live_release
        self.show_devices([])
        if self.is_direct():
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
        self.controls(False)

    def controls(self, busy):
        self.busy = busy
        for widget in (self.find, self.add, self.check, self.install, self.address, self.password, self.prepare):
            widget.configure(state='disabled' if busy else 'normal')
        self.mode_picker.configure(state='disabled' if busy else 'readonly')
        if self.is_direct():
            self.address.configure(state='disabled')
        self.stop.configure(text='Stop after this dragon' if self.finalizing else 'Stop', state='normal' if busy and self.installing else 'disabled')

    def run(self, job, done):
        if self.busy: return
        self.cancel.clear(); self.finalizing = False; self.bar['value'] = 0
        self.controls(True)
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
                elif event[0] == 'batch_result':
                    self.show_batch_result(event[1])
                elif event[0] == 'done':
                    self.installing = False; self.controls(False); event[1](event[2])
                else:
                    self.installing = False; self.controls(False); self.status.set(event[1])
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
        if self.is_direct():
            self.restore_wifi(); return
        def done(release):
            self.release = self.live_release = release
            self.offered.set('Main firmware available: ' + release.tag)
            self.status.set('Choose Find dragons, or add the address from its webpage.')
        self.run(core.Release.latest, done)

    def prepare_offline(self):
        def progress(text, percent): self.events.put(('progress', text, percent))
        def done(release):
            self.prepared = release
            if self.is_direct(): self.release = release
            self.offered.set('Offline firmware ready: ' + release.tag + ' (both board types)')
            self.status.set('Download verified and saved. Choose Dragon setup Wi-Fi (offline), then Find & update all dragons. You can close and reopen this app offline.')
        self.run(lambda: core.prepare_offline(progress=progress), done)

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
            result = 'PASS: packaged HTTPS, signed main release ' + release.tag + ', persistent offline reload and all four packages without internet'
            code = 0
        except Exception:
            result, code = traceback.format_exc(), 1
        at = sys.argv.index('--release-test')
        if len(sys.argv) > at + 1: Path(sys.argv[at + 1]).write_text(result, encoding='utf-8')
        if sys.stdout: print(result)
        sys.exit(code)
    elif '--self-test' in sys.argv:
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
        root.update(); root.destroy()
        if sys.stdout: print('PASS: updater public trust root, network dependencies and Tk interface')
    else:
        root = tk.Tk(); App(root); root.mainloop()
