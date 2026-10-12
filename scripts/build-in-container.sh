#!/usr/bin/env bash
set -euo pipefail

jobs=${JOBS:-8}
cache=/output/cache
nuget=/output/nuget
templates=/output/templates
mkdir -p "$cache" "$nuget" "$templates"
export NUGET_PACKAGES=$cache/nuget-packages
export NUGET_HTTP_CACHE_PATH=$cache/nuget-http-cache

editor=/godot/bin/godot.linuxbsd.editor.x86_64.mono
if [[ ! -x "$editor" ]]; then
  scons platform=linuxbsd target=editor arch=x86_64 module_mono_enabled=yes \
    wayland=no accesskit=no debug_symbols=no -j"$jobs"
fi

if [[ ! -f "$nuget/Godot.NET.Sdk.4.7.2.nupkg" ]]; then
  "$editor" --headless --generate-mono-glue ./modules/mono/glue
  ./modules/mono/build_scripts/build_assemblies.py \
    --godot-output-dir=./bin --godot-platform=linuxbsd --push-nupkgs-local="$nuget"
fi

for mode in debug release; do
  rm -f "bin/godot.web.template_${mode}.wasm32.nothreads.mono.zip"
  scons platform=web target="template_${mode}" arch=wasm32 module_mono_enabled=yes \
    threads=no debug_symbols=no optimize=none lto=none -j"$jobs"
  install -m 0644 "bin/godot.web.template_${mode}.wasm32.nothreads.mono.zip" \
    "$templates/web_${mode}.zip"
done

rm -rf /output/editor
mkdir -p /output/editor
install -m 0755 "$editor" /output/editor/
cp -a /godot/bin/GodotSharp /output/editor/
python3 /workspace/scripts/package-release.py /output

