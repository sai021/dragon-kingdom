"""Build on the target OS; never bundle signing keys, backups or firmware."""
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '.tools' / 'package'
NAME = 'Dragon Kingdom Updater'

def build():
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir', '--windowed', '--name', NAME,
            '--distpath', str(OUT / 'dist'), '--workpath', str(OUT / 'work'), '--specpath', str(OUT),
            '--add-data', str(ROOT / 'release-public-key.pem') + ':.' ]
    if sys.platform == 'darwin':
        args += ['--osx-bundle-identifier', 'io.github.sai021.dragonkingdom.updater']
    subprocess.run(args + [str(ROOT / 'main.py')], check=True, cwd=ROOT)
    OUT.mkdir(parents=True, exist_ok=True)
    if sys.platform == 'darwin':
        import plistlib
        app = OUT / 'dist' / (NAME + '.app')
        plist = app / 'Contents/Info.plist'
        info = plistlib.loads(plist.read_bytes())
        info.update(CFBundleShortVersionString='1.0.0', CFBundleVersion='1.0.0',
                    NSLocalNetworkUsageDescription='Find and update your Dragon Kingdom lamp on your home network.',
                    NSBonjourServices=['_http._tcp'])
        plist.write_bytes(plistlib.dumps(info))
        subprocess.run(['codesign', '--force', '--deep', '--sign', '-', str(app)], check=True)
        subprocess.run([str(app / 'Contents/MacOS' / NAME), '--self-test'], check=True)
        target = OUT / f'Dragon-Kingdom-Updater-Mac-{platform.machine()}.zip'
        subprocess.run(['ditto', '-c', '-k', '--sequesterRsrc', '--keepParent', str(app), str(target)], check=True)
    elif sys.platform == 'win32':
        folder = OUT / 'dist' / NAME
        subprocess.run([str(folder / (NAME + '.exe')), '--self-test'], check=True)
        target = OUT / 'Dragon-Kingdom-Updater-Windows-x64.zip'
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            for p in folder.rglob('*'):
                if p.is_file(): archive.write(p, p.relative_to(folder.parent))
    else: raise SystemExit('Package on Windows or Mac.')
    print(target)

if __name__ == '__main__': build()
