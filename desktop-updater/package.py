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
from prepare_usb_service import prepare as prepare_service

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '.tools' / 'package'
NAME = 'Dragon Kingdom Easy Update'

def build():
    service_path = prepare_service()
    notices = OUT / 'Third-party notices'
    notices.mkdir(parents=True, exist_ok=True)
    names=['cryptography', 'certifi', 'zeroconf', 'psutil', 'ifaddr', 'cffi', 'pycparser', 'pyinstaller',
           'esptool', 'esp-pylib', 'pyserial', 'reedsolo', 'PyYAML', 'intelhex', 'rich-click', 'rich', 'click', 'colorama', 'pygments', 'markdown-it-py', 'mdurl']
    if sys.platform=='darwin':names+=['pyobjc-core','pyobjc-framework-Cocoa','pyobjc-framework-CoreWLAN','pyobjc-framework-CoreLocation']
    for name in names:
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
    for name in ('main.py', 'updater_core.py', 'wifi_control.py', 'batch_update.py', 'usb_update.py', 'usb_tool.py', 'prepare_usb_service.py', 'package.py', 'requirements.txt', 'README.md', 'release-public-key.pem'):
        shutil.copyfile(ROOT / name, source_dir / name)
    shutil.copytree(service_path / 'usb_service', source_dir / 'usb_service', dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
    # Distribute the unmodified GPL CLI separately, with its exact source.
    for package in ('esptool', 'esp-pylib'):
        version = importlib.metadata.version(package)
        with urllib.request.urlopen(f'https://pypi.org/pypi/{package}/{version}/json', timeout=30) as response:
            metadata = json.load(response)
        item = next(x for x in metadata['urls'] if x['packagetype'] == 'sdist')
        if not item['url'].startswith('https://files.pythonhosted.org/'):
            raise ValueError('Unexpected USB tool source host')
        with urllib.request.urlopen(item['url'], timeout=30) as response:
            raw = response.read(20000001)
        if len(raw) > 20000000 or hashlib.sha256(raw).hexdigest() != item['digests']['sha256']:
            raise ValueError('USB tool source hash/size mismatch')
        (notices / item['filename']).write_bytes(raw)
    helper_root = ROOT / '.tools/usb-helper'
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir', '--console',
                    '--name', 'dragon-usb-tool', '--distpath', str(helper_root / 'dist'),
                    '--workpath', str(helper_root / 'work'), '--specpath', str(helper_root),
                    '--collect-all', 'esptool', '--collect-all', 'esp_pylib', str(ROOT / 'usb_tool.py')], check=True)
    (notices / 'README.txt').write_text(
        'Third-party software retains its own licences. Zeroconf 0.151.5 is unmodified LGPL-2.1-or-later; '
        'its complete upstream source and licence are included. You may rebuild this updater with a modified '
        'LGPL library; see updater-source/README.md and package.py. Python: https://www.python.org/psf/license/; '
        'Tcl/Tk: https://www.tcl-lang.org/software/tcltk/license.html; OpenSSL: https://www.openssl.org/source/license.html. '
        'The updater source and pinned build recipe are also at https://github.com/sai021/dragon-kingdom/tree/codex/shipping-reliability/desktop-updater.\n', encoding='utf-8')
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir', '--windowed', '--name', NAME,
            '--paths', str(service_path),
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
                    NSLocationUsageDescription='Find nearby Dragon-Kingdom Wi-Fi networks so you can connect to your lamp.',
                    NSLocationWhenInUseUsageDescription='Find nearby Dragon-Kingdom Wi-Fi networks so you can connect to your lamp.',
                    NSBonjourServices=['_http._tcp'])
        plist.write_bytes(plistlib.dumps(info))
        subprocess.run(['codesign', '--force', '--deep', '--sign', '-', str(app)], check=True)
        subprocess.run([str(app / 'Contents/MacOS' / NAME), '--self-test', str(OUT / 'self-test.txt')], check=True)
        binary = app / 'Contents/MacOS' / NAME
        helper_dir = OUT / 'dist/USB Tools'
        shutil.copytree(helper_root / 'dist/dragon-usb-tool', helper_dir, dirs_exist_ok=True)
        subprocess.run([str(helper_dir / 'dragon-usb-tool'), '--help'], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['codesign', '--force', '--deep', '--sign', '-', str(helper_dir / 'dragon-usb-tool')], check=True)
        target = OUT / f'Dragon-Kingdom-Updater-Mac-{platform.machine()}.zip'
        stage = OUT / 'mac-zip'
        stage.mkdir(exist_ok=True)
        subprocess.run(['ditto', str(app), str(stage / app.name)], check=True)
        subprocess.run(['ditto', str(helper_dir), str(stage / 'USB Tools')], check=True)
        subprocess.run(['ditto', '-c', '-k', '--sequesterRsrc', str(stage), str(target)], check=True)
    elif sys.platform == 'win32':
        folder = OUT / 'dist' / NAME
        helper_dir = folder / 'USB Tools'
        shutil.copytree(helper_root / 'dist/dragon-usb-tool', helper_dir, dirs_exist_ok=True)
        subprocess.run([str(helper_dir / 'dragon-usb-tool.exe'), '--help'], check=True, stdout=subprocess.DEVNULL)
        subprocess.run([str(folder / (NAME + '.exe')), '--self-test', str(OUT / 'self-test.txt')], check=True)
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
