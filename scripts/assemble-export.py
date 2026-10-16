#!/usr/bin/env python3
"""Assemble a Godot .NET Web export."""
import argparse
import base64
import hashlib
import html
import json
import pathlib
import shutil
import zipfile


def assemble(template_path, publish, pack, output):
    publish, pack, output = map(pathlib.Path, (publish, pack, output))
    configs = list(publish.glob('*.runtimeconfig.json'))
    if len(configs) != 1:
        raise ValueError('Expected one application runtimeconfig.json in the publish directory')
    runtime_config = json.loads(configs[0].read_text())
    framework = next(item for item in runtime_config['runtimeOptions']['includedFrameworks']
                     if item['name'] == 'Microsoft.NETCore.App')
    if runtime_config['runtimeOptions'].get('configProperties', {}).get('System.Globalization.Invariant') is not True:
        raise ValueError('The template requires invariant globalization')
    if not (publish / 'System.Private.CoreLib.dll').is_file():
        raise ValueError('The application publish output has no System.Private.CoreLib.dll')
    with zipfile.ZipFile(template_path) as template:
        metadata = json.loads(template.read('godot.dotnet/template.json'))
        if framework['version'] != metadata['runtimeVersion']:
            raise ValueError(f"Runtime mismatch: application {framework['version']}, template {metadata['runtimeVersion']}")
        # System.Runtime.InteropServices.JavaScript depends on the threaded build.
        if not (publish / 'System.Runtime.InteropServices.JavaScript.dll').is_file():
            raise ValueError('The application publish output has no browser JavaScript interop assembly')
        output.parent.mkdir(parents=True, exist_ok=True)
        basename = output.stem
        host_dir = output.parent / f'{basename}.dotnet'
        host_dir.mkdir(exist_ok=True)
        for name in template.namelist():
            if name.startswith('godot.dotnet/') and not name.endswith('/'):
                relative = pathlib.PurePosixPath(name).relative_to('godot.dotnet')
                if '..' in relative.parts:
                    raise ValueError(f'Invalid template path: {name}')
                target = host_dir.joinpath(*relative.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(template.read(name))
        for suffix in ['js', 'wasm', 'audio.worklet.js', 'audio.position.worklet.js']:
            (output.parent / f'{basename}.{suffix}').write_bytes(template.read(f'godot.{suffix}'))
        assemblies = []
        satellites = {}
        for assembly in sorted(publish.rglob('*.dll')):
            relative = assembly.relative_to(publish)
            target = host_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(assembly, target)
            resource = {
                'name': assembly.name,
                'virtualPath': assembly.name,
                'hash': 'sha256-' + base64.b64encode(hashlib.sha256(assembly.read_bytes()).digest()).decode(),
            }
            if assembly.name.endswith('.resources.dll'):
                resource['culture'] = relative.parent.name
                satellites.setdefault(resource['culture'], []).append(resource)
            else:
                assemblies.append(resource)
        config = {
            'mainAssemblyName': configs[0].name.removesuffix('.runtimeconfig.json') + '.dll',
            'globalizationMode': 'invariant',
            'loadAllSatelliteResources': True,
            'runtimeConfig': runtime_config,
            'resources': {
                'jsModuleNative': [{'name': 'native.mjs'}],
                'jsModuleRuntime': [{'name': 'dotnet.runtime.js'}],
                'jsModuleWorker': [{'name': 'worker.mjs'}],
                'wasmNative': [{'name': f'../{basename}.wasm'}],
                'coreAssembly': assemblies,
                'satelliteResources': satellites,
            },
        }
        (host_dir / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
        shutil.copy2(pack, output.with_suffix('.pck'))
        engine_config = {
            'args': [], 'canvasResizePolicy': 2, 'executable': basename,
            'emscriptenPoolSize': 24, 'godotPoolSize': 4,
            'ensureCrossOriginIsolationHeaders': True,
            'experimentalVK': False, 'focusCanvas': True, 'gdextensionLibs': [],
            'fileSizes': {f'{basename}.{suffix}': (output.parent / f'{basename}.{suffix}').stat().st_size
                          for suffix in ['wasm', 'pck']},
        }
        page = template.read('godot.html').decode()
        replacements = {
            '$GODOT_PROJECT_NAME': html.escape(basename), '$GODOT_SPLASH_COLOR': '#242424',
            '$GODOT_HEAD_INCLUDE': '<link rel="icon" href="data:,">', '$GODOT_SPLASH_CLASSES': 'show-image--false fullsize--false use-filter--true',
            '$GODOT_SPLASH': 'data:image/gif;base64,R0lGODlhAQABAAAAACw=',
            '$GODOT_URL': f'{basename}.js', '$GODOT_CONFIG': json.dumps(engine_config),
            '$GODOT_THREADS_ENABLED': 'true',
        }
        for key, value in replacements.items():
            page = page.replace(key, value)
        output.write_text(page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', required=True, type=pathlib.Path)
    parser.add_argument('--publish', required=True, type=pathlib.Path)
    parser.add_argument('--pack', required=True, type=pathlib.Path)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args()
    assemble(args.template, args.publish, args.pack, args.output)
