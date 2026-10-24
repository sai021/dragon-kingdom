import gzip,re,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import embed_web
class GeneratedTests(unittest.TestCase):
    def test_compressed_page_exactly_matches_editable_sources(self):
        root=embed_web.ROOT
        expected=(root/'web/dragon-kingdom.html').read_text(encoding='utf-8').replace('<script src="/library.js"></script>','<script>\n'+(root/'web/library.js').read_text(encoding='utf-8')+'\n</script>')
        header=(root/'DragonPrototype/DragonWebPage.h').read_text(encoding='utf-8')
        payload=bytes(int(n) for n in re.search(r'pageGzip\[\] PROGMEM=\{([^}]+)\}',header)[1].split(','))
        self.assertEqual(gzip.decompress(payload),expected.encode('utf-8'))
        self.assertLess(len(payload),len(expected.encode('utf-8')))
