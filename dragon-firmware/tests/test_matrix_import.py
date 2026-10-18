import json
import csv
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import import_matrix
import palettes

class MatrixImportTests(unittest.TestCase):
    def test_every_source_pixel_and_name(self):
        catalog=import_matrix.load_catalog()
        with import_matrix.SOURCE.open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(catalog['presets']),81)
        grid=palettes.layout()
        for p,row in zip(catalog['presets'],rows):
            self.assertEqual(p['name'],row['Dragon Name'])
            tokens=row['8x8 Matrix Hardware Array (64 Pixels Map)'].split(',')
            actual=palettes.pixel_colors(p)
            for i,token in enumerate(tokens):
                hue,gain=token.split('|');gain=int(gain)
                rgb=[v*gain//255 for v in palettes.color(hue)]
                if grid[i] in ('LE','RE') and any(rgb):rgb=[v+(255-v)*gain//1275 for v in rgb]
                self.assertEqual(palettes.color(actual[i]),tuple(rgb))
        sunny=next(p for p in catalog['presets'] if p['id']=='sunny')
        self.assertEqual(sunny['effect_zones']['breathe'],['FACE','BODY'])
        self.assertEqual(set(sunny['effect_zones']['glitter']),{'LE','RE','LW','RW'})

    def test_shipped_catalog_keeps_storage_slots_and_valid_pixels(self):
        shipped=json.loads(palettes.SOURCE.read_text(encoding='utf-8'))
        original=import_matrix.load_catalog()
        self.assertEqual([p['id'] for p in shipped['presets']],
                         [p['id'] for p in original['presets']])
        audit=json.loads((palettes.ROOT.parent/'docs/COLOUR-AUDIT-2026-10-18.json').read_text())
        self.assertEqual([p['id'] for p in audit['presets']],[p['id'] for p in shipped['presets']])
        self.assertEqual(sum(not p.get('retired',False) for p in shipped['presets']),79)
        for p,review in zip(shipped['presets'],audit['presets']):
            # Dated audit colours are historical evidence. The desktop editor
            # deliberately permits later colour changes without changing IDs.
            self.assertEqual(p['name'],review['name'])
            pixels=palettes.pixel_colors(p);self.assertEqual(len(pixels),64)
            for color in pixels:palettes.color(color)
        # The audit is a frozen reference, not a constraint on later colour edits.
        self.assertEqual(next(p for p in audit['presets'] if p['id']=='marsh')['zones']['body'],'#8B5B35')
        self.assertEqual(next(p for p in audit['presets'] if p['id']=='cricket')['zones']['wings'],'#EAA126')

    def test_edges_can_change_without_wings(self):
        p=import_matrix.load_catalog()['presets'][0]
        original=palettes.pixel_colors(p)
        p['zones']['edges']='#123456'
        changed=palettes.pixel_colors(p)
        for i,z in enumerate(palettes.layout()):
            self.assertEqual(changed[i],'#123456' if z in ('LE','RE') else original[i])

if __name__=='__main__':unittest.main()
