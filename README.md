# Godot .NET Web templates

This repository builds experimental Web export files for Godot 4.7.2 and
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
- Draft pull request
  [godotengine/godot#106125](https://github.com/godotengine/godot/pull/106125),
  commit `aa1f5ffe8321bc57155f606197b5aa93dd9e662c`.

The repository does not use a third-party Godot fork or a third-party template.
It applies a recorded forward port to the official Godot source.

## Scope

A release archive contains these files:

- `web_debug.zip` and `web_release.zip`.
- Four matching local Godot NuGet packages.
- `patch-export.py`, which applies the remaining post-export change from the
  upstream Draft.
- Godot and .NET license notices.
- A manifest and SHA-256 checksums.

The archive does not contain a custom Godot editor. Users and this repository
do not compile one.

Kirie performs .NET Web export as separate, reproducible steps:

1. The Kirie CLI runs `dotnet publish` for `browser-wasm` outside Godot with
   the patched local SDK and verifies the output with a SHA-512 manifest.
2. The user's existing configured official Godot Mono/.NET editor runs
   `--export-pack Web`.
3. Kirie's GDScript export plugin adds the `dotnet` feature, a C# stub, and
   `res://.godot/mono/publish/wasm32` to the PCK during that pack export.
4. The CLI assembles the HTML, JavaScript, WebAssembly, and PCK files outside
   Godot from the custom template, then applies the recorded post-export patch.

`kirie doctor fix` can install the matching templates, NuGet packages, and
patch in the Kirie cache. It does not replace the user's Godot editor or
install a second editor.

The current templates have these limits:

- They use WebAssembly without threads.
- They use `optimize=none` and `lto=none`.
- They target .NET 10.
- They use invariant globalization.
- Only Chromium has browser test evidence.
- Some .NET browser APIs do not work.

## Build

Install Docker. Then run:

```sh
./scripts/prepare-source.sh .tmp/godot
./scripts/build.sh .tmp/godot .tmp/output
```

The build uses fixed container digests, source commits, and tool versions. It
validates the patched source tree before compilation. The container downloads
the official precompiled Godot 4.7.2 .NET Linux editor and verifies its SHA-256
digest. The build uses that editor only to generate managed glue and NuGet
packages. It does not include the editor in the release archive.

## Provenance

Raul Santos authored the upstream Draft implementation. See pull request
[godotengine/godot#106125](https://github.com/godotengine/godot/pull/106125).

Godot uses the MIT License. The templates also include .NET runtime components.
Release files include the applicable Godot and .NET license and copyright
notices. See [NOTICE.md](NOTICE.md) for more information.
