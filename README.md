# IPTV Channel Player

![TAVARC-Code icon](assets/icon-large.png)

**TAVARC-Code — a small desktop companion for playing IPTV channels through VLC.**

I wanted channel lists to be easy to keep and easy to change. This app uses an ordinary CSV file for the database, exports an M3U playlist, and hands playback to VLC. You can edit the same database in Excel or LibreOffice if you prefer. Nobody needs another mysterious file format merely to rename a television channel.

Start with [the complete beginner’s guide](SETUP.md). It covers extracting the download, installing Python and VLC, adding your first channel, and fixing the usual setup problems. The identical guide is available inside the app under **Getting started**, and opens on first launch.

## What it does

- Adds, edits, searches and deletes channel records.
- Keeps names, groups, countries, languages, logos and programme-guide identifiers in CSV.
- Imports ordinary M3U/M3U8 playlists into a new database for review.
- Exports enabled channels and opens the playlist in VLC.
- Checks HTTP stream reachability without downloading a whole programme.
- Saves a separate report and supports small, trusted Python plugins.

This is a standalone Python application, rather than an extension installed inside VLC. Video opens in VLC’s own window. Windows, macOS and Linux launchers are supplied; mobile IPTV apps can use exported playlists, but the desktop editor does not run as an Android or iOS app.

## Requirements and first launch

You need Python 3.10 or newer with Tkinter, VLC, and a desktop session. Normal use has no pip dependencies. Your channel provider must supply URLs you can actually play; a broadcaster’s website address usually will not do.

Extract the entire ZIP into a folder you can write to. On Windows, double-click **Launch Windows.bat**. On macOS, use **Launch macOS.command**. On Linux, run `./launch-linux.sh`. The launchers check Python and Tkinter before opening the editor. If Python is missing on Windows or macOS, they point you to the official download. They do not silently install system software.

[SETUP.md](SETUP.md) gives the exact steps for each operating system. Read that if any of the previous paragraph sounded like homework.

## Your database

The supplied `channels.csv` contains four **disabled examples**. They are deliberately fictional: no working subscriptions or channel feeds come with the app. Load it from **Getting started → Load example CSV**, replace the example URLs, and save your own copy.

```csv
id,name,group,country,language,stream_url,logo_url,tvg_id,enabled
my-news,My News,News,GB,en,https://example.org/live.m3u8,,,false
```

That address is a placeholder. Use a real URL from your authorised provider before enabling the row.

| Column | What to put there |
| --- | --- |
| `id` | A unique, stable label for the record |
| `name` | The channel name shown in your playlist |
| `group` | News, Films, Cartoons, UK TV, or your own category |
| `country` | Optional country code, such as GB |
| `language` | Optional language code, such as en |
| `stream_url` | The playable stream URL, including its scheme |
| `logo_url` | Optional channel logo URL |
| `tvg_id` | Optional identifier matching an external XMLTV guide |
| `enabled` | true to export the channel; false to leave it out |

Keep the header. Use UTF-8 CSV and quote values containing commas. The app also accepts yes/no and 1/0 for enabled. Names, IDs and URLs are required; metadata can be blank. Guide identifiers are exported, but this version does not download or display TV schedules.

Save before switching to a spreadsheet, then reopen the CSV in the app afterwards. One writer at a time. Normal saves replace the selected file using an atomic write, while M3U imports start a new unsaved database instead of guessing how to merge your existing records. Export always includes all enabled channels, even if the search box hides some of them.

## Stream checks, honestly

**Reachable** means the server returned some data. It does not mean the video will play. A login page, a missing HLS segment, a regional restriction or a codec problem can still ruin the evening.

Checks support HTTP and HTTPS, follow redirects, use four workers and read at most 1 KB from each response. The socket timeout is eight seconds; a slow response can take longer overall. Some providers reject a generic client or Range request, so a failed check is a reason to investigate rather than proof that the channel is dead. Other schemes, including RTSP, remain in the playlist and are marked untested.

Ordinary EXTINF attributes and EXTGRP groups are imported. Provider-specific headers, DRM settings and directives are not preserved. The app does not bypass those requirements.

## Optional command line

```sh
python3 iptv.py export channels.csv --output playlist.m3u
python3 iptv.py import incoming.m3u --output imported.csv
python3 iptv.py check channels.csv --output stream-report.csv
```

On Windows, use `py -3` instead of `python3`. Choose a new output filename if you need to keep the original: CLI output paths are overwritten.

## Writing a small plugin

Place a trusted `.py` file in `plugins/` and define `register(app)`. Load it through **Plugins → Load local plugins**. The included `channel_summary.py` adds a group-count menu action and is a useful starting point.

The app exposes `app.rows`, `app.path`, `app.results`, `app.plugin_menu` and `app.refresh()`. Validate changed rows with `studio.core.validate`, set `app.dirty = True`, then refresh the table. Keep Tk calls on the main thread. Plugins are ordinary executable Python code with your account’s permissions; load code you trust. They load once per session.

## Building a desktop app for distribution

The ZIP supplied here is the ready-to-run **source package**, with setup launchers. Python and VLC must still be installed. To build a version that includes Python, run the following on each target operating system:

```sh
python3 -m pip install pyinstaller
python3 build_app.py
```

The builder includes the icon, example database and documentation. It creates `dist/IPTVChannelPlayer/` on Windows/Linux, and an app bundle on macOS. Distribute the whole generated folder or bundle. VLC remains a separate installation. Build on Windows for Windows, macOS for macOS, and Linux for Linux; architecture and OS compatibility still need testing. These builds are unsigned and have not been produced or tested in this release.

## Development and checks

```sh
python3 -m unittest discover -s tests -v
```

The tests cover CSV/M3U round trips, metadata, invalid rows, failed saves, bounded stream reads, private URL redaction and the VLC launch arguments. Desktop layout and actual playback require a graphical machine with VLC. Windows and macOS launchers have not been run in this Linux development environment.

## Usage notice

Do not misuse this software. Use it only to access IPTV channels and streams you are authorised to watch. Do not use it to access or redistribute content unlawfully. You are responsible for complying with applicable laws, provider terms, and licensing requirements, including a UK TV Licence where required. Stream availability and playback are not guaranteed. Keep playlists containing passwords or access tokens private. This independent software is not affiliated with VideoLAN or any broadcaster.

Open VLC writes the exported playlist to a private temporary folder so VLC can keep reading it. The folder remains until system temporary-file cleanup; remove it yourself afterwards if the playlist contains credentials. Reports omit stream URLs and raw exception messages, but still include channel names and IDs. Review unfamiliar CSV files before opening them in spreadsheet software, which may interpret formula-like text.

## Licence and branding

The source code is available under the [MIT licence](LICENSE). The supplied TAVARC-Code artwork is treated separately; see [BRANDING.md](BRANDING.md). A code licence does not give anyone rights to the channels in their playlist.
