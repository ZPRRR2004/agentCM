"""Byte-integrity checks for importing original upstream task packages."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('dataset_download', Path(__file__).parents[1] / 'download.py')
download = importlib.util.module_from_spec(spec)
spec.loader.exec_module(download)


class OriginalDatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        task = self.root / 'tasks/example-task'
        task.mkdir(parents=True)
        (task / 'instruction.md').write_text('Original task instruction.\n')
        (task / 'task.toml').write_text('schema_version = "1.0"\n')
        for name in ('environment', 'solution', 'tests'):
            (task / name).mkdir()
            (task / name / 'original.txt').write_bytes(b'Original binary\x00payload')
        self.entries = []
        for path in self.root.rglob('*'):
            if path.is_file():
                data = path.read_bytes()
                digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                self.entries.append({'path': path.relative_to(self.root).as_posix(), 'git_blob_sha1': digest})

    def tearDown(self):
        self.temp.cleanup()

    def test_original_bytes_and_task_count_match(self):
        self.assertEqual(len(download.validate(self.root, self.entries, 1)), 1)
        with self.assertRaisesRegex(ValueError, 'Expected 89'):
            download.validate(self.root, self.entries, 89)

    def test_modified_or_missing_original_file_fails(self):
        path = self.root / 'tasks/example-task/instruction.md'
        path.write_text('Locally changed content.')
        with self.assertRaisesRegex(ValueError, 'Upstream byte mismatch'):
            download.validate(self.root, self.entries, 1)
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'inventory mismatch'):
            download.validate(self.root, self.entries, 1)

    def test_extra_local_file_is_not_upstream_content(self):
        (self.root / 'extra-file.txt').write_text('Extra local data')
        with self.assertRaisesRegex(ValueError, 'inventory mismatch'):
            download.validate(self.root, self.entries, 1)


if __name__ == '__main__':
    unittest.main()
