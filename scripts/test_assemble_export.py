import importlib.util
import json
import pathlib
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('assemble_export', pathlib.Path(__file__).with_name('assemble-export.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AssembleExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.publish = self.root / 'publish'
        self.publish.mkdir()
        self.config = {'runtimeOptions': {
            'includedFrameworks': [{'name': 'Microsoft.NETCore.App', 'version': '10.0.12'}],
            'configProperties': {'System.Globalization.Invariant': True},
        }}
        self.write_config()
        for name in ['App.dll', 'System.Private.CoreLib.dll', 'System.Runtime.InteropServices.JavaScript.dll']:
            (self.publish / name).write_bytes(b'assembly ' + name.encode())
        (self.publish / 'de').mkdir()
        (self.publish / 'de/App.resources.dll').write_bytes(b'satellite')
        self.template = self.root / 'template.zip'
        with zipfile.ZipFile(self.template, 'w') as archive:
            archive.writestr('godot.dotnet/template.json', json.dumps({'runtimeVersion': '10.0.12'}))
            for suffix in ['js', 'wasm', 'audio.worklet.js', 'audio.position.worklet.js']:
                archive.writestr('godot.' + suffix, suffix)
            archive.writestr('godot.html', '<script src="$GODOT_URL"></script>$GODOT_CONFIG')
        self.pack = self.root / 'input.pck'
        self.pack.write_bytes(b'pack')
        self.output = self.root / 'site/game.html'

    def write_config(self):
        (self.publish / 'App.runtimeconfig.json').write_text(json.dumps(self.config))

    def assemble(self):
        module.assemble(self.template, self.publish, self.pack, self.output)

    def test_export_preserves_resources_and_satellite_layout(self):
        self.assemble()
        host = self.output.parent / 'game.dotnet'
        config = json.loads((host / 'config.json').read_text())
        for item in config['resources']['coreAssembly']:
            self.assertEqual((host / item['name']).read_bytes(), (self.publish / item['name']).read_bytes())
        resource = config['resources']['satelliteResources']['de'][0]
        self.assertEqual((host / 'de' / resource['name']).read_bytes(), b'satellite')
        self.assertEqual(self.output.with_suffix('.pck').read_bytes(), b'pack')
        self.assertTrue((self.output.parent / 'game.audio.worklet.js').is_file())
        self.assertIn('game.js', self.output.read_text())

    def test_rejects_mismatched_framework(self):
        self.config['runtimeOptions']['includedFrameworks'][0]['version'] = '10.0.11'
        self.write_config()
        with self.assertRaisesRegex(ValueError, 'Runtime mismatch'):
            self.assemble()
        self.assertFalse(self.output.parent.exists())

    def test_rejects_unsupported_globalization(self):
        self.config['runtimeOptions']['configProperties']['System.Globalization.Invariant'] = False
        self.write_config()
        with self.assertRaisesRegex(ValueError, 'invariant globalization'):
            self.assemble()

    def test_rejects_incomplete_publish(self):
        (self.publish / 'System.Private.CoreLib.dll').unlink()
        with self.assertRaisesRegex(ValueError, 'System.Private.CoreLib'):
            self.assemble()
