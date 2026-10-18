"""Import the supplied 64-pixel CSV; descriptions map to bounded visual effects.
Rerunning replaces the editable catalog, so use only when importing a new CSV.
"""
import csv
import json
import re
from pathlib import Path
import palettes

SOURCE = palettes.ROOT/'DragonPrototype/wings_of_fire_lightbox_matrix.csv'

def load_catalog(source=SOURCE):
    result=[]
    aliases={'LW':['LW','LE'],'RW':['RW','RE'],'FA':['FACE'],'BO':['BODY'],'TA':['TAIL'],
             'LH':['LH'],'RH':['RH'],'BG':['BG']}
    grid=palettes.layout()
    with Path(source).open(encoding='utf-8-sig',newline='') as stream:
        rows=list(csv.DictReader(stream))
    for row in rows:
        tokens=row['8x8 Matrix Hardware Array (64 Pixels Map)'].split(',')
        if len(tokens)!=64: raise ValueError(f"{row['Dragon Name']}: expected 64 pixels")
        pixels=[]
        for i,token in enumerate(tokens):
            hue,gain=token.strip().split('|');gain=int(gain)
            if not 0<=gain<=255: raise ValueError('Invalid pixel intensity')
            rgb=[v*gain//255 for v in palettes.color(hue)]
            # Preserve separate edges with a modest lighter tint, keeping off pixels off.
            if grid[i] in ('LE','RE') and any(rgb): rgb=[v+(255-v)*gain//(255*5) for v in rgb]
            pixels.append('#'+''.join(f'{v:02X}' for v in rgb))
        # Retain the legacy background field even though no physical pixel uses it.
        zones={}
        for group in palettes.GROUPS:
            index=next((i for i,z in enumerate(grid) if palettes.ZONE_GROUPS[palettes.ZONES.index(z)]==group),None)
            zones[group]=pixels[index] if index is not None else '#000000'
        desc=row['Area Lighting Effects'];effect_zones={}
        for regions,words in re.findall(r'([A-Z /]+):\s*([^.:]+)',desc):
            regions=regions.strip();words=words.lower()
            if regions=='ALL ZONES': selected=list(palettes.ZONES)
            elif regions=='ALL CORES': selected=['FACE','BODY','TAIL']
            else: selected=[z for token in regions.split('/') for z in aliases.get(token.strip(),[])]
            if not selected: continue
            effects=[]
            if 'sparkle' in words: effects.append('glitter')
            elif 'shimmer' in words or 'flicker' in words or 'glare' in words or 'flare' in words or 'wave' in words: effects.append('shimmer')
            elif 'shift' in words: effects.append('cycle')
            if any(w in words for w in ('breath','pulse','fade')): effects.append('breathe')
            for effect in effects: effect_zones.setdefault(effect,set()).update(selected)
        effect_zones={e:sorted(z,key=palettes.ZONES.index) for e,z in effect_zones.items()}
        animated=sorted(set(z for zones_ in effect_zones.values() for z in zones_),key=palettes.ZONES.index)
        name=row['Dragon Name'];slug=re.sub('[^a-z0-9]+','-',name.lower()).strip('-')
        fast=any(w in desc.lower() for w in ('fast','quick','high frequency','flicker'))
        result.append({'id':slug,'name':name,'tribe':row['Tribe'],'zones':zones,'reference_zones':dict(zones),
                       'pixels':pixels,'effects':list(effect_zones),'effect_zones':effect_zones,'animation_zones':animated,
                       'period_ms':2000 if fast else 6000,'breathe_min':65,'shimmer_amount':30,'glitter_percent':10,
                       'accent':'#DAE5FF','source':SOURCE.name,'note':desc})
    data={'schema':1,'default':result[0]['id'],'presets':result}
    palettes.validate(data)
    return data

if __name__=='__main__':
    data=load_catalog()
    palettes.SOURCE.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    palettes.generate()
    print(f"Imported {len(data['presets'])} dragons with 64-pixel maps and independent wing edges.")
