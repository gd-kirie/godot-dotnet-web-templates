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
- `assemble-export.py`, which combines the template, published assemblies, and PCK.
- Godot and .NET license notices.
- A manifest and SHA-256 checksums.

The archive does not contain a custom Godot editor. Users and this repository
do not compile one.

The standard .NET JavaScript host loads the runtime and application assemblies
before Godot starts. It owns runtime initialization and the worker pool.
The generated `DOTNET.setup(...)` call remains intact.

Export requires three inputs: a template ZIP, the complete `dotnet publish`
directory, and a PCK from the same application build. The PCK must include the
`dotnet` custom feature so Godot initializes its managed bindings. Use the patched NuGet
packages as an explicit restore source. `NUGET_PACKAGES` only selects a cache;
it does not make local `.nupkg` files available for restore.

```sh
python3 assemble-export.py --template web_debug.zip \
  --publish path/to/publish --pack path/to/game.pck --output site/game.html
```

Copy application web assets into the site separately, preserving their paths.
Kirie expects them at `src-web/dist/`. Serve the entire output directory.

Kirie CLI 0.14.1 still uses the previous post-export patch contract. It needs a
separate integration change before it can consume these templates. This change
does not replace the user's official Godot .NET editor.

The current templates have these limits:

- They require WebAssembly threads and cross-origin isolation.
- They use `optimize=none` and `lto=none`.
- They require the matching .NET 10.0.12 runtime and published assemblies.
- The Mono interpreter runs managed code. Jiterpreter traces are disabled.
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

The browser acceptance script checks known sums, worker IDs, browser cryptography,
UI clicks during computation, completion, cancellation, restart, and reload:

```sh
npm ci
CHROMIUM_PATH=/path/to/chromium npm run test:browser -- http://localhost:8765/game.html
```

Use `python3 scripts/serve.py path/to/site` to serve the required isolation headers.
The build creates these exports in `.tmp/output/smoke/debug` and
`.tmp/output/smoke/release`. The release workflow tests both before publishing.
`pack-smoke.gd` packages this fixed test fixture; it is not a general Godot exporter.

The local Chromium run passed both templates, including page reload. A real
Kirie Eventa example also completed requests in both directions with the Debug
template. Firefox, Safari, and the released Kirie CLI path remain untested.

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

## Runtime integration

The host uses the [.NET 10.0.12 loader](https://github.com/dotnet/runtime/tree/v10.0.12/src/mono/browser/runtime/loader).
The native template keeps the upstream `DOTNET.setup` imports and hooks.
`patches/js-host.patch` adapts Emscripten 4 startup order and worker dispatch to
that loader. The .NET loader initializes Mono before Godot loads its assemblies.

The native JS module and host files are assembled when templates are built.
Application export copies these files and writes a resource manifest. It does
not search or rewrite generated JavaScript.

All managed assemblies come from one application publish. Mixing framework
assemblies from the template's trimmed build with application assemblies can
break runtime type loading. The SDK pins `RuntimeFrameworkVersion` to 10.0.12;
the assembler rejects a different version or non-invariant globalization.

Godot invokes managed callbacks on the browser UI thread. The .NET jiterpreter
allocates its function tables on managed workers. The host disables its trace
optimizer to avoid accessing missing tables on the UI thread.
See [.NET worker initialization](https://github.com/dotnet/runtime/blob/v10.0.12/src/mono/browser/runtime/pthreads/worker-thread.ts).
This has a performance cost. Other .NET browser APIs still require validation.

## Provenance

Raul Santos authored the upstream Draft implementation. See pull request
[godotengine/godot#106125](https://github.com/godotengine/godot/pull/106125).

Godot uses the MIT License. The templates also include .NET runtime components.
Release files include the applicable Godot and .NET license and copyright
notices. See [NOTICE.md](NOTICE.md) for more information.
