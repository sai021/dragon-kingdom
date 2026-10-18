import json
from pathlib import Path
import sys
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import palettes
from palette_editor import Editor

class EditorTests(unittest.TestCase):
    def test_wing_colour_covers_bottom_pixels_and_preserves_other_dragons(self):
        root=tk.Tk();root.withdraw()
        try:
            with tempfile.TemporaryDirectory() as directory:
                source=Path(directory)/'dragons.json';output=Path(directory)/'DragonPresets.h'
                original=json.loads(palettes.SOURCE.read_text(encoding='utf-8'))
                source.write_text(json.dumps(original),encoding='utf-8')
                editor=Editor(root,source,output)
                self.assertEqual(editor.buttons['background'].cget('state'),'disabled')
                before=palettes.pixel_colors(editor.current)
                with patch('palette_editor.colorchooser.askcolor',return_value=((18,52,86),'#123456')):
                    editor.choose_color('wings')
                editor.save()
                saved=json.loads(source.read_text(encoding='utf-8'))
                self.assertEqual([p['id'] for p in saved['presets']],[p['id'] for p in original['presets']])
                self.assertEqual(saved['presets'][1:],original['presets'][1:])
                pixels=palettes.pixel_colors(saved['presets'][0])
                for i,z in enumerate(editor.map):
                    self.assertEqual(pixels[i],'#123456' if z in ('LW','RW') else before[i])
                for i in (48,55,56,61,62,63):self.assertEqual(pixels[i],'#123456')
                self.assertEqual(len(editor.canvas.find_all()),64)
                palettes.generate(source,output,check=True)
                editor.load()
                self.assertEqual(editor.colors['wings'],'#123456')
        finally:root.destroy()

    def test_colour_preview_save_and_default(self):
        root=tk.Tk();root.withdraw()
        try:
            with tempfile.TemporaryDirectory() as directory:
                source=Path(directory)/'dragons.json';output=Path(directory)/'DragonPresets.h'
                source.write_text(palettes.SOURCE.read_text(encoding='utf-8'),encoding='utf-8')
                editor=Editor(root,source,output);root.update_idletasks()
                self.assertEqual(editor.collect(),editor.clean)
                self.assertEqual(len(editor.canvas.find_all()),64)
                editor.selected.set('glory');editor.load()
                editor.colors['wings']='#123456';editor.effects['glitter'].set(True)
                editor.default.set(True);editor.refresh();editor.save()
                data=json.loads(source.read_text());p=next(p for p in data['presets'] if p['id']=='glory')
                self.assertEqual(p['zones']['wings'],'#123456')
                self.assertIn('glitter',p['effects']);self.assertEqual(data['default'],'glory')
                self.assertTrue(source.with_suffix('.json.bak').exists())
                palettes.generate(source,output,check=True)
                self.assertEqual(editor.collect(),editor.clean)
                wing=editor.map.index('LW');item=editor.canvas.find_all()[wing]
                self.assertEqual(editor.canvas.itemcget(item,'fill'),'#123456')
                editor.settings['period_ms'].set('0')
                with self.assertRaises(ValueError):editor.collect()
        finally:root.destroy()

if __name__=='__main__':unittest.main()
