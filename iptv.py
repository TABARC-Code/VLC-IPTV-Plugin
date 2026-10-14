#!/usr/bin/env python3
"""TAVARC-Code IPTV Channel Player. Open the window, or use the optional CLI."""
import argparse
import csv
from studio import core


def main():
    parser = argparse.ArgumentParser(description='TAVARC-Code IPTV Channel Player — CSV channel management and VLC playback.', epilog=core.DISCLAIMER)
    sub = parser.add_subparsers(dest='command')
    for name in ('export', 'import', 'check'):
        command = sub.add_parser(name)
        command.add_argument('input')
        command.add_argument('--output', required=True)
    args = parser.parse_args()
    if not args.command:
        try:
            from studio.gui import run
            run()
        except ImportError as error:
            parser.exit(1, f'GUI dependency unavailable: {error}. Install Tkinter; see README.\n')
        return
    try:
        if args.command == 'import':
            core.write_csv(args.output, core.import_m3u(args.input))
        else:
            rows = core.read_csv(args.input)
            if args.command == 'export':
                core.export_m3u(args.output, rows)
            else:
                from concurrent.futures import ThreadPoolExecutor
                active = [r for r in rows if core.enabled(r)]
                with ThreadPoolExecutor(max_workers=4) as pool:
                    results = list(pool.map(core.check_stream, active))
                def write(f):
                    writer = csv.writer(f)
                    writer.writerow(['id', 'name', 'status', 'detail'])
                    for row, result in zip(active, results):
                        writer.writerow([row['id'], row['name'], *result])
                core.atomic_write(args.output, write)
        print(f'Created {args.output}')
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
