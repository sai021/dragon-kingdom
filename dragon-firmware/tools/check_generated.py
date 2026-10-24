"""Fail if checked-in generated headers differ from their editable sources."""
from pathlib import Path
from embed_web import generate as web
from palettes import generate as palettes
root=Path(__file__).resolve().parents[1]
paths=[root/'DragonPrototype/DragonWebPage.h',root/'DragonPrototype/DragonPresets.h']
before=[p.read_bytes() for p in paths]
try:
    web();palettes()
    stale=[str(p.relative_to(root)) for p,b in zip(paths,before) if p.read_bytes()!=b]
finally:
    for p,b in zip(paths,before):p.write_bytes(b)
if stale:raise SystemExit('Regenerate checked-in sources: '+', '.join(stale))
print('Generated sources match.')
