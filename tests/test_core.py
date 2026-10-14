import tempfile
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from studio import core


def channel(**changes):
    row = dict.fromkeys(core.FIELDS, '')
    row.update(id='one', name='News, International', group='News', stream_url='https://example.org/live.m3u8?token=a&b=c', enabled='true')
    row.update(changes)
    return row


class PlaylistTests(unittest.TestCase):
    def test_csv_and_m3u_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            csv_path, m3u_path = Path(folder) / 'channels.csv', Path(folder) / 'list.m3u'
            rows = [channel(), channel(id='two', name='Disabled', enabled='false')]
            core.write_csv(csv_path, rows)
            self.assertEqual(core.read_csv(csv_path), rows)
            core.export_m3u(m3u_path, rows)
            imported = core.import_m3u(m3u_path)
            self.assertEqual(len(imported), 1)
            self.assertEqual(imported[0]['name'], rows[0]['name'])
            self.assertEqual(imported[0]['stream_url'], rows[0]['stream_url'])
            self.assertEqual(imported[0]['group'], 'News')

    def test_quoted_comma_attribute(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.m3u'
            path.write_text('#EXTM3U\n#EXTINF:-1 group-title="News, World",Channel\nhttps://example.org/live\n')
            self.assertEqual(core.import_m3u(path)[0]['group'], 'News, World')

    def test_reject_injection_duplicate_and_invalid_boolean(self):
        for rows in ([channel(name='Name\n#EXTINF:bad')], [channel(), channel()], [channel(enabled='maybe')]):
            with self.assertRaises(ValueError):
                core.validate(rows)

    def test_all_content_groups_retained(self):
        rows = [channel(id=str(i), group=g) for i, g in enumerate(['News', 'Films', 'Cartoons', 'UK TV', 'User custom'])]
        result = core.m3u_text(rows)
        for row in rows:
            self.assertIn('group-title="' + row['group'] + '"', result)

    def test_failed_write_preserves_database(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'data.csv'
            path.write_text('original')
            def broken(f):
                f.write('partial')
                raise RuntimeError('failure')
            with self.assertRaises(RuntimeError):
                core.atomic_write(path, broken)
            self.assertEqual(path.read_text(), 'original')

    def test_non_http_check_is_untested(self):
        self.assertEqual(core.check_stream(channel(stream_url='rtsp://example.org/live'))[0], 'UNTESTED')

    def test_check_reads_bounded_prefix_and_flags_html(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.headers = {'Content-Type': 'text/html'}
        response.read.return_value = b'<html>Sign in</html>'
        with patch('studio.core.urlopen', return_value=response):
            self.assertEqual(core.check_stream(channel())[0], 'WEB PAGE')
        response.read.assert_called_once_with(1024)

    def test_check_redacts_private_url_from_errors(self):
        with patch('studio.core.urlopen', side_effect=OSError('https://example.org/?secret=private')):
            status, detail = core.check_stream(channel())
        self.assertEqual(status, 'FAILED')
        self.assertNotIn('private', detail)

    def test_vlc_launch_passes_url_as_file_without_shell(self):
        with patch('studio.core.subprocess.Popen') as launch:
            core.launch_vlc('/opt/VLC player/vlc', '/tmp/my playlist.m3u')
        launch.assert_called_once_with(['/opt/VLC player/vlc', '--', '/tmp/my playlist.m3u'], shell=False)


if __name__ == '__main__':
    unittest.main()
