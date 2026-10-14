"""Small pre-flight check for people who just want to open the app."""
import sys


def main():
    print('TAVARC-Code | IPTV Channel Player')
    if sys.version_info < (3, 10):
        print('Please install Python 3.10 or newer: https://www.python.org/downloads/')
        return 1
    try:
        import tkinter as tk
        probe = tk.Tk()
        probe.withdraw()
        probe.destroy()
    except ImportError:
        print('Python is installed, but Tkinter is missing.')
        print('Windows/macOS: install python.org Python with Tcl/Tk selected.')
        print('Ubuntu/Debian: sudo apt install python3-tk')
        print('Fedora: sudo dnf install python3-tkinter')
        return 1
    except Exception as error:
        print(f'The desktop window could not open ({type(error).__name__}).')
        print('Run this from your desktop session. SSH/headless terminals can still use the CLI.')
        return 1
    # No pip installs are needed. Keeping setup offline also keeps it predictable.
    from studio.gui import run
    run()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
