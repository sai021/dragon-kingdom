"""Small offline Tk editor for the source preset library; never flashes hardware."""
import copy
import json
import re
import shutil
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
import palettes

class Editor:
    def __init__(self, root, source=palettes.SOURCE, output=palettes.OUTPUT):
        self.root, self.source, self.output = root, source, output
        self.data = json.loads(source.read_text(encoding='utf-8'))
        palettes.validate(self.data)
        # Read the actual mapping so preview follows firmware changes.
        core = (palettes.ROOT / 'DragonPrototype' / 'DragonCore.h').read_text(encoding='utf-8')
        mapping = re.search(r'ZONES\[8\]\[8\]\s*=\s*\{(.*?)\};', core, re.S)
        if not mapping: raise ValueError('Cannot find the firmware zone map')
        self.map = re.findall(r'\b(?:BG|LE|RE|LH|RH|FACE|BODY|TAIL|LW|RW)\b', mapping.group(1))
        if len(self.map) != 64: raise ValueError('Expected 64 logical pixels')
        self.zone_group = dict(zip(palettes.ZONES, palettes.ZONE_GROUPS))
        self.current = None
        root.title('Dragon colour studio')
        outer = ttk.Frame(root, padding=18); outer.pack(fill='both', expand=True)
        ttk.Label(outer, text='Dragon colour studio', font=('Segoe UI', 18, 'bold')).grid(row=0, column=0, columnspan=3, sticky='w')
        ttk.Label(outer, text='Choose colours, movement and a starting dragon. Save each dragon, then open Flash Dragons and click Build firmware before flashing.').grid(row=1, column=0, columnspan=3, sticky='w', pady=(3,15))
        self.selected = tk.StringVar()
        self.chooser = ttk.Combobox(outer, textvariable=self.selected, state='readonly', width=30,
                                    values=[p['id'] for p in self.data['presets'] if not p.get('retired',False)])
        self.chooser.grid(row=2, column=0, sticky='w'); self.chooser.bind('<<ComboboxSelected>>', self.change)
        self.description = ttk.Label(outer, wraplength=460)
        self.description.grid(row=3, column=0, columnspan=2, sticky='w', pady=10)
        left = ttk.LabelFrame(outer, text='Colours', padding=10); left.grid(row=4, column=0, sticky='nsw')
        self.colors, self.buttons = {}, {}
        for i, group in enumerate(palettes.GROUPS):
            ttk.Label(left, text=group.capitalize(), width=13).grid(row=i, column=0, sticky='w', pady=4)
            self.colors[group] = '#000000'
            button = tk.Button(left, width=14, command=lambda g=group: self.choose_color(g))
            button.grid(row=i, column=1, pady=4); self.buttons[group] = button
            if group=='background':button.configure(state='disabled')
        right = ttk.LabelFrame(outer, text='Movement', padding=10); right.grid(row=4, column=1, sticky='nsw', padx=14)
        self.effects = {}
        for i, effect in enumerate(palettes.EFFECTS):
            var = tk.BooleanVar(); self.effects[effect] = var
            ttk.Checkbutton(right, text=effect.capitalize(), variable=var).grid(row=i, column=0, columnspan=2, sticky='w')
        self.settings = {}
        for i, (key, label) in enumerate([('period_ms','Cycle (milliseconds)'),('breathe_min','Breath minimum %'),('shimmer_amount','Shimmer strength %'),('glitter_percent','Glitter chance %')], start=4):
            ttk.Label(right, text=label).grid(row=i, column=0, sticky='w', pady=5)
            var = tk.StringVar(); self.settings[key] = var
            ttk.Entry(right, width=8, textvariable=var).grid(row=i, column=1)
        self.accent = '#DAE5FF'
        self.accent_button = tk.Button(right, text='Accent colour', command=self.choose_accent)
        self.accent_button.grid(row=8, column=0, columnspan=2, sticky='ew', pady=8)
        preview = ttk.Frame(outer); preview.grid(row=4, column=2, sticky='n')
        ttk.Label(preview, text='Base colours · logical 8 × 8').pack(anchor='w')
        self.canvas = tk.Canvas(preview, width=272, height=272, background='#121821', highlightthickness=0)
        self.canvas.pack(pady=8)
        ttk.Label(preview, text='Static preview; physical LEDs and diffuser\nwill differ. Movement runs on the dragon.', wraplength=280).pack(anchor='w')
        zones = ttk.LabelFrame(outer, text='Where movement applies', padding=8)
        zones.grid(row=5, column=0, columnspan=3, sticky='ew', pady=14)
        self.animated = {}
        labels = ('Background','Left edge','Right edge','Left horn','Right horn','Face','Body','Tail','Left wing','Right wing')
        for i, (zone, label) in enumerate(zip(palettes.ZONES, labels)):
            var = tk.BooleanVar(); self.animated[zone] = var
            control=ttk.Checkbutton(zones, text=label, variable=var)
            control.grid(row=i//5, column=i%5, sticky='w', padx=7)
            if zone not in self.map:control.state(['disabled'])
        self.default = tk.BooleanVar()
        ttk.Checkbutton(outer, text='Start with this dragon after power-on', variable=self.default).grid(row=6,column=0,columnspan=3,sticky='w')
        buttons = ttk.Frame(outer); buttons.grid(row=7,column=0,columnspan=3,sticky='w',pady=(12,0))
        ttk.Button(buttons,text='Save preset',command=self.save).pack(side='left')
        ttk.Button(buttons,text='Close',command=self.close).pack(side='left',padx=8)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.status = ttk.Label(outer, wraplength=830)
        self.status.grid(row=8,column=0,columnspan=3,sticky='w',pady=(10,0))
        self.selected.set(self.data.get('default', self.data['presets'][0]['id'])); self.load()

    def load(self):
        self.current = copy.deepcopy(next(p for p in self.data['presets'] if p['id']==self.selected.get()))
        p=self.current; self.colors=dict(p['zones'])
        self.description.configure(text=f"{p['name']} · {p['tribe']}")
        for effect,var in self.effects.items(): var.set(effect in p.get('effects',[]))
        for key,var in self.settings.items(): var.set(str(p.get(key,palettes.DEFAULTS[key])))
        self.accent=p.get('accent',palettes.DEFAULTS['accent'])
        selected=p.get('animation_zones',palettes.DEFAULTS['animation_zones'])
        for zone,var in self.animated.items():var.set(zone in selected or self.zone_group[zone] in selected)
        self.default.set(self.data.get('default')==p['id'])
        self.status.configure(text=p.get('note','Original dragon palette.'))
        self.refresh()
        self.clean=self.collect()

    def refresh(self):
        for group,button in self.buttons.items():
            rgb=palettes.color(self.colors[group]); fg='black' if sum(rgb)>400 else 'white'
            button.configure(text=self.colors[group],background=self.colors[group],foreground=fg)
        self.accent_button.configure(background=self.accent)
        self.canvas.delete('all')
        preview=copy.deepcopy(self.current);preview['zones']=dict(self.colors)
        for i,color in enumerate(palettes.pixel_colors(preview)):
            x,y=(i%8)*34,(i//8)*34
            self.canvas.create_rectangle(x+2,y+2,x+32,y+32,fill=color,outline='')

    def choose_color(self, group):
        value=colorchooser.askcolor(self.colors[group],parent=self.root,title=group.capitalize())[1]
        if value:
            self.colors[group]=value.upper()
            # Editing a paired region deliberately sets both sides.
            for zone in palettes.ZONES:
                if self.zone_group[zone]==group:self.current.get('zone_overrides',{}).pop(zone,None)
            self.refresh()

    def choose_accent(self):
        value=colorchooser.askcolor(self.accent,parent=self.root,title='Shimmer / glitter accent')[1]
        if value:self.accent=value.upper();self.refresh()

    def collect(self):
        data=copy.deepcopy(self.data); p=copy.deepcopy(self.current)
        p['zones']=dict(self.colors);p['effects']=[e for e,v in self.effects.items() if v.get()]
        p['accent']=self.accent
        for key,var in self.settings.items():p[key]=int(var.get())
        p['animation_zones']=[z for z,v in self.animated.items() if v.get()]
        index=next(i for i,item in enumerate(data['presets']) if item['id']==p['id'])
        data['presets'][index]=p
        if self.default.get():data['default']=p['id']
        elif data.get('default')==p['id']:data['default']=data['presets'][0]['id']
        palettes.validate(data);return data

    def change(self, _event=None):
        old=self.current['id']
        try:dirty=self.collect()!=self.clean
        except ValueError:dirty=True
        if dirty and not messagebox.askyesno('Unsaved changes','Discard changes to the previous dragon?',parent=self.root):
            self.selected.set(old);return
        self.load()

    def close(self):
        try:dirty=self.collect()!=self.clean
        except ValueError:dirty=True
        if not dirty or messagebox.askyesno('Unsaved changes','Close without saving these changes?',parent=self.root):
            self.root.destroy()

    def save(self):
        try:
            data=self.collect()
            shutil.copy2(self.source,self.source.with_suffix('.json.bak'))
            temp=self.source.with_suffix('.json.tmp')
            temp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');temp.replace(self.source)
            palettes.generate(self.source,self.output)
            self.data=data;self.current=copy.deepcopy(next(p for p in data['presets'] if p['id']==self.selected.get()))
            self.clean=self.collect()
            self.status.configure(text='Saved. In Flash Dragons: Build firmware, then Flash this ESP32. Previous JSON kept as .json.bak.')
        except (ValueError,OSError) as error:messagebox.showerror('Could not save',str(error),parent=self.root)

def main(source=palettes.SOURCE, output=palettes.OUTPUT):
    root=tk.Tk();Editor(root,source,output);root.mainloop()

if __name__=='__main__':main()
