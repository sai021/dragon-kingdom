"""Embed the editable, offline Dragon Kingdom page in program flash."""
from pathlib import Path
import gzip

ROOT = Path(__file__).resolve().parents[1]

def generate():
    page = (ROOT / 'web/dragon-kingdom.html').read_text(encoding='utf-8')
    page = page.replace('<script src="/library.js"></script>', '<script>\n' + (ROOT / 'web/library.js').read_text(encoding='utf-8') + '\n</script>')
    if ')DRAGONWEB"' in page:
        raise ValueError('Page contains the C++ raw-string delimiter')
    output = '#pragma once\n// Generated from web/dragon-kingdom.html by tools/embed_web.py.\n'
    output += 'const char page[] PROGMEM=R"DRAGONWEB(' + page + ')DRAGONWEB";\n'
    compressed=gzip.compress(page.encode('utf-8'),mtime=0)
    output+='const unsigned char pageGzip[] PROGMEM={'+','.join(str(b) for b in compressed)+'};\n'
    target = ROOT / 'DragonPrototype/DragonWebPage.h'
    if not target.exists() or target.read_text(encoding='utf-8') != output:
        target.write_text(output, encoding='utf-8')

if __name__ == '__main__':
    generate()
