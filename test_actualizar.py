import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import actualizar

class Updates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / 'canales.m3u'
        self.output = patch.object(actualizar, 'OUTPUT', self.file)
        self.output.start()
        self.addCleanup(self.output.stop)
    def rows(self, count):
        return [{'nombre': f'Canal {i}', 'url': f'acestream://{i:040x}'} for i in range(1, count+1)]
    def previous(self, count=103):
        content=actualizar.render(actualizar.normalize(self.rows(count)))
        self.file.write_text(content)
        return self.file.read_bytes(), self.file.stat().st_mtime_ns
    def unchanged(self, before):
        self.assertEqual(before, (self.file.read_bytes(), self.file.stat().st_mtime_ns))
    def test_empty_extraction_keeps_valid_list_without_failure(self):
        before=self.previous()
        with patch.object(actualizar,'collect',return_value=[]): actualizar.main()
        self.unchanged(before)
    def test_unreachable_site_keeps_valid_list_without_failure(self):
        before=self.previous()
        with patch.object(actualizar,'collect',side_effect=actualizar.PlaywrightError('site unavailable')): actualizar.main()
        self.unchanged(before)
    def test_partial_extraction_keeps_previous_list(self):
        before=self.previous()
        with patch.object(actualizar,'collect',return_value=self.rows(12)): actualizar.main()
        self.unchanged(before)
    def test_equal_list_completes_without_rewriting(self):
        before=self.previous()
        with patch.object(actualizar,'collect',return_value=self.rows(103)): actualizar.main()
        self.unchanged(before)
    def test_new_valid_list_is_written(self):
        self.previous(12)
        with patch.object(actualizar,'collect',return_value=self.rows(13)): actualizar.main()
        self.assertEqual(13,actualizar.previous_count(self.file.read_text()))
    def test_no_valid_previous_list_still_fails(self):
        for content in ['', '\n'.join(f'acestream://{i:040x}' for i in range(20))]:
            self.file.write_text(content)
            with patch.object(actualizar,'collect',return_value=[]):
                with self.assertRaises(RuntimeError):actualizar.main()
    def test_unexpected_programming_failure_is_not_hidden(self):
        before=self.previous()
        with patch.object(actualizar,'collect',side_effect=NameError('bug')):
            with self.assertRaises(NameError):actualizar.main()
        self.unchanged(before)
if __name__=='__main__':unittest.main()
