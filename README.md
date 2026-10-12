# Godot .NET Web templates

This repository builds experimental Web export files for Godot 4.7.2 and .NET 10.

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

## Scope

The release contains these files:

- `web_debug.zip`.
- `web_release.zip`.
- The matching local Godot NuGet packages.
- A manifest and SHA-256 checksums.

The template files alone do not add .NET Web support to the official editor.
A compatible editor and the matching NuGet packages are also necessary.
The Kirie CLI manages this experimental toolchain through `kirie doctor`.

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

The build uses fixed container digests and fixed source commits. It validates
the patched source tree before it starts compilation.

## Provenance

Raul Santos authored the upstream Draft implementation. See pull request
[godotengine/godot#106125](https://github.com/godotengine/godot/pull/106125).

Godot uses the MIT License. Release files include the Godot license and
copyright notices. See [NOTICE.md](NOTICE.md) for more information.

