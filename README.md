# Godot .NET Web toolchains

This repository builds experimental Web export toolchains for Godot 4.7.2 and
.NET 10.

> [!WARNING]
> This project is experimental. Godot does not support .NET Web export in an
> official release at this time.
>
> AI agents developed all current code in this repository. A human has not done
> a systematic entropy-reduction pass. The repository contains substantial AI
> slop, duplication, temporary structure, and unrefined build logic.
>
> Do not use this project as a production toolchain. Examine the source and the
> generated files before you use them.

The build uses only these Godot sources:

- Godot 4.7.2 commit `ed1daf0bf001b61586d9930840f2f1394092c079`.
- Draft pull request [godotengine/godot#106125](https://github.com/godotengine/godot/pull/106125), commit `aa1f5ffe8321bc57155f606197b5aa93dd9e662c`.

The repository does not use a third-party Godot fork or a third-party template.
It applies a recorded forward port to the official Godot source.

## Planned Kirie install

The preview 2 archive layout is designed for `kirie doctor fix`. When preview 2
is published, a Godot project that uses C# and targets Web can run:

```sh
kirie doctor fix
```

The fix downloads the matching platform asset, verifies `SHA256SUMS` and the
file hashes in `manifest.json`, then installs the toolchain in the Kirie cache.
It includes the editor. Users do not need to clone Godot or compile it.
The installer must make `manifest.editor.path` executable after extraction.

The official Godot 4.7.2 .NET editor still rejects Web export. Kirie uses the
editor in this toolchain only for the experimental Web export.

## Supported hosts

| Host | Release asset | Editor path |
| --- | --- | --- |
| macOS Apple Silicon | `godot-dotnet-web-4.7.2-net10-darwin-arm64.zip` | `editor/Godot.app/Contents/MacOS/Godot` |
| Linux x64 | `godot-dotnet-web-4.7.2-net10-linux-x64.zip` | `editor/godot` |

The macOS app has an ad hoc signature. It is not notarized. Intel macOS,
Windows, and Linux arm64 are not supported by preview 2.

Each platform archive contains:

- The patched Godot editor and its matching `GodotSharp` directory.
- `templates/web_debug.zip` and `templates/web_release.zip`.
- Four matching local Godot NuGet packages in `nuget/`.
- `patch-export.py`, which performs the post-export change required by the
  upstream Draft.
- License notices and a schema v2 `manifest.json`.

`SHA256SUMS` in the GitHub Release verifies the complete archives. The manifest
contains the editor, template, NuGet package, and patch paths and SHA-256 hashes.

The current toolchains have these limits:

- They use WebAssembly without threads.
- They use `optimize=none` and `lto=none`.
- They target .NET 10.
- They use invariant globalization.
- Only Chromium has browser test evidence.
- Some .NET browser APIs do not work.

## Build Linux x64

Install Docker. Then run:

```sh
./scripts/prepare-source.sh .tmp/godot
./scripts/build.sh .tmp/godot .tmp/output
```

The build uses fixed container digests and fixed source commits. It validates
the patched source tree before it starts compilation.

## Build macOS arm64

Install Xcode, Python, SCons 4.10.1, and .NET SDK 10.0.401. Build the Web
templates on Linux first and put them in `.tmp/output/templates`. Then run:

```sh
./scripts/prepare-source.sh .tmp/godot
./scripts/build-macos.sh .tmp/godot .tmp/output
```

The release workflow performs both platform builds. A tag named
`4.7.2-dotnet10-preview.2` creates the preview 2 Release only after both assets
exist and their outer checksums pass.

## Provenance

Raul Santos authored the upstream Draft implementation. See pull request
[godotengine/godot#106125](https://github.com/godotengine/godot/pull/106125).

Godot uses the MIT License. Release files include the Godot license and
copyright notices. See [NOTICE.md](NOTICE.md) for more information.
