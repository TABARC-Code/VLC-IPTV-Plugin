"""TAVARC-Code IPTV Channel Player: CSV and playlist plumbing."""
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

FIELDS = ['id', 'name', 'group', 'country', 'language', 'stream_url', 'logo_url', 'tvg_id', 'enabled']
DISCLAIMER = 'Do not misuse this software. Use it only to access IPTV channels and streams you are authorised to watch. Do not use it to access or redistribute content unlawfully. You are responsible for complying with applicable laws, provider terms, and licensing requirements, including a UK TV Licence where required. Stream availability and playback are not guaranteed. Keep playlists containing passwords or access tokens private. This independent software is not affiliated with VideoLAN or any broadcaster.'


def enabled(row):
    return row.get('enabled', 'true').strip().lower() in ('true', '1', 'yes')


def validate(rows):
    seen = set()
    for i, row in enumerate(rows, 2):
        for key, value in row.items():
            if any(c in str(value) for c in '\r\n\x00'):
                raise ValueError(f'Row {i}: {key} must be a single line.')
        if not row.get('id') or not row.get('name'):
            raise ValueError(f'Row {i}: id and name are required.')
        if row['id'] in seen:
            raise ValueError(f'Row {i}: duplicate id {row["id"]}.')
        seen.add(row['id'])
        if row.get('enabled', '').lower() not in ('true', 'false', '1', '0', 'yes', 'no'):
            raise ValueError(f'Row {i}: enabled must be true or false.')
        url = row.get('stream_url', '')
        if not url or not urlsplit(url).scheme:
            raise ValueError(f'Row {i}: stream_url needs a URL scheme (such as https://).')


def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        missing = set(FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError('Missing CSV columns: ' + ', '.join(sorted(missing)))
        rows = []
        for line, raw in enumerate(reader, 2):
            if None in raw or any(raw.get(k) is None for k in FIELDS):
                raise ValueError(f'Row {line}: wrong number of columns.')
            rows.append({k: raw[k].strip() for k in FIELDS})
    validate(rows)
    return rows


def atomic_write(path, writer):
    # Write beside the destination, then swap it in. A failed save should leave the last good CSV alone.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.playlist-', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', newline='', encoding='utf-8') as f:
            writer(f)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_csv(path, rows):
    validate(rows)
    def write(f):
        out = csv.DictWriter(f, fieldnames=FIELDS)
        out.writeheader()
        out.writerows({k: r.get(k, '') for k in FIELDS} for r in rows)
    atomic_write(path, write)


def m3u_text(rows):
    validate(rows)
    lines = ['#EXTM3U']
    for row in rows:
        if not enabled(row):
            continue
        def attr(value):
            return value.replace('"', "'")
        lines.append('#EXTINF:-1 ' + ' '.join(
            f'{key}="{attr(row.get(field, ""))}"' for key, field in
            [('tvg-id', 'tvg_id'), ('tvg-name', 'name'), ('tvg-logo', 'logo_url'), ('group-title', 'group')]
        ) + ',' + row['name'])
        lines.append(row['stream_url'])
    return '\n'.join(lines) + '\n'


def export_m3u(path, rows):
    content = m3u_text(rows)
    atomic_write(path, lambda f: f.write(content))


def import_m3u(path):
    # Imports stay separate from the user's database. Guessing which duplicate to overwrite is a bad bargain.
    rows, pending, groups = [], {}, ''
    text = Path(path).read_text(encoding='utf-8-sig')
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('#EXTINF:'):
            match = re.match(r'^#EXTINF:[^\s,]+\s*((?:[^",]|"[^"]*")*),(.*)$', line)
            if not match:
                raise ValueError('Unsupported EXTINF formatting.')
            attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', match[1]))
            pending = {'name': match[2].strip(), 'group': attrs.get('group-title', ''),
                       'tvg_id': attrs.get('tvg-id', ''), 'logo_url': attrs.get('tvg-logo', '')}
            groups = ''
        elif line.startswith('#EXTGRP:'):
            groups = line.partition(':')[2]
        elif not line.startswith('#'):
            row = dict.fromkeys(FIELDS, '')
            row.update(pending)
            row.update(id=f'import-{len(rows)+1}', stream_url=line, enabled='true')
            row['name'] = row['name'] or f'Channel {len(rows)+1}'
            row['group'] = row['group'] or groups
            rows.append(row)
            pending, groups = {}, ''
    validate(rows)
    return rows


def check_stream(row, timeout=8):
    """Read a small HTTP prefix, never download a complete continuous stream."""
    if urlsplit(row['stream_url']).scheme.lower() not in ('http', 'https'):
        return 'UNTESTED', 'Reachability checks support HTTP(S); VLC may support this scheme.'
    try:
        request = Request(row['stream_url'], headers={'User-Agent': 'TAVARC-Code-IPTVChannelPlayer/1.0', 'Range': 'bytes=0-1023'})
        with urlopen(request, timeout=timeout) as response:
            prefix = response.read(1024)
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type or prefix.lstrip().lower().startswith((b'<!doctype html', b'<html')):
                return 'WEB PAGE', 'HTTP response appears to be HTML, not a stream.'
            if not prefix:
                return 'EMPTY', 'No data received.'
            return 'REACHABLE', 'Received data; playback, manifest segments and licensing not verified.'
    except Exception as error:
        # Do not copy exception text: it can expose token-bearing URLs.
        return 'FAILED', f'{type(error).__name__}; check access, network or provider requirements.'


def find_vlc():
    found = shutil.which('vlc')
    if found:
        return found
    candidates = ['/Applications/VLC.app/Contents/MacOS/VLC'] if sys.platform == 'darwin' else []
    if sys.platform == 'win32':
        for root in ('ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA'):
            if os.environ.get(root):
                candidates.append(str(Path(os.environ[root]) / 'VideoLAN' / 'VLC' / 'vlc.exe'))
    return next((p for p in candidates if Path(p).is_file()), None)


def launch_vlc(executable, playlist):
    # Pass filenames as arguments, never shell commands. Spaces in a Windows path are normal.
    return subprocess.Popen([str(executable), '--', str(Path(playlist).resolve())], shell=False)
