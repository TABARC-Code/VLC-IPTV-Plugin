# IPTV Channel Player — the complete beginner’s guide

TAVARC-Code

You do not need to know Python. You need to install two ordinary programs once, extract this folder, and add a channel URL. Keep this guide open while you do it.

## 1. Extract the download

Download the ZIP. On Windows, right-click it and choose Extract All. On macOS, double-click the ZIP in Finder. On Linux, use your file manager’s Extract option.

Put the extracted folder somewhere you can find again, such as Documents. Keep its files together: iptv.py, studio, assets and the rest belong in the same folder. Do not run a launcher from inside the ZIP preview.

## 2. Install Python and VLC

Windows:

1. Visit https://www.python.org/downloads/ and download Python 3.10 or newer for Windows. Use the standard Python installer, with Tcl/Tk and the Python launcher included. If offered, select Add Python to PATH.
2. Install VLC from https://www.videolan.org/vlc/ using the usual installer options.
3. Open the extracted app folder and double-click Launch Windows.bat. If Python is not found, it opens the Python download page and explains what is missing. After installing, run the launcher again.

macOS:

1. Install Python 3.10 or newer from https://www.python.org/downloads/macos/. The python.org package includes Tk support. If its folder contains Install Certificates.command, run that once for HTTPS certificate support.
2. Install VLC from https://www.videolan.org/vlc/ and move VLC into Applications.
3. Double-click Launch macOS.command in the extracted folder. If it cannot run, open Terminal, type cd followed by a space, drag the extracted app folder into Terminal, and press Return. Then type python3 setup_app.py and press Return.

Linux:

1. Open Terminal. On Ubuntu or Debian, install the requirements with: sudo apt install python3 python3-tk vlc
2. On Fedora, use: sudo dnf install python3 python3-tkinter. Install VLC using your distribution’s available software sources.
3. Open a terminal in the extracted folder and run: python3 setup_app.py
4. You can also run ./launch-linux.sh. If permissions were lost during extraction, use chmod +x launch-linux.sh first.

There are no pip packages to install for normal use. The optional app builder is for people preparing executable releases, not a step you need to watch a channel.

## 3. Read the welcome screen

The app opens a Getting started guide on first launch. This is that same guide. Close it when you are ready; reopen it any time from the menu.

The title should say IPTV Channel Player, with TAVARC-Code underneath. Video will open in VLC’s own window.

## 4. Add your first channel

1. Choose Add in the main window.
2. Leave the generated ID alone. Enter a channel name and a group, such as News.
3. Paste an actual stream URL from a provider you are authorised to use into Stream URL. Do not paste the address of a normal webpage. HTTP streams often end in .m3u8, but that ending is not compulsory.
4. Leave Country, Language, Logo URL and TVG ID blank if you do not have them.
5. Set Enabled to true, then choose Save channel.
6. Choose Save CSV. Save it in Documents with a name such as my-channels.csv.
7. Choose Open VLC. If the app cannot find VLC, it asks you to locate its executable. On Windows this is normally C:\Program Files\VideoLAN\VLC\vlc.exe; on macOS, /Applications/VLC.app/Contents/MacOS/VLC. On Linux it is often /usr/bin/vlc.

The button opens a playlist of all enabled channels. In VLC, use View → Playlist, or its playlist button, to choose a channel. Playback controls, volume and full-screen viewing are handled by VLC.

No feeds are supplied. The example CSV has disabled placeholder URLs, so it will not play until you replace them.

## 5. Start from a list you already have

For a CSV created by this app, choose Open CSV.

For an ordinary M3U or M3U8 playlist, choose Import M3U. This makes a new database in the app; it does not edit the original playlist. Check the imported records, then Save CSV under your own filename. Special provider headers and DRM settings are not imported, so some lists need the provider’s supported player instead.

The Load example CSV button in this guide gives you four sample categories. Replace their URLs and enable only the channels you want.

## 6. Maintain the database

Select a row and choose Edit, or double-click it. Delete removes selected rows after asking. Enabled=false keeps a channel in your database while leaving it out of exports. Search looks through names, groups, countries and languages.

Save before closing. You will be asked about unsaved changes.

If you prefer Excel or LibreOffice, save the app’s CSV, close or leave the editor idle, and open the file in your spreadsheet program. Keep the column names and save as UTF-8 CSV. Reopen it in the app afterwards. Do not edit the same file in two places at once; neither program can read your mind.

## 7. Export for another IPTV app

Choose Export M3U and save a playlist.m3u file. Import that file into your other IPTV app using its local playlist option. Menus differ between apps; this software does not publish or host a playlist URL.

All enabled records are exported, regardless of the current search. Keep any playlist containing passwords or access tokens private.

## 8. Check a channel that will not play

Choose Check streams, then wait for the status message to finish. You can keep using the window while the checks run. Save report writes a separate CSV without stream URLs.

REACHABLE: some data arrived; playback still needs testing in VLC.
WEB PAGE: the address seems to return HTML, often a login page or viewing website.
FAILED: check the URL, connection and provider requirements. Generic checks can fail on otherwise valid streams.
UNTESTED: the URL uses a scheme other than HTTP or HTTPS; try it in VLC.
EMPTY: the server returned no data.

A check is a clue, not a guarantee. Test the same URL using VLC’s Media → Open Network Stream (File → Open Network on some macOS versions). If VLC cannot play it directly either, check with your provider.

## Common setup problems

Nothing happens on Windows: run Launch Windows.bat, not iptv.py. Read the message in the console. If it says Python is missing, install Python, then close and reopen the launcher.

No module named tkinter: reinstall python.org Python with Tcl/Tk on Windows/macOS; on Linux install the Tkinter package listed above.

A desktop window could not open: run from a normal desktop session. A server or SSH terminal without a display can use the command line tools but cannot show the editor.

VLC is not found: install VLC, restart this app, or select the VLC executable when prompted. Choose the program, not a shortcut or a playlist file.

The ZIP or launcher is blocked: use the source launcher after reviewing the files. Do not switch off system security checks merely to run an unfamiliar download. No signed Windows or macOS installer is included here.

A macOS launcher says permission denied: use the Terminal method in step 2. Alternatively run chmod +x followed by the quoted launcher filename.

The channel asks for credentials or special headers: follow your provider’s instructions. This version does not add custom request headers or bypass DRM.

## Optional plugins

The supplied channel summary plugin can be loaded through Plugins → Load local plugins. It counts channels by group. Plugins run Python code with your account’s permissions, so use trusted files. This feature is optional; playback and CSV editing work without it.

## Usage notice

Do not misuse this software. Use it only to access IPTV channels and streams you are authorised to watch. Do not use it to access or redistribute content unlawfully. You are responsible for complying with applicable laws, provider terms, and licensing requirements, including a UK TV Licence where required. Stream availability and playback are not guaranteed. Keep playlists containing passwords or access tokens private. This independent software is not affiliated with VideoLAN or any broadcaster.

Keep a backup of your own CSV. The app’s examples are replaceable; your carefully maintained list probably is not.
