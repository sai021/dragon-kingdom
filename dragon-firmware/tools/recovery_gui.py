"""USB recovery and opt-in automatic S3/C3 batches; no compiler controls."""
import queue, threading, tkinter as tk
from tkinter import ttk
from recovery import recover, installed_esptool, prepared_release, esptool_path, update_if_newer
from recovery_batch import BatchGate
from flash_support import ROOT, serial_modules, check_startup


def create_window(visible=True):
    window=tk.Tk();window.title('Dragon Kingdom - USB update and recovery');window.geometry('780x740')
    if not visible:window.withdraw()
    timers={'poll':None,'auto':None}
    def cleanup(event):
        if event.widget is window:
            for task in timers.values():
                if task:window.after_cancel(task)
    window.bind('<Destroy>',cleanup,add='+')
    frame=ttk.Frame(window,padding=20);frame.pack(fill='both',expand=True)
    ttk.Label(frame,text='Update or recover a dragon',font=('',20,'bold')).pack(anchor='w')
    bundle=tk.StringVar(value='Checking firmware...');ttk.Label(frame,textvariable=bundle,wraplength=680).pack(anchor='w',pady=8)
    ttk.Label(frame,text='1. Disconnect product/external power. Never use both power inputs.\n2. Connect laptop USB to the internal ESP32 connector (one access screw).\n3. Select the current port. The tool reads the chip and chooses S3 or C3.',wraplength=680).pack(anchor='w',pady=8)
    ports=ttk.Combobox(frame,state='readonly');ports.pack(fill='x');safe=tk.BooleanVar(value=False)
    safety=ttk.Checkbutton(frame,text='External/main power is disconnected; internal laptop USB is the only power.',variable=safe);safety.pack(anchor='w',pady=12)
    status=tk.StringVar(value='Select a port. Each board needs its own USB-only confirmation.');ttk.Label(frame,textvariable=status,wraplength=680).pack(anchor='w')
    output=tk.Text(frame,height=13,wrap='word');output.pack(fill='both',expand=True,pady=12)
    auto=tk.BooleanVar(value=False);batch=BatchGate();passes=0
    auto_status=tk.StringVar(value='Auto off. Confirm USB-only power, then enable Auto for a batch.')
    events=queue.Queue();busy=False;tool=None;info=None
    cli=str(ROOT/'.tools/arduino-cli/arduino-cli.exe')
    def emit(text):events.put(('log',str(text)))
    def controls():
        update.configure(state='disabled' if busy or batch.enabled or not info else 'normal')
        startup.configure(state='disabled' if busy or batch.enabled or not info else 'normal')
        refresh_button.configure(state='disabled' if busy or batch.enabled else 'normal')
        ports.configure(state='disabled' if busy or batch.enabled else 'readonly');safety.configure(state='disabled' if busy or batch.enabled else 'normal')
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
    def stop_auto(message):
        auto.set(False);batch.stop();auto_status.set('Auto off. '+message)
    def toggle_auto():
        if not auto.get():stop_auto('Any current board will finish normally.');controls();return
        if busy or not info or not safe.get():stop_auto('Confirm USB-only power for every board in this batch first.');controls();return
        batch.arm();auto_status.set('Auto on: one ESP32 at a time. Older/legacy firmware updates automatically; same/newer firmware is checked without rewriting.');controls()
    def start(only_check=False,automatic=False):
        nonlocal busy
        if busy or not info:return
        if not safe.get() or not ports.get():status.set('Confirm USB-only power and select the current port first.');return
        busy=True;port=ports.get();status.set('Working. Keep USB connected until validation finishes.');output.delete('1.0','end');controls()
        def work():
            try:
                if only_check:check_startup(port,emit,timeout=75,expected_firmware=info.get('firmware_tag'),require_validation=True)
                elif automatic:emit(update_if_newer(cli,port,True,emit,tool=tool))
                else:recover(cli,port,True,emit,tool=tool)
                events.put(('done','STARTUP PASS - firmware, storage, uptime and USB ceiling verified.'))
            except Exception as e:events.put(('error',str(e)))
        threading.Thread(target=work,daemon=True).start()
    row=ttk.Frame(frame);row.pack(fill='x')
    refresh_button=ttk.Button(row,text='Refresh ports',command=refresh);refresh_button.pack(side='left')
    update=ttk.Button(row,text='Update / recover firmware',command=start);update.pack(side='left',padx=10)
    startup=ttk.Button(row,text='Check startup only',command=lambda:start(True));startup.pack(side='left')
    auto_button=ttk.Checkbutton(frame,text='Auto mode - update boards when connected (USB-only batch)',variable=auto,command=toggle_auto);auto_button.pack(anchor='w',pady=(10,4))
    ttk.Label(frame,textvariable=auto_status,wraplength=720).pack(anchor='w')
    ttk.Label(frame,text='STARTUP PASS checks firmware/storage/power reporting, not physical LEDs, sensors or Wi-Fi range.',wraplength=720).pack(anchor='w',pady=6)
    def auto_tick():
        if batch.enabled and not busy:
            try:
                _,listing=serial_modules();current={p.device for p in listing.comports() if p.vid==0x303a}
                waiting=batch.waiting;chosen=batch.choose(current)
                if chosen:
                    ports['values']=sorted(current);ports.set(chosen);auto_status.set('Processing '+chosen+'. Keep USB connected until STARTUP PASS.');start(automatic=True)
                elif waiting and not batch.waiting:auto_status.set('Auto ready - connect the next ESP32. Startup passes: '+str(passes))
            except Exception as e:stop_auto(str(e));safe.set(False);controls()
        timers['auto']=window.after(1000,auto_tick)
    def poll():
        nonlocal busy,passes
        try:
            while True:
                kind,text=events.get_nowait()
                if kind=='done':
                    busy=False;passes+=1;status.set(text+' Passes: '+str(passes));batch.finished()
                    if batch.enabled:auto_status.set('STARTUP PASS - unplug this board, then wait for Auto ready before connecting the next.')
                    else:safe.set(False)
                    controls()
                elif kind=='error':busy=False;stop_auto('Operation failed. Resolve the error before continuing.');safe.set(False);status.set(text);controls()
                else:output.insert('end',text+'\n');output.see('end')
        except queue.Empty:pass
        timers['poll']=window.after(100,poll)
    window.protocol('WM_DELETE_WINDOW',lambda:status.set('Wait for recovery to finish.') if busy else window.destroy())
    refresh();poll();timers['auto']=window.after(1000,auto_tick);return window


def main():create_window().mainloop()
if __name__=='__main__':main()
