"""Build on the OS you intend to distribute to. Requires PyInstaller."""
import importlib.util
import subprocess
import sys
from pathlib import Path


def main():
    if importlib.util.find_spec('PyInstaller') is None:
        print('Install the optional builder first: python -m pip install pyinstaller')
        return 1
    root = Path(__file__).resolve().parent
    icon = 'icon.ico' if sys.platform == 'win32' else 'icon.icns' if sys.platform == 'darwin' else 'icon-large.png'
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--windowed',
               '--name', 'IPTVChannelPlayer', '--icon', str(root / 'assets' / icon)]
    # Bundle the guide too. A packaged app should not lose its own instructions.
    for name in ('assets', 'plugins', 'SETUP.md', 'README.md', 'description.md', 'channels.csv', 'LICENSE', 'BRANDING.md', 'VERSION', 'CSV-GUIDE.md'):
        if not (root / name).exists():
            continue
        command.extend(['--add-data', f'{root / name}{":" if sys.platform != "win32" else ";"}{name if (root / name).is_dir() else "."}'])
    command.append(str(root / 'iptv.py'))
    return subprocess.call(command, cwd=root)


if __name__ == '__main__':
    raise SystemExit(main())
