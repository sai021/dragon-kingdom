"""Fail if checked-in generated headers differ from their editable sources."""
from pathlib import Path
import gzip
import re
from embed_web import generate as web
from palettes import generate as palettes
def comparable(raw):
    text=raw.decode('utf-8').replace('\r\n','\n')
    # gzip's OS byte and deflate encoding can vary with Python/zlib/platform.
    # Require identical C++ and exact decompressed data, including a valid CRC.
    def unpack(match):
        payload=bytes(int(n) for n in match[1].split(','))
        return 'pageGzip_CONTENT='+repr(gzip.decompress(payload))
    return re.sub(r'const unsigned char pageGzip\[\] PROGMEM=\{([0-9,]+)\};',unpack,text)

def main():
    root=Path(__file__).resolve().parents[1]
    paths=[root/'DragonPrototype/DragonWebPage.h',root/'DragonPrototype/DragonPresets.h']
    before=[p.read_bytes() for p in paths]
    try:
        web();palettes()
        stale=[str(p.relative_to(root)) for p,b in zip(paths,before) if comparable(p.read_bytes())!=comparable(b)]
    finally:
        for p,b in zip(paths,before):p.write_bytes(b)
    if stale:raise SystemExit('Regenerate checked-in sources: '+', '.join(stale))
    print('Generated sources match.')

if __name__=='__main__':main()
