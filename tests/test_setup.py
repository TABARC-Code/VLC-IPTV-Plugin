"""Setup failures should give a useful next step, not a wall of traceback."""
import unittest
from unittest.mock import patch
import setup_app
import build_app


class SetupTests(unittest.TestCase):
    def test_old_python_has_download_instruction(self):
        with patch('setup_app.sys.version_info', (3, 9)), patch('builtins.print') as output:
            self.assertEqual(setup_app.main(), 1)
        self.assertTrue(any('python.org' in str(call) for call in output.call_args_list))

    def test_headless_display_has_clear_message(self):
        with patch('tkinter.Tk', side_effect=RuntimeError('no display')), patch('builtins.print') as output:
            self.assertEqual(setup_app.main(), 1)
        self.assertTrue(any('desktop session' in str(call) for call in output.call_args_list))

    def test_builder_preserves_asset_folder_and_includes_guide(self):
        with patch('build_app.importlib.util.find_spec', return_value=object()), patch('build_app.subprocess.call', return_value=0) as build:
            self.assertEqual(build_app.main(), 0)
        args = build.call_args.args[0]
        self.assertTrue(any('assets:assets' in arg or 'assets;assets' in arg for arg in args))
        self.assertTrue(any('SETUP.md' in arg for arg in args))


if __name__ == '__main__':
    unittest.main()
