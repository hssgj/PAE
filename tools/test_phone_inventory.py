import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('phone_inventory', Path(__file__).with_name('phone_inventory.py'))
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class PhoneInventoryTests(unittest.TestCase):
    def test_profile_metadata_and_opt_in_source_exclude_other_json(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'PAE'
            (root / 'prototype_v0/data/sessions').mkdir(parents=True)
            config = root / 'config'
            config.mkdir()
            data = b'{"profiles":{"echo":{"provider":"echo"}}}\n'
            (config / 'model_profiles.json').write_bytes(data)
            (config / 'private.json').write_text('{"private":"configuration"}')
            (root / 'prototype_v0/private.json').write_text('{"private":"other"}')
            (root / 'prototype_v0/data/sessions/private.json').write_text('{"private":"conversation"}')
            for include_source in (False, True):
                with self.subTest(include_source=include_source):
                    output = Path(temp) / ('source.zip' if include_source else 'metadata.zip')
                    report = inventory.collect(root, output, include_source=include_source)
                    self.assertEqual(report['files'], [{
                        'path': 'config/model_profiles.json',
                        'bytes': len(data),
                        'sha256': hashlib.sha256(data).hexdigest(),
                        'source_included': include_source,
                    }])
                    with zipfile.ZipFile(output) as archive:
                        expected = {'inventory.json'}
                        if include_source:
                            expected.add('source/config/model_profiles.json')
                            self.assertEqual(archive.read('source/config/model_profiles.json'), data)
                        self.assertEqual(set(archive.namelist()), expected)
                        self.assertEqual(json.loads(archive.read('inventory.json')), report)
                        self.assertIsNone(archive.testzip())

    def test_profile_with_embedded_credential_has_no_exported_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'PAE'
            (root / 'prototype_v0').mkdir(parents=True)
            (root / 'config').mkdir()
            (root / 'config/model_profiles.json').write_text(json.dumps({'api_key': 'gsk_' + 'x' * 30}))
            output = Path(temp) / 'snapshot.zip'
            report = inventory.collect(root, output, include_source=True)
            self.assertEqual(len(report['files']), 1)
            self.assertFalse(report['files'][0]['source_included'])
            self.assertEqual(report['excluded'], [{
                'path': 'config/model_profiles.json',
                'reason': 'possible embedded credential; source omitted',
            }])
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.namelist(), ['inventory.json'])

    def test_symlinked_profile_is_excluded(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'PAE'
            (root / 'prototype_v0').mkdir(parents=True)
            (root / 'config').mkdir()
            private = Path(temp) / 'private.json'
            private.write_text('{"private":"outside checkout"}')
            (root / 'config/model_profiles.json').symlink_to(private)
            output = Path(temp) / 'snapshot.zip'
            report = inventory.collect(root, output, include_source=True)
            self.assertEqual(report['files'], [])
            self.assertEqual(report['excluded'], [{'path': 'config/model_profiles.json', 'reason': 'symlink'}])
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.namelist(), ['inventory.json'])

    def test_source_inventory_excludes_sessions_credentials_and_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'PAE'
            code = root / 'prototype_v0'
            code.mkdir(parents=True)
            (code / 'app.py').write_text('print("safe")\n')
            (code / 'context_guard.py').write_text('LIMIT = 4096\n')
            (code / 'embedded.py').write_text('PAE_API_KEY = "' + 'gsk_' + 'x' * 30 + '"\n')
            (code / 'data/sessions').mkdir(parents=True)
            (code / 'data/sessions/private.json').write_text('{"private":"conversation"}')
            (code / 'github.env').write_text('SECRET=private')
            (code / 'outside.py').symlink_to(Path(temp) / 'private.py')
            (Path(temp) / 'private.py').write_text('private data')
            output = Path(temp) / 'snapshot.zip'
            report = inventory.collect(root, output, include_source=True)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(set(archive.namelist()), {'inventory.json','source/prototype_v0/app.py','source/prototype_v0/context_guard.py'})
                self.assertIsNone(archive.testzip())
            self.assertTrue(any(x['path'].endswith('embedded.py') for x in report['excluded']))
            self.assertFalse(report['uploaded'])
            with self.assertRaises(FileExistsError):
                inventory.collect(root, output, include_source=True)


if __name__ == '__main__':
    unittest.main()
