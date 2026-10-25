"""Package the reviewed firmware recovery implementation without Arduino CLI."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def prepare():
    original = ROOT.parent / 'dragon-firmware/tools'
    if not original.is_dir():
        if (ROOT / 'usb_service/recovery.py').is_file():
            return ROOT
        raise RuntimeError('Build from the full repository or supplied updater-source directory.')
    destination = ROOT / '.tools/service-source/usb_service'
    destination.mkdir(parents=True, exist_ok=True)
    (destination / '__init__.py').write_text('', encoding='utf-8')
    (destination / 'runtime.py').write_text(
        'from updater_core import backup_folder\nfrom .board_targets import TARGETS\n'
        'ROOT = backup_folder().parent / "USB Service"\nROOT.mkdir(mode=0o700, parents=True, exist_ok=True)\nFQBN = TARGETS["s3"]\n', encoding='utf-8')
    for name in ('recovery', 'flash_support', 'release_contract', 'board_targets', 'recovery_batch'):
        source = (original / (name + '.py')).read_text(encoding='utf-8')
        for module in ('board_targets', 'flash_support', 'release_contract'):
            source = source.replace('from ' + module + ' import', 'from .' + module + ' import')
        source = source.replace('from dev import ROOT, FQBN', 'from .runtime import ROOT, FQBN')
        if name == 'recovery':
            source = source.replace('subprocess.run(', 'run_tool(')
            source += '\n\ndef run_tool(*args, **kwargs):\n    kwargs.setdefault("creationflags", getattr(subprocess, "CREATE_NO_WINDOW", 0))\n    return subprocess.run(*args, **kwargs)\n'
        if name == 'release_contract':
            node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'public_key')
            lines = source.splitlines(keepends=True)
            lines[node.lineno-1:node.end_lineno] = ['def public_key():\n    from updater_core import trust_key\n    return trust_key()\n']
            source = ''.join(lines)
        (destination / (name + '.py')).write_text(source, encoding='utf-8')
    return destination.parent


if __name__ == '__main__':
    print(prepare())
