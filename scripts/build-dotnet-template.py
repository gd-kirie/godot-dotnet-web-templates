#!/usr/bin/env python3
"""Add the standard .NET JavaScript host to a compiled Godot template."""
import json
import pathlib
import sys
import zipfile

source = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
output = pathlib.Path(sys.argv[3])
repo = pathlib.Path(__file__).resolve().parent.parent
versions = dict(line.split('=', 1) for line in (repo / 'versions.env').read_text().splitlines() if '=' in line)
native = source / 'modules/mono/runtime/GetRuntimePack/bin/mono_runtime'
basename = f'godot.web.template_{mode}.wasm32.mono'
with zipfile.ZipFile(source / 'bin' / f'{basename}.zip') as template:
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as result:
        for entry in template.infolist():
            result.writestr(entry, template.read(entry.filename))
        for name in ['dotnet.js', 'dotnet.runtime.js']:
            result.write(native / name, f'godot.dotnet/{name}')
        for name in ['host.mjs', 'native.mjs', 'worker.mjs']:
            result.write(repo / 'host' / name, f'godot.dotnet/{name}')
        # These are link-time fragments from the matching .NET runtime pack.
        script = (source / 'bin' / f'{basename}.js').read_text()
        script += '\n' + (native / 'src/es6/dotnet.es6.extpost.js').read_text()
        script += '\nvar _scriptDir = "";\nexport default Godot;\n'
        result.writestr('godot.dotnet/godot-native.mjs', script)
        result.writestr('godot.dotnet/template.json', json.dumps({
            'schemaVersion': 1,
            'runtimeVersion': versions['DOTNET_RUNTIME_VERSION'],
            'threadSupport': True,
        }) + '\n')
