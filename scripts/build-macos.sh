#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source "$repo_root/versions.env"
export RELEASE_TAG
source_dir=${1:?Usage: build-macos.sh SOURCE_DIR OUTPUT_DIR}
output_dir=${2:?Usage: build-macos.sh SOURCE_DIR OUTPUT_DIR}
jobs=${JOBS:-3}
source_dir=$(cd -- "$source_dir" && pwd)
mkdir -p "$output_dir"
output_dir=$(cd -- "$output_dir" && pwd)
export TMPDIR=${TMPDIR:-$output_dir/cache/tmp}
build_home=$output_dir/cache/build-home

"$repo_root/scripts/validate-source.sh" "$source_dir"
mkdir -p "$output_dir/nuget" "$output_dir/templates" "$build_home" "$TMPDIR"

pushd "$source_dir" >/dev/null
editor=bin/godot.macos.editor.arm64.mono
bundle=bin/godot_macos_editor_mono.app

HOME="$build_home" scons platform=macos target=editor arch=arm64 module_mono_enabled=yes \
  accesskit=no angle=no vulkan=no debug_symbols=no -j"$jobs"

if [[ ! -d bin/GodotSharp || \
      ! -f "$output_dir/nuget/Godot.NET.Sdk.4.7.2.nupkg" || \
      ! -f "$output_dir/nuget/Godot.SourceGenerators.4.7.2.nupkg" || \
      ! -f "$output_dir/nuget/GodotSharp.4.7.2.nupkg" || \
      ! -f "$output_dir/nuget/GodotSharpEditor.4.7.2.nupkg" ]]; then
  "$editor" --headless --generate-mono-glue ./modules/mono/glue
  ./modules/mono/build_scripts/build_assemblies.py \
    --godot-output-dir=./bin \
    --godot-platform=macos \
    --push-nupkgs-local="$output_dir/nuget"
fi

# The bundle builder copies the matching GodotSharp directory after the
# managed assemblies exist. The second SCons call reuses the compiled editor.
HOME="$build_home" scons platform=macos target=editor arch=arm64 module_mono_enabled=yes \
  accesskit=no angle=no vulkan=no debug_symbols=no generate_bundle=yes -j"$jobs"

test -x "$bundle/Contents/MacOS/Godot"
test -d "$bundle/Contents/Resources/GodotSharp"
rm -rf "$output_dir/editor"
mkdir -p "$output_dir/editor"
cp -a "$bundle" "$output_dir/editor/Godot.app"
codesign --force --deep --sign - "$output_dir/editor/Godot.app"
popd >/dev/null

python3 "$repo_root/scripts/package-release.py" \
  "$output_dir" darwin arm64 \
  editor/Godot.app/Contents/MacOS/Godot \
  editor/Godot.app/Contents/Resources/GodotSharp
