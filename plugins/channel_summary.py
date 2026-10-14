"""TAVARC-Code example plugin: count channels without changing the database.

Put trusted plugins in this folder and load them from Plugins in the app.
The Getting started menu contains the same SETUP.md guide shipped with the download."""
from collections import Counter
from tkinter import messagebox


def register(app):
    # Read the live rows when clicked, so edits made after loading are included.
    def summary():
        counts = Counter(row['group'] or 'Ungrouped' for row in app.rows)
        messagebox.showinfo('Channel summary', '\n'.join(f'{name}: {count}' for name, count in sorted(counts.items())) or 'No channels yet.')
    app.plugin_menu.add_command(label='Channel summary', command=summary)
