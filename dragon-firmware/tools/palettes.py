#!/usr/bin/env python3
"""Edit named dragon colours/effects without changing C++. Standard library only."""
import argparse
import copy
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'presets' / 'dragons.json'
OUTPUT = ROOT / 'DragonPrototype' / 'DragonPresets.h'
GROUPS = ('background', 'edges', 'horns', 'face', 'body', 'tail', 'wings')
ZONE_GROUPS = ('background', 'edges', 'edges', 'horns', 'horns', 'face', 'body', 'tail', 'wings', 'wings')
ZONES = ('BG', 'LE', 'RE', 'LH', 'RH', 'FACE', 'BODY', 'TAIL', 'LW', 'RW')
EFFECTS = {'cycle': 1, 'breathe': 2, 'shimmer': 4, 'glitter': 8}
DEFAULTS = {'period_ms': 6000, 'breathe_min': 65, 'shimmer_amount': 35, 'glitter_percent': 10,
            'accent': '#DAE5FF', 'animation_zones': ['face', 'body', 'tail', 'wings']}

def color(value):
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        raise ValueError(f'Colour must be #RRGGBB: {value!r}')
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))

def validate(data):
    if not isinstance(data, dict) or data.get('schema') != 1:
        raise ValueError('Expected schema 1')
    presets = data.get('presets')
    if not isinstance(presets, list) or not 1 <= len(presets) <= 255:
        raise ValueError('Use 1..255 presets')
    # Version-1 saved records use preset-count-relative custom IDs. Freeze the
    # supplied slots until an explicit storage migration is implemented.
    stable = json.loads((ROOT / 'presets/catalog-ids.json').read_text(encoding='utf-8'))
    if [p.get('id') if isinstance(p, dict) else None for p in presets] != stable:
        raise ValueError('Catalog IDs and order are fixed for saved-data compatibility. Edit colours or create a custom dragon on the device instead.')
    seen = set()
    allowed = {'id', 'name', 'tribe', 'zones', 'zone_overrides', 'effects', 'source', 'note', 'pixels', 'reference_zones', 'effect_zones', 'retired'} | set(DEFAULTS)
    for p in presets:
        if not isinstance(p, dict) or set(p) - allowed:
            raise ValueError('Unknown preset fields')
        if type(p.get('retired',False)) is not bool: raise ValueError('retired must be a boolean')
        slug = p.get('id', '')
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,31}', slug) or slug in seen:
            raise ValueError(f'Invalid or duplicate preset id: {slug!r}')
        seen.add(slug)
        if not isinstance(p.get('name'), str) or not p['name'] or len(p['name']) > 60:
            raise ValueError(f'{slug}: use a name of 1..60 characters')
        if not isinstance(p.get('tribe'), str) or len(p['tribe']) > 80:
            raise ValueError(f'{slug}: tribe must be text up to 80 characters')
        if not isinstance(p.get('zones'), dict) or set(p['zones']) != set(GROUPS):
            raise ValueError(f'{slug}: zones must contain exactly {GROUPS}')
        for value in p['zones'].values(): color(value)
        if 'pixels' in p:
            if len(p['pixels']) != 64: raise ValueError('Expected 64 pixel colours')
            for value in p['pixels']: color(value)
        if 'reference_zones' in p:
            if set(p['reference_zones']) != set(GROUPS): raise ValueError('Invalid reference zones')
            for value in p['reference_zones'].values(): color(value)
        for effect, zones in p.get('effect_zones', {}).items():
            if effect not in EFFECTS or any(z not in ZONES for z in zones): raise ValueError('Invalid effect zones')
        overrides = p.get('zone_overrides', {})
        if not isinstance(overrides, dict) or set(overrides) - set(ZONES):
            raise ValueError(f'{slug}: unknown zone override')
        for value in overrides.values(): color(value)
        effects = p.get('effects', [])
        if not isinstance(effects, list) or any(e not in EFFECTS for e in effects) or len(effects) != len(set(effects)):
            raise ValueError(f'{slug}: effects must be unique choices from {tuple(EFFECTS)}')
        for key in ('period_ms', 'breathe_min', 'shimmer_amount', 'glitter_percent'):
            v = p.get(key, DEFAULTS[key])
            low, high = (1000, 60000) if key == 'period_ms' else (0, 100)
            if type(v) is not int or not low <= v <= high:
                raise ValueError(f'{slug}: {key} must be an integer in {low}..{high}')
        color(p.get('accent', DEFAULTS['accent']))
        animated = p.get('animation_zones', DEFAULTS['animation_zones'])
        if not isinstance(animated, list) or any(z not in GROUPS + ZONES for z in animated):
            raise ValueError(f'{slug}: unknown animation zone')
    if any(p.get('retired',False) and p['id']==data.get('default',presets[0]['id']) for p in presets): raise ValueError('Default must be an active preset')
    if data.get('default', presets[0]['id']) not in seen:
        raise ValueError('Default must name an existing preset id')
    return presets

def cpp_rgb(value):
    return '{' + ','.join(map(str, color(value))) + '}'

def layout():
    core = (ROOT/'DragonPrototype'/'DragonCore.h').read_text(encoding='utf-8')
    grid = re.search(r'ZONES\[8\]\[8\]\s*=\s*\{(.*?)\};', core, re.S)
    return re.findall(r'\b(?:BG|LE|RE|LH|RH|FACE|BODY|TAIL|LW|RW)\b', grid.group(1))

def pixel_colors(p):
    result = []
    for i, z in enumerate(layout()):
        group = ZONE_GROUPS[ZONES.index(z)]
        c = p.get('pixels', [p['zones'][group]]*64)[i]
        if p['zones'][group] != p.get('reference_zones', p['zones'])[group]: c = p['zones'][group]
        c = p.get('zone_overrides', {}).get(z, c)
        result.append(c)
    return result

def header(data):
    presets = validate(data)
    lines = ['#pragma once', '// Generated by tools/palettes.py from presets/dragons.json. Do not edit.',
             '#include "DragonCore.h"', 'namespace Dragon {',
             'enum PresetEffect : uint8_t { PRESET_CYCLE=1, PRESET_BREATHE=2, PRESET_SHIMMER=4, PRESET_GLITTER=8 };',
             'struct DragonPreset {', ' const char* id; const char* name; RGB zones[ZONE_COUNT];',
             ' uint8_t effects; uint16_t animatedZones,periodMs;',
             ' uint8_t breatheMin,shimmerAmount,glitterPercent; RGB accent; RGB pixels[64]; uint16_t effectZones[4];', '};',
             'static const DragonPreset DRAGON_PRESETS[] = {']
    for p in presets:
        rgb = [cpp_rgb(p.get('zone_overrides', {}).get(z, p['zones'][group])) for z, group in zip(ZONES, ZONE_GROUPS)]
        animated = p.get('animation_zones', DEFAULTS['animation_zones'])
        mask = sum(1 << i for i, (z, group) in enumerate(zip(ZONES, ZONE_GROUPS)) if z in animated or group in animated)
        values = [sum(EFFECTS[e] for e in p.get('effects', [])), mask]
        values += [p.get(k, DEFAULTS[k]) for k in ('period_ms', 'breathe_min', 'shimmer_amount', 'glitter_percent')]
        masks = [sum(1 << ZONES.index(z) for z in set(p.get('effect_zones', {}).get(e, ZONES))) & mask for e in EFFECTS]
        lines.append(' {' + json.dumps(p['id']) + ',' + json.dumps(p['name'], ensure_ascii=True) + ',{' + ','.join(rgb) + '},' +
                     ','.join(map(str, values)) + ',' + cpp_rgb(p.get('accent', DEFAULTS['accent'])) + ',{' +
                     ','.join(cpp_rgb(c) for c in pixel_colors(p)) + '},{' + ','.join(map(str,masks)) + '}},')
    default = next(i for i, p in enumerate(presets) if p['id'] == data.get('default', presets[0]['id']))
    lines += ['};', 'constexpr uint8_t PRESET_COUNT=sizeof(DRAGON_PRESETS)/sizeof(DRAGON_PRESETS[0]);',
              f'constexpr uint8_t DEFAULT_PRESET={default};',
              'static const bool PRESET_RETIRED[] = {' + ','.join('true' if p.get('retired',False) else 'false' for p in presets) + '};',
              'constexpr uint8_t ACTIVE_PRESET_COUNT=' + str(sum(not p.get('retired',False) for p in presets)) + ';', '}']
    return '\n'.join(lines) + '\n'

def generate(source=SOURCE, output=OUTPUT, check=False):
    result = header(json.loads(Path(source).read_text(encoding='utf-8')))
    output = Path(output)
    current = output.read_text(encoding='utf-8') if output.exists() else None
    if check:
        if current != result: raise ValueError('Generated presets are stale; run tools/palettes.py generate')
    elif current != result:
        output.parent.mkdir(parents=True, exist_ok=True)
        temp = output.with_suffix('.h.tmp')
        temp.write_text(result, encoding='utf-8')
        temp.replace(output)

def edit(data, slug):
    presets = validate(data)
    if slug is None:
        for p in presets: print(f"{p['id']:16} {p['name']}")
        slug = input('Dragon id to edit: ').strip()
    selected = next((p for p in presets if p['id'] == slug), None)
    if selected is None: raise ValueError(f'Unknown dragon: {slug}')
    print(f"Editing {selected['name']}. Enter keeps the current value. Ctrl+C cancels.")
    edited = copy.deepcopy(selected)
    for group in GROUPS:
        value = input(f"{group.capitalize():12} [{selected['zones'][group]}]: ").strip()
        if value: color(value); edited['zones'][group] = value.upper()
    effects = input(f"Effects: cycle breathe shimmer glitter (or none) [{','.join(selected.get('effects', [])) or 'none'}]: ").strip()
    if effects: edited['effects'] = [] if effects == 'none' else effects.replace(',', ' ').split()
    for key in ('period_ms', 'breathe_min', 'shimmer_amount', 'glitter_percent', 'accent'):
        current = selected.get(key, DEFAULTS[key])
        value = input(f'{key} [{current}]: ').strip()
        if value: edited[key] = value if key == 'accent' else int(value)
    zones = input('Animated zones, space-separated [' + ' '.join(selected.get('animation_zones', DEFAULTS['animation_zones'])) + ']: ').strip()
    if zones: edited['animation_zones'] = zones.split()
    index = presets.index(selected); presets[index] = edited
    validate(data)
    return data

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['list', 'gui', 'edit', 'clone', 'default', 'generate', 'check'])
    parser.add_argument('id', nargs='?')
    parser.add_argument('new_id', nargs='?')
    parser.add_argument('--name')
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        if args.action == 'gui':
            from palette_editor import main as open_editor
            open_editor(args.source, args.output)
            return
        data = json.loads(args.source.read_text(encoding='utf-8'))
        presets = validate(data)
        if args.action == 'list':
            for i, p in enumerate(presets):
                print(f"{i:2}  {p['id']:16} {p['tribe']:22} {', '.join(p.get('effects', [])) or 'steady'}")
            return
        if args.action == 'edit': edit(data, args.id)
        if args.action == 'default': data['default'] = args.id
        if args.action == 'clone':
            if not args.id or not args.new_id: raise ValueError('clone needs an existing id and a new id')
            original = next((p for p in presets if p['id'] == args.id), None)
            if original is None: raise ValueError(f'Unknown dragon: {args.id}')
            new = copy.deepcopy(original); new['id'] = args.new_id; new['name'] = args.name or args.new_id
            new['tribe'] = 'Custom'; new['note'] = 'Custom variation; colours and effects may differ from the source character.'
            presets.append(new)
        if args.action in ('edit', 'clone', 'default'):
            validate(data)
            shutil.copy2(args.source, args.source.with_suffix('.json.bak'))
            temp = args.source.with_suffix('.json.tmp')
            temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            temp.replace(args.source)
        generate(args.source, args.output, check=args.action == 'check')
        print('Presets checked.' if args.action == 'check' else 'Presets ready. Build/upload with tools/dev.py to install them.')
    except (ValueError, OSError, TypeError) as error: parser.exit(1, f'Error: {error}\n')
    except (KeyboardInterrupt, EOFError): parser.exit(1, '\nCancelled; no preset changes saved.\n')

if __name__ == '__main__': main()
