"""Run the project's Python and native C++ regression suites without a board."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SUITES = ('core', 'load', 'power', 'presets', 'sensors', 'startup', 'voltage', 'connection', 'library', 'creations', 'c3', 'alarm', 'network_serial', 'library_web', 'http', 'release', 'lifecycle', 'transport')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cxx', default='c++', help='C++17 compiler executable')
    parser.add_argument('--zig', help='Use this Zig executable in C++ mode instead')
    parser.add_argument('--group', choices=['all','python','native'], default='all')
    args = parser.parse_args()
    output = ROOT / '.tools' / 'regression-tests'
    output.mkdir(parents=True, exist_ok=True)
    failures=[]
    if args.group in ('all','python'):
        if subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'], cwd=ROOT).returncode:failures.append('Python')
    compiler = [args.zig, 'c++'] if args.zig else [args.cxx]
    for suite in SUITES if args.group in ('all','native') else ():
        executable = output / ('test_' + suite + ('.exe' if os.name == 'nt' else ''))
        compile=subprocess.run(compiler + ['-std=c++17', '-I', str(ROOT / 'tests/transport-fakes'), '-I', str(ROOT / 'tests/fakes'), '-I', str(ROOT / 'tests/http-fakes'), str(ROOT / 'tests' / ('test_' + suite + '.cpp')), '-o', str(executable)], cwd=ROOT)
        if compile.returncode or subprocess.run([str(executable)], cwd=ROOT).returncode:failures.append(suite)
    if failures:
        print('Failed groups/suites: '+', '.join(failures));sys.exit(1)
    print('Requested regression groups passed.')

if __name__ == '__main__':
    main()
