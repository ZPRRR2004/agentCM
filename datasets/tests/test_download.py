"""Byte-integrity checks for importing original upstream task packages."""
import hashlib
import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

spec = importlib.util.spec_from_file_location('dataset_download', Path(__file__).parents[1] / 'download.py')
download = importlib.util.module_from_spec(spec)
spec.loader.exec_module(download)


class OriginalDatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        task = self.root / 'tasks/example-task'
        task.mkdir(parents=True)
        (task / 'instruction.md').write_text('Original task instruction: 处理数据 🚀.\n', encoding='utf-8')
        (task / 'task.toml').write_text('schema_version = "1.0"\n', encoding='utf-8')
        (task / '说明.txt').write_text('原版附属文件。\n', encoding='utf-8')
        for name in ('environment', 'solution', 'tests'):
            (task / name).mkdir()
            (task / name / 'original.txt').write_bytes(b'Original binary\x00payload')
        self.entries = []
        for path in self.root.rglob('*'):
            if path.is_file():
                data = path.read_bytes()
                digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                self.entries.append({'path': path.relative_to(self.root).as_posix(),
                                     'git_blob_sha1': digest, 'size': len(data), 'mode': '100644'})

    def tearDown(self):
        self.temp.cleanup()

    def dataset(self):
        return {'id': 'example', 'source_path': 'example/source',
                'manifest_path': 'example/source-manifest.json', 'expected_tasks': 1,
                'source': {'repository': 'https://github.com/example/tasks', 'commit': 'a' * 40}}

    def archive(self):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode='w:gz') as package:
            for entry in self.entries:
                data = (self.root / entry['path']).read_bytes()
                member = tarfile.TarInfo('official/' + entry['path'])
                member.size = len(data)
                member.mode = 0o644
                package.addfile(member, io.BytesIO(data))
        return output.getvalue()

    def save_manifest(self, archive):
        dataset = self.dataset()
        path = self.root / dataset['manifest_path']
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {'repository': dataset['source']['repository'], 'commit': 'a' * 40,
                    'task_count': 1, 'files': self.entries,
                    'archive_sha256': hashlib.sha256(archive).hexdigest(),
                    'note': '保留原始来源清单 🚀'}
        path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
        return path

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

    def test_main_reads_utf8_catalog_under_the_system_locale(self):
        dataset = self.dataset()
        catalog = {'datasets': [dict(dataset, description='官方任务 🚀')]}
        (self.root / 'catalog.json').write_bytes(json.dumps(catalog, ensure_ascii=False).encode('utf-8'))
        with mock.patch.object(download, 'ROOT', self.root), \
                mock.patch.object(download, 'download') as importer, \
                mock.patch('sys.argv', ['download.py', '--dataset', 'example']):
            download.main()
        importer.assert_called_once_with(catalog['datasets'][0], False)

    def test_restore_from_saved_manifest_preserves_its_bytes(self):
        archive = self.archive()
        path = self.save_manifest(archive)
        original = path.read_bytes()
        dataset = self.dataset()
        with mock.patch.object(download, 'ROOT', self.root), \
                mock.patch.object(download, 'request', return_value=io.BytesIO(archive)) as request:
            download.download(dataset)
            download.download(dataset, verify_only=True)
        request.assert_called_once_with('https://codeload.github.com/example/tasks/tar.gz/' + 'a' * 40)
        self.assertEqual(path.read_bytes(), original)
        source = self.root / dataset['source_path']
        self.assertEqual((source / 'tasks/example-task/instruction.md').read_bytes(),
                         (self.root / 'tasks/example-task/instruction.md').read_bytes())

    def test_new_import_downloads_inventory_and_writes_utf8_manifest(self):
        archive = self.archive()
        tree = {'tree': [{'type': 'blob', 'path': e['path'], 'size': e['size'],
                          'sha': e['git_blob_sha1'], 'mode': e['mode']} for e in self.entries]}
        responses = [io.BytesIO(json.dumps(tree).encode('utf-8')), io.BytesIO(archive)]
        with mock.patch.object(download, 'ROOT', self.root), \
                mock.patch.object(download, 'request', side_effect=responses):
            download.download(self.dataset())
        raw = (self.root / self.dataset()['manifest_path']).read_bytes()
        manifest = json.loads(raw.decode('utf-8'))
        self.assertEqual(manifest['task_count'], 1)
        self.assertIn('tasks/example-task/说明.txt', [e['path'] for e in manifest['files']])
        self.assertNotIn(b'\r\n', raw)

    def test_saved_manifest_rejects_a_changed_archive(self):
        archive = self.archive()
        path = self.save_manifest(archive)
        original = path.read_bytes()
        with mock.patch.object(download, 'ROOT', self.root), \
                mock.patch.object(download, 'request', return_value=io.BytesIO(archive + b'changed')):
            with self.assertRaisesRegex(ValueError, 'Archive SHA-256'):
                download.download(self.dataset())
        self.assertFalse((self.root / self.dataset()['source_path']).exists())
        self.assertEqual(path.read_bytes(), original)

    def test_catalog_commit_mismatch_is_rejected_before_download(self):
        self.save_manifest(self.archive())
        dataset = self.dataset()
        dataset['source']['commit'] = 'b' * 40
        with mock.patch.object(download, 'ROOT', self.root), \
                mock.patch.object(download, 'request') as request:
            with self.assertRaisesRegex(ValueError, 'Manifest commit'):
                download.download(dataset)
        request.assert_not_called()

    def test_archive_extraction_rejects_traversal_and_links(self):
        for name, kind in [('../escape.txt', tarfile.REGTYPE), ('official/link', tarfile.SYMTYPE)]:
            with self.subTest(name=name):
                raw = io.BytesIO()
                with tarfile.open(fileobj=raw, mode='w') as package:
                    member = tarfile.TarInfo(name)
                    member.type = kind
                    member.linkname = '../../escape.txt' if kind == tarfile.SYMTYPE else ''
                    member.size = 1 if kind == tarfile.REGTYPE else 0
                    package.addfile(member, io.BytesIO(b'x') if member.size else None)
                raw.seek(0)
                with tarfile.open(fileobj=raw) as package:
                    with self.assertRaisesRegex(ValueError, 'Archive'):
                        download.extract_archive(package, self.root / 'unpacked')
                self.assertFalse((self.root / 'escape.txt').exists())


if __name__ == '__main__':
    unittest.main()
