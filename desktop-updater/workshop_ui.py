"""Dragon Kingdom keeper-workshop interface, drawn with native Tk widgets."""
import tkinter as tk
from tkinter import ttk
import webbrowser
import updater_core as core

PAPER = '#f3eee2'
CARD = '#fffcf5'
FOREST = '#163e36'
TEAL = '#286b5b'
GOLD = '#d4ad62'
INK = '#213d35'
MUTED = '#586b5e'
LINE = '#dedbcb'


def crest(canvas, x, y):
    """An original eight-by-eight LED dragon crest; no external artwork."""
    pattern = ('00100100', '00111100', '01111110', '11101111',
               '11111110', '01111100', '00111010', '00011000')
    for row, pixels in enumerate(pattern):
        for column, pixel in enumerate(pixels):
            canvas.create_rectangle(x+column*9, y+row*9, x+column*9+6, y+row*9+6,
                                    fill=GOLD if pixel == '1' else '#224b40', outline='')


def build(app, root):
    root.title('Dragon Kingdom Easy Update')
    root.geometry('1040x870'); root.minsize(940, 850)
    root.configure(background=PAPER)
    style = ttk.Style(root); style.theme_use('clam')
    style.configure('.', font=('Segoe UI', 10), background=PAPER, foreground=INK)
    style.configure('TFrame', background=PAPER)
    style.configure('Card.TFrame', background=CARD)
    style.configure('TLabel', background=PAPER, foreground=INK)
    style.configure('Muted.TLabel', foreground=MUTED)
    style.configure('Section.TLabel', font=('Segoe UI', 11, 'bold'), foreground=FOREST)
    style.configure('TButton', padding=(12, 7), background=CARD, bordercolor=LINE, foreground=FOREST)
    style.map('TButton', background=[('active', '#e7ecdd')], foreground=[('disabled', '#9dada2')])
    style.configure('Primary.TButton', background=TEAL, foreground='white', font=('Segoe UI', 10, 'bold'))
    style.map('Primary.TButton', background=[('disabled', '#aabbb0'), ('active', FOREST)], foreground=[('disabled', '#edf2e9')])
    style.configure('TCheckbutton', background=PAPER, foreground=INK, padding=4)
    style.map('TCheckbutton', background=[('active', PAPER)])
    style.configure('TRadiobutton', background=PAPER, foreground=INK, padding=4)
    style.map('TRadiobutton', background=[('active', PAPER)])
    style.configure('Treeview', background=CARD, fieldbackground=CARD, rowheight=31, bordercolor=LINE, font=('Segoe UI', 10))
    style.configure('Treeview.Heading', background='#e4e9dd', foreground=FOREST, font=('Segoe UI', 9, 'bold'), padding=7)
    style.map('Treeview', background=[('selected', TEAL)], foreground=[('selected', 'white')])
    style.configure('Horizontal.TProgressbar', background=TEAL, troughcolor='#dfdfcf', bordercolor=LINE)
    header = tk.Canvas(root, height=128, background=FOREST, highlightthickness=0)
    header.pack(fill='x')
    crest(header, 28, 29)
    header.create_text(122, 27, text="THE KEEPER'S WORKSHOP", anchor='nw', fill=GOLD, font=('Segoe UI', 9, 'bold'))
    header.create_text(120, 47, text='Dragon Kingdom', anchor='nw', fill='#fff9e9', font=('Georgia', 27, 'bold'))
    header.create_text(122, 92, text='Easy Update  /  Keep the whole roost glowing', anchor='nw', fill='#c5d8c6', font=('Segoe UI', 10))
    panel = ttk.Frame(root, padding=(26, 18, 26, 12)); panel.pack(fill='both', expand=True)
    ttk.Label(panel, text='01   CHOOSE YOUR CONNECTION', style='Section.TLabel').pack(anchor='w', pady=(0, 9))
    app.mode = tk.StringVar(value='Dragon setup Wi-Fi (offline)')
    # Kept as a state holder for the existing controller; the visible controls are cards.
    app.mode_picker = ttk.Combobox(panel, textvariable=app.mode, state='readonly', values=('Dragon setup Wi-Fi (offline)', 'Home Wi-Fi', 'USB cable'))
    cards = ttk.Frame(panel); cards.pack(fill='x')
    app.mode_buttons = []
    def choose(value): app.mode.set(value); app.change_mode()
    for index, (value, title, subtitle) in enumerate([
        ('Dragon setup Wi-Fi (offline)', 'Dragon Wi-Fi', 'Find and update nearby dragons'),
        ('Home Wi-Fi', 'Home Wi-Fi', 'Dragons already on your network'),
        ('USB cable', 'USB cable', 'Auto update, empty or reused boards')]):
        button = tk.Button(cards, text=title+'\n'+subtitle, command=lambda v=value: choose(v),
                           font=('Segoe UI', 10), relief='flat', bd=0, padx=12, pady=12,
                           background=CARD, foreground=FOREST, cursor='hand2', activebackground='#e3e9d9')
        button.grid(row=0, column=index, sticky='nsew', padx=(0 if index==0 else 6, 0))
        cards.columnconfigure(index, weight=1, uniform='mode')
        app.mode_buttons.append((value, button))
    app.instructions = tk.StringVar()
    ttk.Label(panel, textvariable=app.instructions, wraplength=970, style='Muted.TLabel').pack(anchor='w', pady=(10, 12))
    app.usb_group = ttk.Frame(panel)
    app.usb_notice = ttk.Label(app.usb_group,
        text='Please connect USB only to the ESP32. Disconnect the bottom/external power first; never use both power inputs.',
        wraplength=970, style='Muted.TLabel')
    app.usb_notice.pack(anchor='w', pady=(5,6))
    app.usb_auto_button = ttk.Checkbutton(app.usb_group, text='Auto update USB dragons as they are connected - one at a time', variable=app.usb_auto, command=app.toggle_usb_auto)
    app.usb_auto_button.pack(anchor='w', pady=(0, 7))
    app.devices_frame = ttk.Frame(panel); app.devices_frame.pack(fill='both', expand=True)
    heading = ttk.Frame(app.devices_frame); heading.pack(fill='x', pady=(0, 8))
    ttk.Label(heading, text='02   YOUR DRAGONS', style='Section.TLabel').pack(side='left')
    app.prepare = ttk.Button(heading, text='Choose firmware file…', command=app.choose_firmware); app.prepare.pack(side='right')
    toolbar = ttk.Frame(app.devices_frame); toolbar.pack(fill='x', pady=(0, 9))
    app.find = ttk.Button(toolbar, style='Primary.TButton', text='Find dragons', command=app.find_devices); app.find.pack(side='left')
    app.address = ttk.Entry(toolbar, width=19); app.address.pack(side='left', padx=(10, 5))
    app.add = ttk.Button(toolbar, text='Add address', command=app.add_address); app.add.pack(side='left')
    app.check = ttk.Button(toolbar, text='Check for updates', command=app.check_release); app.check.pack(side='right')
    table = ttk.Frame(app.devices_frame); table.pack(fill='both', expand=True)
    app.tree = ttk.Treeview(table, columns=('name', 'board', 'firmware', 'address', 'result'), show='headings', height=4, selectmode='browse')
    for name, label, width in [('name','Dragon',215),('board','Board',65),('firmware','Firmware',155),('address','Connection',155),('result','Result',160)]:
        app.tree.heading(name,text=label);app.tree.column(name,width=width,minwidth=55)
    app.tree.pack(side='left',fill='both',expand=True)
    scroll=ttk.Scrollbar(table,command=app.tree.yview);scroll.pack(side='right',fill='y');app.tree.configure(yscrollcommand=scroll.set)
    app.offered=tk.StringVar(value='Checking signed stable firmware...')
    ttk.Label(panel,textvariable=app.offered,style='Muted.TLabel',wraplength=970).pack(anchor='w',pady=(8,4))
    app.auth=ttk.Frame(panel);app.auth.pack(fill='x',pady=(2,8))
    ttk.Label(app.auth,text='Parent password',style='Muted.TLabel').pack(side='left')
    app.password=ttk.Entry(app.auth,show='*',width=19);app.password.pack(side='left',padx=10);app.password.insert(0,'dragon123')
    ttk.Label(app.auth,text='Already filled in. Edit only if needed.',style='Muted.TLabel').pack(side='left')
    actions=ttk.Frame(panel);actions.pack(fill='x',pady=(0,10));app.actions=actions
    app.install=ttk.Button(actions,text='Update selected dragon',style='Primary.TButton',command=app.install_selected);app.install.pack(side='left')
    app.stop=ttk.Button(actions,text='Stop',command=app.request_stop,state='disabled');app.stop.pack(side='left',padx=8)
    ttk.Button(actions,text='Setup & help',command=lambda:webbrowser.open(core.GUIDE)).pack(side='right')
    app.bar=ttk.Progressbar(panel,maximum=100);app.bar.pack(fill='x',pady=(0,8))
    app.status=tk.StringVar(value='Welcome. Your dragons are in good hands.')
    short=tk.StringVar(value=app.status.get())
    ttk.Label(panel,textvariable=short,wraplength=970,style='Section.TLabel').pack(anchor='w',pady=(0,6))
    app.activity=tk.Text(panel,height=3,wrap='word',background=CARD,foreground=MUTED,relief='flat',font=('Consolas',9),padx=10,pady=8,state='disabled')
    app.activity.pack(fill='x')
    def status_changed(*args):
        value=app.status.get();short.set(value if len(value)<145 else value[:142]+'...')
        app.activity.configure(state='normal');app.activity.insert('end',value+'\n');app.activity.see('end');app.activity.configure(state='disabled')
    app.status.trace_add('write',status_changed)
    ttk.Label(panel,text='Signed stable firmware  ·  Backups stay on this computer  ·  '+core.APP_VERSION,style='Muted.TLabel').pack(anchor='w',pady=(9,0))
