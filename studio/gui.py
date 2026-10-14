import importlib.util
import tempfile
import threading
import sys
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from . import core

ROOT = Path(__file__).resolve().parent.parent
APP_NAME = 'IPTV Channel Player'
BRAND = 'TAVARC-Code'
VERSION = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f'{APP_NAME} {VERSION} | {BRAND}')
        self.geometry('1100x700')
        self.minsize(850, 550)
        self.configure(bg='#101827')
        self.rows, self.path, self.dirty = [], None, False
        self.results, self.busy = {}, False
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.icon = tk.PhotoImage(file=str(ROOT / 'assets' / 'icon.png'))
        self.iconphoto(True, self.icon)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('.', font=('Segoe UI', 10), background='#182338', foreground='#e8eef9')
        style.configure('TButton', padding=(12, 8))
        style.map('TButton', background=[('active', '#334b70')])
        style.configure('Treeview', background='#101827', fieldbackground='#101827', foreground='#e8eef9', rowheight=30)
        style.map('Treeview', background=[('selected', '#245fa0')])
        style.configure('Treeview.Heading', background='#24344e', padding=8)
        header = tk.Frame(self, bg='#101827', padx=22, pady=18)
        header.pack(fill='x')
        tk.Label(header, image=self.icon, bg='#101827').pack(side='left', padx=(0, 15))
        labels = tk.Frame(header, bg='#101827')
        labels.pack(side='left')
        tk.Label(labels, text='IPTV CHANNEL PLAYER', font=('Segoe UI', 23, 'bold'), fg='#f5f8ff', bg='#101827').pack(anchor='w')
        tk.Label(labels, text='TAVARC-Code  ·  Your channels, played through VLC.', fg='#c0dc55', bg='#101827', font=('Segoe UI', 11)).pack(anchor='w')
        toolbar = ttk.Frame(self, padding=(18, 8))
        toolbar.pack(fill='x')
        for label, action in [('New', self.new), ('Open CSV', self.open_csv), ('Save CSV', self.save),
                              ('Import M3U', self.import_list), ('Export M3U', self.export), ('Open VLC', self.play)]:
            ttk.Button(toolbar, text=label, command=action).pack(side='left', padx=3)
        controls = ttk.Frame(self, padding=(18, 10))
        controls.pack(fill='x')
        ttk.Label(controls, text='Search').pack(side='left', padx=(0, 8))
        self.search = tk.StringVar()
        self.search.trace_add('write', lambda *_: self.refresh())
        ttk.Entry(controls, textvariable=self.search, width=30).pack(side='left', padx=(0, 15))
        for label, action in [('Add', lambda: self.edit()), ('Edit', self.edit_selected), ('Delete', self.delete),
                              ('Check streams', self.check), ('Save report', self.report)]:
            ttk.Button(controls, text=label, command=action).pack(side='left', padx=3)
        area = ttk.Frame(self, padding=(18, 0))
        area.pack(fill='both', expand=True)
        columns = ('name', 'group', 'country', 'enabled', 'status')
        self.table = ttk.Treeview(area, columns=columns, show='headings', selectmode='extended')
        for key, width in [('name', 300), ('group', 160), ('country', 80), ('enabled', 80), ('status', 140)]:
            self.table.heading(key, text=key.title())
            self.table.column(key, width=width)
        scroll = ttk.Scrollbar(area, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.table.pack(fill='both', expand=True)
        self.table.bind('<Double-1>', lambda _: self.edit_selected())
        bottom = ttk.Frame(self, padding=(18, 12))
        bottom.pack(fill='x')
        self.status = tk.StringVar(value='Open a CSV or add your first channel.')
        ttk.Label(bottom, textvariable=self.status).pack(side='left')
        self.plugin_menu = tk.Menu(self, tearoff=False)
        menu = tk.Menu(self)
        menu.add_cascade(label='Plugins', menu=self.plugin_menu)
        menu.add_command(label='Getting started', command=self.help)
        menu.add_command(label='Usage & about', command=lambda: messagebox.showinfo('Usage & about', core.DISCLAIMER))
        self.config(menu=menu)
        self.load_plugins()
        # A new user should see the instructions before being handed an empty table.
        self.after(200, self.first_run)

    def first_run(self):
        import os
        if sys.platform == 'win32':
            base = Path(os.environ.get('LOCALAPPDATA', str(Path.home())))
        elif sys.platform == 'darwin':
            base = Path.home() / 'Library' / 'Application Support'
        else:
            base = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
        marker = base / 'TAVARC-Code' / 'IPTVChannelPlayer' / 'welcome-seen'
        if not marker.exists():
            self.help()
            try:
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.write_text('1', encoding='utf-8')
            except OSError:
                pass  # A read-only profile must not stop someone watching a channel.

    def help(self):
        dialog = tk.Toplevel(self)
        dialog.title('Getting started — TAVARC-Code')
        dialog.geometry('820x650')
        content = tk.Text(dialog, wrap='word', bg='#101827', fg='#e8eef9', padx=20, pady=20, font=('Segoe UI', 11))
        scroll = ttk.Scrollbar(dialog, command=content.yview)
        content.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        content.pack(fill='both', expand=True)
        # The same guide ships on disk and inside the app. One source means fewer surprises.
        try:
            guide_path = ROOT / 'SETUP.md'
            if not guide_path.exists():
                guide_path = ROOT / 'assets' / 'getting-started.md'
            guide = guide_path.read_text(encoding='utf-8')
        except OSError:
            guide = 'Open a CSV, add an authorised stream URL, enable it, save, then choose Open VLC.'
        content.insert('1.0', guide)
        content.configure(state='disabled')
        buttons = ttk.Frame(dialog, padding=10)
        buttons.pack(fill='x')
        ttk.Button(buttons, text='VLC download', command=lambda: webbrowser.open('https://www.videolan.org/vlc/')).pack(side='left')
        ttk.Button(buttons, text='Load example CSV', command=lambda: self.load_example()).pack(side='left', padx=8)
        ttk.Button(buttons, text='Close guide', command=dialog.destroy).pack(side='right')

    def load_example(self):
        if self.discard_ok():
            def load():
                self.rows = core.read_csv(ROOT / 'channels.csv')
                # Treat examples as a new document so Save asks for a personal filename.
                self.path, self.dirty, self.results = None, True, {}
                self.refresh()
                self.status.set('Examples are disabled placeholders. Replace their stream URLs before enabling.')
            self.guarded(load)

    def guarded(self, action):
        try:
            return action()
        except Exception as error:
            messagebox.showerror(APP_NAME, str(error))

    def refresh(self):
        selected = set(self.table.selection())
        self.table.delete(*self.table.get_children())
        query = self.search.get().lower()
        for i, row in enumerate(self.rows):
            if query in ' '.join(row.get(k, '') for k in ('name', 'group', 'country', 'language')).lower():
                self.table.insert('', 'end', iid=str(i), values=(row['name'], row['group'], row['country'], row['enabled'], self.results.get(row['id'], ('', ''))[0]))
                if str(i) in selected:
                    self.table.selection_add(str(i))
        self.title(f'{APP_NAME} {VERSION} | {BRAND} — {self.path.name if self.path else "Untitled"}{" *" if self.dirty else ""}')

    def discard_ok(self):
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel('Unsaved changes', 'Save your CSV before continuing?')
        return self.save() if answer else answer is False

    def new(self):
        if self.discard_ok():
            self.rows, self.path, self.dirty, self.results = [], None, False, {}
            self.refresh()

    def open_csv(self):
        if not self.discard_ok():
            return
        path = filedialog.askopenfilename(filetypes=[('CSV database', '*.csv')])
        if path:
            def load():
                rows = core.read_csv(path)
                self.rows, self.path, self.dirty, self.results = rows, Path(path), False, {}
                self.refresh()
                self.status.set(f'Loaded {len(rows)} channels.')
            self.guarded(load)

    def save(self):
        path = self.path or filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV database', '*.csv')])
        if not path:
            return False
        def write():
            core.write_csv(path, self.rows)
            self.path, self.dirty = Path(path), False
            self.refresh()
            self.status.set('CSV saved.')
            return True
        return bool(self.guarded(write))

    def import_list(self):
        if not self.discard_ok():
            return
        path = filedialog.askopenfilename(filetypes=[('M3U playlist', '*.m3u *.m3u8'), ('All files', '*')])
        if path:
            def load():
                self.rows = core.import_m3u(path)
                self.path, self.dirty, self.results = None, True, {}
                self.refresh()
                self.status.set('Imported as a new database; save to a new CSV for review.')
            self.guarded(load)

    def export(self):
        path = filedialog.asksaveasfilename(defaultextension='.m3u', filetypes=[('M3U playlist', '*.m3u')])
        if path:
            def write():
                core.export_m3u(path, self.rows)
                self.status.set('Exported enabled channels (all groups, regardless of search).')
            self.guarded(write)

    def play(self):
        def run():
            if not any(core.enabled(r) for r in self.rows):
                raise ValueError('Add or enable a channel first.')
            executable = core.find_vlc()
            if not executable:
                executable = filedialog.askopenfilename(title='Locate your VLC executable')
            if not executable:
                return
            folder = Path(tempfile.mkdtemp(prefix='playlist-studio-'))
            path = folder / 'playlist.m3u'
            core.export_m3u(path, self.rows)
            try:
                core.launch_vlc(executable, path)
            except Exception:
                path.unlink(missing_ok=True)
                folder.rmdir()
                raise
            self.status.set('Opened in VLC. Temporary playlist stays available until system temp cleanup.')
        self.guarded(run)

    def edit_selected(self):
        selected = self.table.selection()
        if selected:
            self.edit(int(selected[0]))

    def edit(self, index=None):
        row = self.rows[index].copy() if index is not None else dict.fromkeys(core.FIELDS, '')
        if index is None:
            import uuid
            row.update(id=uuid.uuid4().hex[:12], enabled='true')
        dialog = tk.Toplevel(self)
        dialog.title('Channel details')
        dialog.transient(self)
        dialog.grab_set()
        dialog.columnconfigure(1, weight=1)
        values = {}
        for i, key in enumerate(core.FIELDS):
            ttk.Label(dialog, text=key.replace('_', ' ').title()).grid(row=i, column=0, padx=15, pady=7, sticky='w')
            values[key] = tk.StringVar(value=row[key])
            entry = ttk.Combobox(dialog, textvariable=values[key], values=['true', 'false'], state='readonly') if key == 'enabled' else ttk.Entry(dialog, textvariable=values[key], width=65)
            entry.grid(row=i, column=1, padx=15, pady=7, sticky='ew')
        def apply():
            updated = {k: v.get().strip() for k, v in values.items()}
            candidate = [r.copy() for r in self.rows]
            if index is None:
                candidate.append(updated)
            else:
                candidate[index] = updated
            def commit():
                core.validate(candidate)
                self.rows, self.dirty = candidate, True
                self.results.pop(row['id'], None)
                self.refresh()
                dialog.destroy()
            self.guarded(commit)
        ttk.Button(dialog, text='Save channel', command=apply).grid(row=len(core.FIELDS), column=1, sticky='e', padx=15, pady=15)

    def delete(self):
        indices = sorted((int(i) for i in self.table.selection()), reverse=True)
        if indices and messagebox.askyesno('Delete channels', f'Delete {len(indices)} selected channels?'):
            for i in indices:
                self.results.pop(self.rows[i]['id'], None)
                del self.rows[i]
            self.dirty = True
            self.refresh()

    def check(self):
        if self.busy:
            return
        snapshot = [r.copy() for r in self.rows if core.enabled(r)]
        if not snapshot:
            self.status.set('No enabled channels to check.')
            return
        self.busy = True
        self.status.set(f'Checking {len(snapshot)} enabled streams…')
        # Worker only writes to a queue; all Tk calls stay on the main thread.
        import queue
        messages = queue.Queue()
        def worker():
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=4) as pool:
                for row, result in zip(snapshot, pool.map(core.check_stream, snapshot)):
                    messages.put((row, result))
            messages.put(None)
        def poll():
            while not messages.empty():
                item = messages.get()
                if item is None:
                    self.busy = False
                    self.status.set('Checks complete. Reachable does not guarantee playback.')
                    return
                row, result = item
                if any(r['id'] == row['id'] and r['stream_url'] == row['stream_url'] for r in self.rows):
                    self.results[row['id']] = result
                    self.refresh()
            self.after(100, poll)
        threading.Thread(target=worker, daemon=True).start()
        self.after(100, poll)

    def report(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV report', '*.csv')])
        if path:
            def write(f):
                import csv
                writer = csv.writer(f)
                writer.writerow(['id', 'name', 'status', 'detail'])
                for row in self.rows:
                    writer.writerow([row['id'], row['name'], *self.results.get(row['id'], ('NOT CHECKED', ''))])
            self.guarded(lambda: core.atomic_write(path, write))

    def load_plugins(self):
        # Explicit opt-in: local plugins are executable Python code.
        self.plugin_menu.add_command(label='Load local plugins…', command=self.enable_plugins)

    def enable_plugins(self):
        if not messagebox.askyesno('Load trusted plugins', 'Plugins run Python code with your account permissions. Load trusted .py files from the plugins folder?'):
            return
        for path in sorted((ROOT / 'plugins').glob('*.py')):
            if path.name.startswith('_'):
                continue
            def load(path=path):
                spec = importlib.util.spec_from_file_location('playlist_plugin_' + path.stem, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.register(self)
            self.guarded(load)
        self.plugin_menu.entryconfig(0, state='disabled')

    def close(self):
        if self.discard_ok():
            self.destroy()


def run():
    App().mainloop()
