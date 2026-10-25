"""Build on the target OS; never bundle signing keys, backups or firmware."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from updater_core import APP_VERSION

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '.tools' / 'package'
NAME = 'Dragon Kingdom Updater'

def build():
    notices = OUT / 'Third-party notices'
    notices.mkdir(parents=True, exist_ok=True)
    for name in ('cryptography', 'certifi', 'zeroconf', 'psutil', 'ifaddr', 'cffi', 'pycparser', 'pyinstaller'):
        dist = importlib.metadata.distribution(name)
        for entry in dist.files or ():
            if any(part.lower().startswith(('license', 'copying', 'notice')) for part in entry.parts):
                source = Path(dist.locate_file(entry))
                if source.is_file():
                    target = notices / name / entry.name
                    target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
    for source in (Path(sys.base_prefix) / 'LICENSE.txt', Path(sys.base_prefix) / 'lib/python3.12/LICENSE.txt'):
        if source.is_file(): shutil.copyfile(source, notices / 'Python-LICENSE.txt')
    # Supply unmodified LGPL source alongside the bundled library, and the
    # updater sources/build recipe so families can rebuild with a modified copy.
    with urllib.request.urlopen('https://pypi.org/pypi/zeroconf/0.151.5/json', timeout=30) as response:
        release = json.load(response)
    sdist = next(item for item in release['urls'] if item['packagetype'] == 'sdist')
    if not sdist['url'].startswith('https://files.pythonhosted.org/'):
        raise ValueError('Unexpected dependency source host')
    with urllib.request.urlopen(sdist['url'], timeout=30) as response:
        source = response.read(5000001)
    if len(source) > 5000000 or hashlib.sha256(source).hexdigest() != sdist['digests']['sha256']:
        raise ValueError('Dependency source hash/size mismatch')
    (notices / sdist['filename']).write_bytes(source)
    source_dir = notices / 'updater-source'; source_dir.mkdir(exist_ok=True)
    for name in ('main.py', 'updater_core.py', 'package.py', 'requirements.txt', 'README.md', 'release-public-key.pem'):
        shutil.copyfile(ROOT / name, source_dir / name)
    (notices / 'README.txt').write_text(
        'Third-party software retains its own licences. Zeroconf 0.151.5 is unmodified LGPL-2.1-or-later; '
        'its complete upstream source and licence are included. You may rebuild this updater with a modified '
        'LGPL library; see updater-source/README.md and package.py. Python: https://www.python.org/psf/license/; '
        'Tcl/Tk: https://www.tcl-lang.org/software/tcltk/license.html; OpenSSL: https://www.openssl.org/source/license.html. '
        'The updater source and pinned build recipe are also at https://github.com/sai021/dragon-kingdom/tree/codex/shipping-reliability/desktop-updater.\n', encoding='utf-8')
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir', '--windowed', '--name', NAME,
            '--distpath', str(OUT / 'dist'), '--workpath', str(OUT / 'work'), '--specpath', str(OUT),
            '--add-data', str(ROOT / 'release-public-key.pem') + ':.',
            '--add-data', str(notices) + ':Third-party notices' ]
    if sys.platform == 'darwin':
        args += ['--osx-bundle-identifier', 'io.github.sai021.dragonkingdom.updater']
    subprocess.run(args + [str(ROOT / 'main.py')], check=True, cwd=ROOT)
    OUT.mkdir(parents=True, exist_ok=True)
    if sys.platform == 'darwin':
        import plistlib
        app = OUT / 'dist' / (NAME + '.app')
        plist = app / 'Contents/Info.plist'
        info = plistlib.loads(plist.read_bytes())
        info.update(CFBundleShortVersionString=APP_VERSION, CFBundleVersion=APP_VERSION,
                    NSLocalNetworkUsageDescription='Find and update your Dragon Kingdom lamp on home or dragon setup Wi-Fi.',
                    NSBonjourServices=['_http._tcp'])
        plist.write_bytes(plistlib.dumps(info))
        subprocess.run(['codesign', '--force', '--deep', '--sign', '-', str(app)], check=True)
        subprocess.run([str(app / 'Contents/MacOS' / NAME), '--self-test'], check=True)
        binary = app / 'Contents/MacOS' / NAME
        target = OUT / f'Dragon-Kingdom-Updater-Mac-{platform.machine()}.zip'
        subprocess.run(['ditto', '-c', '-k', '--sequesterRsrc', '--keepParent', str(app), str(target)], check=True)
    elif sys.platform == 'win32':
        folder = OUT / 'dist' / NAME
        subprocess.run([str(folder / (NAME + '.exe')), '--self-test'], check=True)
        binary = folder / (NAME + '.exe')
        target = OUT / 'Dragon-Kingdom-Updater-Windows-x64.zip'
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            for p in folder.rglob('*'):
                if p.is_file(): archive.write(p, p.relative_to(folder.parent))
    else: raise SystemExit('Package on Windows or Mac.')
    # Prove HTTPS works with the bundled CA file, not a developer's Python CA
    # path that will be absent on a family computer without Python installed.
    env = dict(os.environ, SSL_CERT_FILE=str(OUT / 'absent-ca.pem'), SSL_CERT_DIR=str(OUT / 'absent-ca-dir'))
    result_path = OUT / 'release-test-result.txt'
    result = subprocess.run([str(binary), '--release-test', str(result_path)], env=env, timeout=120)
    if result_path.exists(): print(result_path.read_text(encoding='utf-8'))
    if result.returncode: raise RuntimeError('Packaged release-download check failed; see result above.')
    print(target)

if __name__ == '__main__': build()
