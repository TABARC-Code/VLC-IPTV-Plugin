#!/usr/bin/env python3
"""IPTV Channel Player v.1.6: load a CSV and hand the playlist to VLC."""
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from studio import core

ROOT = Path(__file__).resolve().parent


class Player(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('IPTV Channel Player v.1.6 | TAVARC-Code')
        self.geometry('750x440')
        self.rows = []
        self.icon = tk.PhotoImage(file=str(ROOT / 'assets' / 'icon.png'))
        self.iconphoto(True, self.icon)
        ttk.Label(self, text='IPTV CHANNEL PLAYER', font=('Segoe UI', 20, 'bold')).pack(pady=(18, 4))
        ttk.Label(self, text='TAVARC-Code · v.1.6 · CSV playlists played through VLC').pack()
        bar = ttk.Frame(self, padding=14)
        bar.pack()
        for name, action in [('Open CSV', self.open_csv), ('Export M3U', self.export), ('Open VLC', self.play), ('Help & usage', self.help)]:
            ttk.Button(bar, text=name, command=action).pack(side='left', padx=4)
        self.list = tk.Listbox(self, font=('Segoe UI', 11))
        self.list.pack(fill='both', expand=True, padx=18)
        self.status = tk.StringVar(value='Open your CSV to begin. Sample entries are disabled placeholders.')
        ttk.Label(self, textvariable=self.status, wraplength=700).pack(pady=14)

    def attempt(self, action):
        try:
            action()
        except Exception as error:
            messagebox.showerror('IPTV Channel Player', str(error))

    def open_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV database', '*.csv')])
        if path:
            def load():
                rows = core.read_csv(path)
                self.rows = rows
                self.list.delete(0, 'end')
                for row in rows:
                    self.list.insert('end', f'{row["name"]} — {row["group"]} ({"enabled" if core.enabled(row) else "disabled"})')
                self.status.set(f'Loaded {len(rows)} records. Playback uses all enabled rows.')
            self.attempt(load)

    def export(self):
        path = filedialog.asksaveasfilename(defaultextension='.m3u', filetypes=[('M3U playlist', '*.m3u')])
        if path:
            self.attempt(lambda: core.export_m3u(path, self.rows))

    def play(self):
        def launch():
            if not any(core.enabled(row) for row in self.rows):
                raise ValueError('Open a CSV with at least one enabled channel first.')
            vlc = core.find_vlc() or filedialog.askopenfilename(title='Locate the VLC executable')
            if not vlc:
                return
            # Leave the temporary playlist in place: VLC may read it after this window closes.
            folder = Path(tempfile.mkdtemp(prefix='iptv-player-'))
            playlist = folder / 'playlist.m3u'
            core.export_m3u(playlist, self.rows)
            try:
                core.launch_vlc(vlc, playlist)
            except Exception:
                playlist.unlink(missing_ok=True)
                folder.rmdir()
                raise
            self.status.set('Opened enabled channels in VLC. Choose a channel in VLC’s playlist.')
        self.attempt(launch)

    def help(self):
        messagebox.showinfo('Getting started & usage',
            'Install Python 3.10+ with Tkinter and VLC. Run python3 iptv.py (Windows: py -3 iptv.py). '
            'Open a UTF-8 CSV using the header in channels.csv. Replace placeholder URLs with authorised stream URLs, '
            'set enabled=true, save, reopen it, then choose Open VLC. Use VLC’s playlist to choose a channel. '
            'Keep playlists with access tokens private; temporary playlists remain until system cleanup.\n\n' + core.DISCLAIMER)


if __name__ == '__main__':
    Player().mainloop()
