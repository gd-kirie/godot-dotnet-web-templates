#!/usr/bin/env bash
set -euo pipefail

# Runs in the build container after packages and templates have been built.
smoke=/output/smoke
mkdir -p "$smoke/project"
cp /workspace/smoke/* "$smoke/project/"
cat > "$smoke/project/NuGet.Config" <<'XML'
<configuration>
  <packageSources>
    <clear />
    <add key="templates" value="/output/nuget" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
  </packageSources>
  <packageSourceMapping>
    <packageSource key="templates"><package pattern="Godot*" /></packageSource>
    <packageSource key="nuget.org"><package pattern="*" /></packageSource>
  </packageSourceMapping>
</configuration>
XML
export NUGET_PACKAGES="$smoke/nuget-cache"
# Package versions stay at 4.7.2 across template builds.
for package in godot.net.sdk godot.sourcegenerators godotsharp godotsharpeditor; do
  rm -rf "$NUGET_PACKAGES/$package"
done
dotnet publish "$smoke/project/Step1CSharpWeb.csproj" -c ExportDebug \
  -r browser-wasm --self-contained true -p:GodotTargetPlatform=web -o "$smoke/publish"
/opt/godot/godot --headless --path "$smoke/project" \
  --script /workspace/scripts/pack-smoke.gd -- "$smoke/publish" "$smoke/game.pck"
for mode in debug release; do
  python3 /workspace/scripts/assemble-export.py \
    --template "/output/templates/web_${mode}.zip" --publish "$smoke/publish" \
    --pack "$smoke/game.pck" --output "$smoke/$mode/game.html"
done
