#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import shutil
import sys
import zipfile

output = pathlib.Path(sys.argv[1]).resolve()
platform = sys.argv[2]
arch = sys.argv[3]
editor_path = pathlib.PurePosixPath(sys.argv[4])
managed_path = pathlib.PurePosixPath(sys.argv[5])
if platform not in {"darwin", "linux"}:
    raise ValueError(f"Unsupported platform: {platform}")
if arch not in {"arm64", "x64"}:
    raise ValueError(f"Unsupported architecture: {arch}")
for path in (editor_path, managed_path):
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Archive path must be relative and contained: {path}")
stage = output / f"stage-{platform}-{arch}"
dist = output / "dist"
shutil.rmtree(stage, ignore_errors=True)
stage.mkdir()
dist.mkdir(exist_ok=True)

shutil.copytree(output / "editor", stage / "editor", symlinks=True)
shutil.copytree(output / "templates", stage / "templates")
shutil.copytree(output / "nuget", stage / "nuget")
for source in sorted((output / "nuget").glob("Godot*.4.7.2.nupkg")):
    if not (stage / "nuget" / source.name).is_file():
        raise RuntimeError(f"Missing staged NuGet package: {source.name}")

script_root = pathlib.Path(__file__).resolve().parent
repo_root = script_root.parent
shutil.copy2(script_root / "patch-export.py", stage / "patch-export.py")
shutil.copytree(repo_root / "licenses", stage / "licenses")
shutil.copy2(repo_root / "LICENSE", stage / "licenses" / "REPOSITORY-LICENSE.txt")
shutil.copy2(repo_root / "NOTICE.md", stage / "licenses" / "NOTICE.md")

required_packages = {
    "Godot.NET.Sdk.4.7.2.nupkg",
    "Godot.SourceGenerators.4.7.2.nupkg",
    "GodotSharp.4.7.2.nupkg",
    "GodotSharpEditor.4.7.2.nupkg",
}
actual_packages = {path.name for path in (stage / "nuget").glob("*.nupkg")}
if actual_packages != required_packages:
    raise RuntimeError(
        f"Expected exactly {sorted(required_packages)}, found {sorted(actual_packages)}"
    )

if not (stage / editor_path).is_file():
    raise RuntimeError(f"Editor executable is missing: {editor_path}")
if not (stage / managed_path).is_dir():
    raise RuntimeError(f"GodotSharp directory is missing: {managed_path}")

files = {}
for source in sorted(path for path in stage.rglob("*") if path.is_file()):
    relative = source.relative_to(stage).as_posix()
    files[relative] = {
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "size": source.stat().st_size,
    }

manifest = {
    "schemaVersion": 2,
    "release": os.environ["RELEASE_TAG"],
    "platform": platform,
    "arch": arch,
    "godotVersion": "4.7.2.stable.mono",
    "godotCommit": "ed1daf0bf001b61586d9930840f2f1394092c079",
    "draftCommit": "aa1f5ffe8321bc57155f606197b5aa93dd9e662c",
    "targetFramework": "net10.0",
    "editor": {"path": editor_path.as_posix()},
    "templates": {
        "debug": "templates/web_debug.zip",
        "release": "templates/web_release.zip",
    },
    "nuget": {
        "directory": "nuget",
        "packages": [
            path
            for path in files
            if path.startswith("nuget/") and path.endswith(".nupkg")
        ],
    },
    "patch": {
        "id": "remove-dotnet-setup-v1",
        "path": "patch-export.py",
    },
    "files": files,
}
(stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

archive = dist / f"godot-dotnet-web-4.7.2-net10-{platform}-{arch}.zip"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
    for source in sorted(path for path in stage.rglob("*") if path.is_file()):
        archive_path = source.relative_to(stage)
        info = zipfile.ZipInfo.from_file(source, archive_path)
        info.date_time = (2026, 8, 16, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        with source.open("rb") as input_file:
            bundle.writestr(info, input_file.read(), compresslevel=9)

checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
(dist / f"{archive.name}.sha256").write_text(f"{checksum}  {archive.name}\n")
