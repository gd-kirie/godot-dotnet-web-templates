import pathlib
import subprocess
import sys
import tempfile
import unittest


class PatchExportTest(unittest.TestCase):
    def run_patch(self, source):
        with tempfile.TemporaryDirectory() as directory:
            html = pathlib.Path(directory) / "game.html"
            script = html.with_suffix(".js")
            script.write_text(source)
            result = subprocess.run(
                [sys.executable, str(pathlib.Path(__file__).with_name("patch-export.py")), str(html)],
                capture_output=True,
                text=True,
            )
            return result, script.read_text()

    def test_generated_host_formats(self):
        for setup in [
            'DOTNET.setup({wasmEnableThreads:false});;\n',
            'DOTNET.setup({\n  wasmEnableThreads: true,\n  gitHash: "runtime"\n});\n',
        ]:
            with self.subTest(setup=setup):
                before = "PThread.init();\nFS.staticInit();\n"
                after = 'Module["pauseMainLoop"] = MainLoop.pause;\n'
                result, patched = self.run_patch(before + setup + after)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(patched, before + after)

    def test_unexpected_host_is_not_modified(self):
        for source in [
            "MainLoop.init();\n",
            "DOTNET.setup({});\nDOTNET.setup({});\n",
            "DOTNET.setup({\nMainLoop.init();\n",
        ]:
            with self.subTest(source=source):
                result, patched = self.run_patch(source)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(patched, source)


if __name__ == "__main__":
    unittest.main()
