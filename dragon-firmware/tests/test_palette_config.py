import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('palettes', ROOT / 'tools' / 'palettes.py')
palettes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(palettes)

class PresetConfigTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(palettes.SOURCE.read_text(encoding='utf-8'))

    def test_real_catalog_and_header(self):
        self.assertEqual(len(palettes.validate(self.data)), 81)
        palettes.generate(check=True)

    def test_invalid_inputs(self):
        changes = [lambda p: p.update(id='bad"code'), lambda p: p.update(period_ms=0),
                   lambda p: p.update(period_ms=65536), lambda p: p.update(effects=['typo']),
                   lambda p: p.update(effects=['glitter','glitter']),
                   lambda p: p.update(glitter_percent=101), lambda p: p.update(animation_zones=['wingz']),
                   lambda p: p['zones'].update(edges='#12'), lambda p: p['zones'].pop('tail'),
                   lambda p: p.update(period_ms=True), lambda p: p.update(zone_overrides={'WRONG':'#112233'})]
        for change in changes:
            data = copy.deepcopy(self.data); change(data['presets'][0])
            with self.assertRaises(ValueError): palettes.validate(data)

    def test_duplicate_and_overrides(self):
        self.data['presets'][1]['id'] = self.data['presets'][0]['id']
        with self.assertRaises(ValueError): palettes.validate(self.data)
        self.data['presets'][1]['id'] = json.loads(palettes.SOURCE.read_text(encoding='utf-8'))['presets'][1]['id']
        self.data['presets'][0]['zone_overrides'] = {'LE':'#010203'}
        self.assertIn('{1,2,3}', palettes.header(self.data))

    def test_catalog_ids_cannot_shift_saved_custom_ids(self):
        for change in ('append', 'remove', 'reorder', 'rename'):
            with self.subTest(change=change):
                data=copy.deepcopy(self.data)
                if change=='append':
                    extra=copy.deepcopy(data['presets'][0]);extra['id']='extra';data['presets'].append(extra)
                elif change=='remove':data['presets'].pop()
                elif change=='reorder':data['presets'][0],data['presets'][1]=data['presets'][1],data['presets'][0]
                else:data['presets'][0]['id']='renamed'
                with self.assertRaisesRegex(ValueError,'saved-data compatibility'):palettes.header(data)

    def test_generate_and_stale_check(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder)/'dragons.json', Path(folder)/'DragonPresets.h'
            source.write_text(json.dumps(self.data), encoding='utf-8')
            palettes.generate(source, output); palettes.generate(source, output, check=True)
            self.data['presets'][4]['zones']['wings']='#123456'
            source.write_text(json.dumps(self.data), encoding='utf-8')
            with self.assertRaises(ValueError): palettes.generate(source, output, check=True)
            palettes.generate(source, output)
            self.assertIn('{18,52,86},{18,52,86}', output.read_text())

if __name__ == '__main__': unittest.main()
