#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import shutil
import sys
import zipfile

output = pathlib.Path(sys.argv[1]).resolve()
stage = output / "stage"
dist = output / "dist"
shutil.rmtree(stage, ignore_errors=True)
shutil.rmtree(dist, ignore_errors=True)
stage.mkdir()
dist.mkdir()

for source in [output / "templates" / "web_debug.zip", output / "templates" / "web_release.zip"]:
    shutil.copy2(source, stage / source.name)
for source in sorted((output / "nuget").glob("Godot*.4.7.2.nupkg")):
    shutil.copy2(source, stage / source.name)
shutil.copy2("/workspace/scripts/patch-export.py", stage / "patch-export.py")
shutil.copytree("/workspace/licenses", stage / "licenses")

required_packages = {
    "Godot.NET.Sdk.4.7.2.nupkg",
    "Godot.SourceGenerators.4.7.2.nupkg",
    "GodotSharp.4.7.2.nupkg",
    "GodotSharpEditor.4.7.2.nupkg",
}
actual_packages = {path.name for path in stage.glob("*.nupkg")}
if actual_packages != required_packages:
    raise RuntimeError(
        f"Expected exactly {sorted(required_packages)}, found {sorted(actual_packages)}"
    )

files = {}
for source in sorted(path for path in stage.rglob("*") if path.is_file()):
    relative = source.relative_to(stage).as_posix()
    files[relative] = {
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "size": source.stat().st_size,
    }

manifest = {
    "schemaVersion": 1,
    "channel": "experimental-ai-slop",
    "release": os.environ["RELEASE_TAG"],
    "godotVersion": "4.7.2.stable.mono",
    "godotCommit": "ed1daf0bf001b61586d9930840f2f1394092c079",
    "draftPullRequest": 106125,
    "draftCommit": "aa1f5ffe8321bc57155f606197b5aa93dd9e662c",
    "targetFramework": "net10.0",
    "threadSupport": False,
    "extensionsSupport": False,
    "optimized": False,
    "files": files,
}
(stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

archive = dist / "godot-dotnet-web-templates-4.7.2-net10.zip"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
    for source in sorted(path for path in stage.rglob("*") if path.is_file()):
        bundle.write(source, source.relative_to(stage))

checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
(dist / "SHA256SUMS").write_text(f"{checksum}  {archive.name}\n")
