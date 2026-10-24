"""Single-device recovery interface; no automatic flashing or compiler controls."""
import queue, threading, tkinter as tk
from tkinter import ttk
from recovery import recover
from flash_support import ROOT, serial_modules

def main():
    window=tk.Tk();window.title('Dragon Kingdom USB recovery');window.geometry('680x550')
    frame=ttk.Frame(window,padding=20);frame.pack(fill='both',expand=True)
    ttk.Label(frame,text='Recover one dragon',font=('',20,'bold')).pack(anchor='w')
    ttk.Label(frame,text='1. Unplug the bottom product power cable.\n2. Remove one access screw. Connect laptop USB to the internal ESP32.\n3. Select its port. Recovery checks the chip and preserves saved data.',wraplength=620).pack(anchor='w',pady=15)
    ports=ttk.Combobox(frame,state='readonly');ports.pack(fill='x');safe=tk.BooleanVar(value=False)
    ttk.Checkbutton(frame,text='External/main power is disconnected; internal laptop USB is the only power.',variable=safe).pack(anchor='w',pady=12)
    status=tk.StringVar(value='Select a port. Never connect both power inputs.');ttk.Label(frame,textvariable=status,wraplength=620).pack(anchor='w')
    output=tk.Text(frame,height=10,wrap='word');output.pack(fill='both',expand=True,pady=12)
    events=queue.Queue();busy=False
    def emit(text):events.put(('log',str(text)))
    def refresh():
        try:_,listing=serial_modules();ports['values']=[p.device for p in listing.comports()]
        except Exception as e:status.set(str(e))
    def start(action):
        nonlocal busy
        if busy:return
        if not safe.get() or not ports.get():status.set('Confirm USB-only power and select the current port first.');return
        busy=True;port=ports.get();status.set('Working. Keep USB connected.');output.delete('1.0','end')
        def work():
            try:
                recover(str(ROOT/'.tools/arduino-cli/arduino-cli.exe'),port,True,emit)
                events.put(('done','Finished.'))
            except Exception as e:events.put(('done',str(e)))
        threading.Thread(target=work,daemon=True).start()
    row=ttk.Frame(frame);row.pack(fill='x');ttk.Button(row,text='Refresh ports',command=refresh).pack(side='left');ttk.Button(row,text='Recover firmware',command=lambda:start('recover')).pack(side='left',padx=10)
    def poll():
        nonlocal busy
        try:
            while True:
                kind,text=events.get_nowait()
                if kind=='done':busy=False;status.set(text)
                else:output.insert('end',text+'\n');output.see('end')
        except queue.Empty:pass
        window.after(100,poll)
    window.protocol('WM_DELETE_WINDOW',lambda:status.set('Wait for recovery to finish.') if busy else window.destroy());refresh();poll();window.mainloop()
if __name__=='__main__':main()
