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
- `assemble-export.py` for assembling the Web export.
- Godot and .NET license notices.
- A manifest and SHA-256 checksums.

The archive does not contain a custom Godot editor. Users and this repository
do not compile one.

Use the patched NuGet packages as a restore source. Publish for `browser-wasm`,
then export a PCK from the same build with the `dotnet` custom feature.

```sh
python3 assemble-export.py --template web_debug.zip \
  --publish path/to/publish --pack path/to/game.pck --output site/game.html
```

Copy application web assets to `site/`, preserving their paths.
Kirie CLI 0.14.1 does not support this export format yet.

The current templates have these limits:

- They require WebAssembly threads and cross-origin isolation.
- They use `optimize=none` and `lto=none`.
- They require .NET 10.0.12.
- Jiterpreter traces are disabled.
- They use invariant globalization.
- Only Chromium has browser test evidence.
- Some .NET browser APIs do not work.

## Threaded exports

Both templates use `threads=yes` and the .NET multithreaded runtime.
The SDK sets `WasmEnableThreads=true`. The release manifest declares
`threadSupport=true`. This repository no longer builds a single-threaded variant.

The template defaults to 24 Emscripten workers and 4 Godot workers.
The Emscripten pool serves both Godot and Mono. A pool of 8 exhausted the workers
in the smoke test. Larger workloads can require a larger pool.

For export presets, set `variant/thread_support=true`,
`threads/emscripten_pool_size=24`, and `threads/godot_pool_size=4`.
For a custom JavaScript host, use `emscriptenPoolSize: 24` and `godotPoolSize: 4`.
The `scripts/configure-export.gd` script sets these preset values.

Serve the export through HTTPS or localhost with these response headers:

```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

The page must report `crossOriginIsolated === true`.
Cross-origin resources must also meet the browser's CORS or CORP requirements.

Install the matching templates, SDK packages, and `assemble-export.py` together.
The NuGet version remains `4.7.2`. An existing NuGet cache can contain the previous
single-threaded SDK under that version. When you switch releases, use a fresh
`NUGET_PACKAGES` directory. Then restore and publish the project again.

The `smoke/` project checks `Thread` and `Task.Run` against a known sum and logs
`THREAD_PROBE_PASS` with their managed thread IDs. Its interactive demo also runs
two CPU tasks while the main thread updates the UI. It supports cancellation and
restart. The progress bars show elapsed time, and the counters show actual work.

On 2026-10-13, Debug and Release passed these checks in Chromium through
Playwright: known sums, distinct worker IDs, UI clicks during computation,
completion, cancellation, restart, and page reload. The host used the template's
default worker pool. Firefox, Safari, and the full Kirie export flow remain untested
with these threaded templates.

Only the main thread modifies Godot objects. Background threads submit plain
data through `Volatile` and `Interlocked`. These tests do not establish support
for all .NET browser APIs or measure parallel speedup.

Chromium logs an Emscripten main-thread blocking warning during restart.
The tested runs continued without a hang.

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
