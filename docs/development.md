# Development

## Runtime integration

The template uses the [.NET 10.0.12 loader](https://github.com/dotnet/runtime/tree/v10.0.12/src/mono/browser/runtime/loader).
`patches/js-host.patch` adapts Emscripten 4 startup order and worker dispatch.
The loader initializes Mono before Godot starts and preserves `DOTNET.setup`.

Template builds include the native JS module and host files. Application export
copies these files and creates a resource manifest from one complete publish.
The SDK pins `RuntimeFrameworkVersion` to 10.0.12. Mixing trimmed framework
assemblies from different publishes can break type loading.

Godot invokes managed callbacks on the UI thread. The jiterpreter allocates
function tables on managed workers, so the host disables its trace optimizer.
See [.NET worker initialization](https://github.com/dotnet/runtime/blob/v10.0.12/src/mono/browser/runtime/pthreads/worker-thread.ts).

Both templates use `threads=yes`, `optimize=none`, and `lto=none`. The build uses
the official precompiled Godot .NET editor to generate glue and NuGet packages.
It validates the patched source tree before compilation.

## Browser tests

The build creates smoke exports in `.tmp/output/smoke/debug` and
`.tmp/output/smoke/release`. The release workflow tests both before publishing.

```sh
npm ci
python3 scripts/serve.py .tmp/output/smoke
```

In another terminal:

```sh
CHROMIUM_PATH=/path/to/chromium npm run test:browser -- http://localhost:8765/debug/game.html
CHROMIUM_PATH=/path/to/chromium npm run test:browser -- http://localhost:8765/release/game.html
```

The suite checks browser cryptography, thread results, UI input during work,
completion, cancellation, restart, and reload. `pack-smoke.gd` packages only this
fixture. Only the main thread modifies Godot objects.

Chromium can log an Emscripten main-thread blocking warning during restart.
