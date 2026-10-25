"""Desktop entry point. Firmware installation always requires a selected lamp and click."""
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import updater_core as core


class App:
    def __init__(self, root, online=True):
        self.root, self.events = root, queue.Queue()
        self.devices, self.release = [], None
        self.busy, self.installing, self.finalizing = False, False, False
        self.cancel = threading.Event()
        root.title('Dragon Kingdom Updater')
        root.geometry('860x660')
        root.minsize(730, 610)
        panel = ttk.Frame(root, padding=22)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='Keep your dragon up to date', font=('TkDefaultFont', 21, 'bold')).pack(anchor='w')
        ttk.Label(panel, text='Keep the lamp on its normal supply. Join the same home network on this computer.\nNo USB connection to the lamp is needed.', wraplength=790).pack(anchor='w', pady=(9, 15))
        toolbar = ttk.Frame(panel); toolbar.pack(fill='x')
        self.find = ttk.Button(toolbar, text='Find dragons', command=self.find_devices); self.find.pack(side='left')
        self.address = ttk.Entry(toolbar, width=24); self.address.pack(side='left', padx=(15, 6))
        self.add = ttk.Button(toolbar, text='Add address', command=self.add_address); self.add.pack(side='left')
        self.check = ttk.Button(toolbar, text='Check for updates', command=self.check_release); self.check.pack(side='right')
        self.tree = ttk.Treeview(panel, columns=('name', 'board', 'firmware', 'address'), show='headings', height=6, selectmode='browse')
        for name, label, width in [('name', 'Dragon', 235), ('board', 'Board', 55), ('firmware', 'Installed firmware', 150), ('address', 'Address', 170)]:
            self.tree.heading(name, text=label); self.tree.column(name, width=width)
        self.tree.pack(fill='both', expand=True, pady=16)
        self.offered = tk.StringVar(value='Checking the main firmware release...')
        ttk.Label(panel, textvariable=self.offered, wraplength=790).pack(anchor='w')
        auth = ttk.Frame(panel); auth.pack(fill='x', pady=12)
        ttk.Label(auth, text='Parent password (normally dragon123)').pack(side='left')
        self.password = ttk.Entry(auth, show='*', width=20); self.password.pack(side='left', padx=10)
        actions = ttk.Frame(panel); actions.pack(fill='x')
        self.install = ttk.Button(actions, text='Update selected dragon', command=self.install_selected); self.install.pack(side='left')
        self.stop = ttk.Button(actions, text='Cancel', command=self.cancel.set, state='disabled'); self.stop.pack(side='left', padx=10)
        ttk.Button(actions, text='Setup and update guide', command=lambda: webbrowser.open(core.GUIDE)).pack(side='right')
        self.bar = ttk.Progressbar(panel, maximum=100); self.bar.pack(fill='x', pady=(16, 7))
        self.status = tk.StringVar(value='Ready. Choose Find dragons.')
        ttk.Label(panel, textvariable=self.status, wraplength=790).pack(anchor='w')
        ttk.Label(panel, text='Backups stay on this computer: ' + str(core.backup_folder()), wraplength=790).pack(anchor='w', pady=(12, 0))
        ttk.Label(panel, text='Updater ' + core.APP_VERSION + ' · Signed firmware · No automatic installation').pack(anchor='w', pady=(8, 0))
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.drain)
        if online: self.check_release()

    def controls(self, busy):
        self.busy = busy
        for widget in (self.find, self.add, self.check, self.install, self.address, self.password):
            widget.configure(state='disabled' if busy else 'normal')
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
        self.status.set('Finding dragons on this computer\'s local network...')
        self.run(lambda: core.discover(self.cancel), self.show_devices)

    def add_address(self):
        address = self.address.get().strip()
        self.run(lambda: core.Device.probe(address, timeout=4), lambda d: self.show_devices([x for x in self.devices if x.hostname != d.hostname] + [d]))

    def check_release(self):
        def done(release):
            self.release = release
            self.offered.set('Main firmware available: ' + release.tag)
            self.status.set('Choose Find dragons, or add the address from its webpage.')
        self.run(core.Release.latest, done)

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
        if not messagebox.askokcancel('Install firmware?', f'{device.hostname} ({device.board.upper()})\n{device.firmware} → {release.tag}\n\nA backup will be saved before installation. Keep power and Wi-Fi connected until the restart check finishes.', parent=self.root): return
        self.installing = True
        def progress(text, percent): self.events.put(('progress', text, percent))
        def done(result):
            self.password.delete(0, 'end')
            self.status.set('Update verified: ' + result['firmware'] + '. Backup: ' + result['backup'])
            self.bar['value'] = 100
            updated = core.Device(result['address'], device.hostname, device.board, result['firmware'])
            self.devices[int(selected[0])] = updated
            self.tree.item(selected[0], values=(updated.hostname, updated.board.upper(), updated.firmware, updated.address))
            messagebox.showinfo('Your dragon is updated', 'Startup was validated and saved settings match the backup. Reopen the lamp webpage and check normal lighting and touch controls.', parent=self.root)
        self.run(lambda: core.update(device, release, password, progress, self.cancel), done)

    def close(self):
        if self.busy:
            messagebox.showinfo('Please wait', 'Let the current check finish. During upload, use Cancel and wait; after final verification, keep the app open until the restart check finishes.', parent=self.root); return
        self.root.destroy()


if __name__ == '__main__':
    if '--release-test' in sys.argv:
        release = core.Release.latest()
        if sys.stdout: print('PASS: packaged HTTPS and signed main release ' + release.tag)
    elif '--self-test' in sys.argv:
        core.trust_key()
        core.tls_context()
        import psutil, zeroconf
        root = tk.Tk(); root.withdraw(); App(root, online=False); root.update(); root.destroy()
        if sys.stdout: print('PASS: updater public trust root, network dependencies and Tk interface')
    else:
        root = tk.Tk(); App(root); root.mainloop()
