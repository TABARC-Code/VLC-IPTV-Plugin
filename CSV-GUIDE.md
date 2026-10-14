# Setting up your channel CSV

IPTV Channel Player · TAVARC-Code

The CSV is your database. Keep a copy somewhere sensible and make a backup before changing a large list. You can edit it in the app, Excel or LibreOffice; the app reads the same file, without a separate database server.

## Start with the supplied file

Copy channels.csv to my-channels.csv in Documents. Its rows are disabled examples. Replace the addresses with actual streams you are authorised to watch. They are not viewing-page links and the example.org addresses will not play.

Use this exact header, in this order:

```csv
id,name,group,country,language,stream_url,logo_url,tvg_id,enabled
```

A disabled example with commas in the channel name looks like this:

```csv
news-01,"News, International",News,GB,en,https://example.org/live.m3u8,,,false
```

The quotation marks keep the comma inside the name instead of creating another column. Three commas after the URL leave logo_url and tvg_id blank before false.

## What each column means

| Column | Required? | Example or rule |
| --- | --- | --- |
| id | Yes | news-01; unique and stable within this file |
| name | Yes | The channel label viewers see |
| group | No | News, Films, Cartoons, UK TV or any category you choose |
| country | No | GB, or another country code |
| language | No | en, or another language code |
| stream_url | Yes | Complete playable URL including https://, rtsp:// or another scheme |
| logo_url | No | URL of a channel logo |
| tvg_id | No | Exact channel identifier used by an external XMLTV guide |
| enabled | Yes | true or false; yes/no and 1/0 are also accepted |

The app does not fetch an XMLTV guide or download logos into the editor. It exports the relevant metadata for players that use it. Blank optional cells are fine. Embedded line breaks are not.

## Save from a spreadsheet

In Excel, choose Save As and select CSV UTF-8 (Comma delimited). In LibreOffice, save as Text CSV with UTF-8 and a comma separator. Keep the first row as the column names. Do not save an .xlsx workbook and simply rename it .csv; a new suffix does not change its contents.

Save the app first, then edit externally and reopen the CSV afterwards. Avoid changing the same file in two programs at once. If the spreadsheet asks whether to keep its current format, keep the CSV format.

## Organise a growing list

Use a separate record for each stream variant. A second quality level or regional feed should have its own ID. Reusing the same ID is rejected, even if the name is different. Similar URLs are not automatically merged: it is better to leave that decision with the person maintaining the list.

Set enabled=false to retain a channel without exporting it. Search affects the visible table, not what Export M3U or Open VLC includes. All enabled rows are used.

## Private data and common errors

A stream URL may contain a password or access token. Keep that file and its M3U export private, and never commit a personal channel database to a public repository. The included .gitignore excludes my-channels.csv, but other filenames still need checking.

Missing CSV columns means the header was changed or the separator is wrong. Duplicate id means two rows share an identifier. Wrong number of columns normally points to an unquoted comma. Save as UTF-8 CSV and reopen after correcting it.

When importing an M3U, save the resulting CSV under a fresh name. Provider-specific request headers and DRM directives are not preserved. Use the supported provider player if those details are essential.

## Usage notice

Do not misuse this software. Use it only to access IPTV channels and streams you are authorised to watch. Do not use it to access or redistribute content unlawfully. You are responsible for complying with applicable laws, provider terms, and licensing requirements, including a UK TV Licence where required. Stream availability and playback are not guaranteed. Keep playlists containing passwords or access tokens private. This independent software is not affiliated with VideoLAN or any broadcaster.
