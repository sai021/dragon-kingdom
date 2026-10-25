"""Desktop entry point. Firmware installation always requires a selected lamp and click."""
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import updater_core as core
import wifi_control as wifi


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
        self.tree = ttk.Treeview(panel, columns=('name', 'board', 'firmware', 'address'), show='headings', height=6, selectmode='browse')
        for name, label, width in [('name', 'Dragon', 235), ('board', 'Board', 55), ('firmware', 'Installed firmware', 150), ('address', 'Address', 170)]:
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
        self.stop = ttk.Button(actions, text='Cancel', command=self.cancel.set, state='disabled'); self.stop.pack(side='left', padx=10)
        ttk.Button(actions, text='Setup and update guide', command=lambda: webbrowser.open(core.GUIDE)).pack(side='right')
        self.bar = ttk.Progressbar(panel, maximum=100); self.bar.pack(fill='x', pady=(16, 7))
        self.status = tk.StringVar(value='Ready. Choose Find dragons.')
        ttk.Label(panel, textvariable=self.status, wraplength=790).pack(anchor='w')
        ttk.Label(panel, text='Backups stay on this computer: ' + str(core.backup_folder()), wraplength=790).pack(anchor='w', pady=(12, 0))
        ttk.Label(panel, text='Easy Update ' + core.APP_VERSION + ' · Signed firmware · No automatic installation').pack(anchor='w', pady=(8, 0))
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.drain)
        if online:
            try: self.prepared = core.PreparedRelease.load()
            except core.UpdateError: pass
        self.change_mode()

    def is_direct(self):
        return self.mode.get() == 'Dragon setup Wi-Fi (offline)'

    def change_mode(self):
        if not self.is_direct() and self.wifi_session and self.wifi_session.changed:
            self.restore_wifi(after=self.change_mode); return
        self.release = self.prepared if self.is_direct() else self.live_release
        self.show_devices([])
        if self.is_direct():
            self.find.configure(text='Find dragon Wi-Fi')
            self.add.configure(text='Manual connection')
            self.check.configure(text='Return to original Wi-Fi')
            self.instructions.set('Choose Find dragon Wi-Fi, select a Dragon-Kingdom network and Connect. The app downloads files first if needed, then switches Wi-Fi for you. Allow OS Wi-Fi/location permission if asked.\nDirect mode is for lamps NOT connected to home Wi-Fi. Their AP otherwise closes after 15 seconds; use Home Wi-Fi mode for those lamps.')
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
        self.stop.configure(state='normal' if busy and self.installing and not self.finalizing else 'disabled')

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
                    if event[2] >= 88:
                        self.finalizing = True; self.stop.configure(state='disabled')
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
            def job():
                prepared = self.prepared or core.prepare_offline(progress=lambda text, percent: self.events.put(('progress', text, percent)))
                return prepared, self.wifi_session.adapter.scan()
            def done(result):
                self.prepared, networks = result; self.release = self.prepared
                self.offered.set('Prepared offline firmware: ' + self.prepared.tag)
                if not networks:
                    self.status.set('No dragon APs found. A lamp already on home Wi-Fi closes its AP 15 seconds after joining; use Home Wi-Fi mode. For an unconfigured lamp, power-cycle before an update and scan again.'); return
                self.choose_wifi(networks)
            self.status.set('Preparing signed files and scanning nearby dragon Wi-Fi. Your connection has not been changed.')
            self.run(job,done)
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
            self.status.set('Download verified and saved. Choose Dragon setup Wi-Fi (offline), then Find dragon Wi-Fi to connect automatically. You can close and reopen this app offline.')
        self.run(lambda: core.prepare_offline(progress=progress), done)

    def choose_wifi(self,networks):
        dialog=tk.Toplevel(self.root);dialog.title('Choose a dragon Wi-Fi network');dialog.transient(self.root)
        ttk.Label(dialog,text='Select your dragon. Connecting temporarily switches this computer\'s Wi-Fi.\nFirmware is installed only after you review it in the main window.',padding=14).pack()
        choices=tk.Listbox(dialog,width=55,height=min(8,len(networks)),exportselection=False)
        choices.pack(padx=14,pady=5)
        for network in networks:choices.insert('end',f'{network.ssid}    Signal {network.signal}%')
        choices.selection_set(0)
        def join():
            selected=choices.curselection()
            if not selected:return
            network=networks[selected[0]];dialog.destroy()
            def job():
                import time
                try:
                    self.wifi_session.join(network)
                    deadline=time.monotonic()+25
                    while True:
                        try:device=core.Device.probe('192.168.4.1',timeout=3)
                        except core.UpdateError:
                            if time.monotonic()>=deadline:raise
                            time.sleep(1);continue
                        if device.hostname.casefold()!=network.ssid.casefold():
                            raise core.UpdateError('The lamp identity does not match the selected Wi-Fi network. No firmware was installed.')
                        return [device]
                except Exception as error:
                    try:self.wifi_session.restore()
                    except Exception:raise core.UpdateError(str(error)+' Rejoin your original Wi-Fi through the computer menu.') from error
                    raise
            self.status.set('Connecting to '+network.ssid+' and checking the lamp...')
            self.run(job,self.show_devices)
        ttk.Button(dialog,text='Connect to selected dragon',command=join).pack(pady=12)
        dialog.grab_set()

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
        if not selected or not self.release:
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
            messagebox.showinfo('Please wait', 'Let the current check finish. During upload, use Cancel and wait; after final verification, keep the app open until the restart check finishes.', parent=self.root); return
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
