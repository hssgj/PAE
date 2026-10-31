import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('phone_inventory', Path(__file__).with_name('phone_inventory.py'))
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class PhoneInventoryTests(unittest.TestCase):
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
