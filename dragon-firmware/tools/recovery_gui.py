"""Single-device recovery interface; no automatic flashing or compiler controls."""
import queue, threading, tkinter as tk
from tkinter import ttk
from recovery import recover, installed_esptool, prepared_release, esptool_path
from flash_support import ROOT, serial_modules, check_startup


def create_window(visible=True):
    window=tk.Tk();window.title('Dragon Kingdom - USB update and recovery');window.geometry('740x680')
    if not visible:window.withdraw()
    frame=ttk.Frame(window,padding=20);frame.pack(fill='both',expand=True)
    ttk.Label(frame,text='Update or recover a dragon',font=('',20,'bold')).pack(anchor='w')
    bundle=tk.StringVar(value='Checking firmware...');ttk.Label(frame,textvariable=bundle,wraplength=680).pack(anchor='w',pady=8)
    ttk.Label(frame,text='1. Disconnect product/external power. Never use both power inputs.\n2. Connect laptop USB to the internal ESP32 connector (one access screw).\n3. Select the current port. The tool reads the chip and chooses S3 or C3.',wraplength=680).pack(anchor='w',pady=8)
    ports=ttk.Combobox(frame,state='readonly');ports.pack(fill='x');safe=tk.BooleanVar(value=False)
    safety=ttk.Checkbutton(frame,text='External/main power is disconnected; internal laptop USB is the only power.',variable=safe);safety.pack(anchor='w',pady=12)
    status=tk.StringVar(value='Select a port. Each board needs its own USB-only confirmation.');ttk.Label(frame,textvariable=status,wraplength=680).pack(anchor='w')
    output=tk.Text(frame,height=13,wrap='word');output.pack(fill='both',expand=True,pady=12)
    events=queue.Queue();busy=False;tool=None;info=None
    cli=str(ROOT/'.tools/arduino-cli/arduino-cli.exe')
    def emit(text):events.put(('log',str(text)))
    def controls():
        update.configure(state='disabled' if busy or not info else 'normal')
        startup.configure(state='disabled' if busy or not info else 'normal')
        refresh_button.configure(state='disabled' if busy else 'normal')
        ports.configure(state='disabled' if busy else 'readonly');safety.configure(state='disabled' if busy else 'normal')
    def refresh():
        nonlocal info,tool
        if busy:return
        safe.set(False);info=None
        try:
            candidate=prepared_release();tool=installed_esptool() or esptool_path(cli)
            if not tool.is_file():raise RuntimeError('ESP32 tool not found.')
            _,listing=serial_modules();values=[p.device for p in listing.comports()];ports['values']=values
            if ports.get() not in values:ports.set('')
            info=candidate;bundle.set('Prepared firmware: '+info.get('firmware_tag','version not recorded')+' | S3 and C3 checksums/layouts verified.\nESP32 tool: '+str(tool))
            status.set('Select the current board port and confirm USB-only power.')
        except Exception as e:bundle.set('Recovery is not ready: '+str(e));status.set('Check the recovery bundle and installed Espressif tool. Nothing was written.')
        controls()
    def start(only_check=False):
        nonlocal busy
        if busy or not info:return
        if not safe.get() or not ports.get():status.set('Confirm USB-only power and select the current port first.');return
        busy=True;port=ports.get();status.set('Working. Keep USB connected until validation finishes.');output.delete('1.0','end');controls()
        def work():
            try:
                if only_check:check_startup(port,emit,timeout=75,expected_firmware=info.get('firmware_tag'),require_validation=True)
                else:recover(cli,port,True,emit,tool=tool)
                events.put(('done','Verified. Disconnect this board before connecting the next, then Refresh ports and confirm USB-only power again.'))
            except Exception as e:events.put(('done',str(e)))
        threading.Thread(target=work,daemon=True).start()
    row=ttk.Frame(frame);row.pack(fill='x')
    refresh_button=ttk.Button(row,text='Refresh ports',command=refresh);refresh_button.pack(side='left')
    update=ttk.Button(row,text='Update / recover firmware',command=start);update.pack(side='left',padx=10)
    startup=ttk.Button(row,text='Check startup only',command=lambda:start(True));startup.pack(side='left')
    def poll():
        nonlocal busy
        try:
            while True:
                kind,text=events.get_nowait()
                if kind=='done':busy=False;safe.set(False);status.set(text);controls()
                else:output.insert('end',text+'\n');output.see('end')
        except queue.Empty:pass
        window.after(100,poll)
    window.protocol('WM_DELETE_WINDOW',lambda:status.set('Wait for recovery to finish.') if busy else window.destroy())
    refresh();poll();return window


def main():create_window().mainloop()
if __name__=='__main__':main()
