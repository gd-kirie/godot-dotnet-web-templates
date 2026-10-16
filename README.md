# Godot .NET Web templates

Experimental Web export templates for Godot 4.7.2 and .NET 10.0.12.

> [!WARNING]
> AI-developed experimental toolchain. Not for production use.
> Godot does not officially support .NET Web export.

## Export

Use the templates, four Godot NuGet packages, and `assemble-export.py` from the
same release. Add the packages as a NuGet restore source. Use a fresh
`NUGET_PACKAGES` directory when switching releases.

Publish for `browser-wasm` with invariant globalization. Export a PCK from the
same build with the `dotnet` custom feature, then run:

```sh
python3 assemble-export.py --template web_debug.zip \
  --publish path/to/publish --pack path/to/game.pck --output site/game.html
```

Use `web_release.zip` for Release. Copy application web assets into the site;
Kirie expects them at `src-web/dist/`.

Serve the output through HTTPS or localhost with these headers:

```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

Cross-origin assets also need suitable CORS or CORP headers.

## Compatibility

- Requires WebAssembly threads. Defaults: 24 Emscripten workers, 4 Godot workers.
- Tested in Chromium. Firefox and Safari are untested.
- Uses the Mono interpreter with jiterpreter traces disabled.
- Kirie CLI 0.14.1 does not support this export format.

## Build

Install Docker, then run:

```sh
./scripts/prepare-source.sh .tmp/godot
./scripts/build.sh .tmp/godot .tmp/output
```

Release archives are written to `.tmp/output/dist/`.
See [development notes](docs/development.md) for runtime integration and tests.

## Credits and licenses

Based on Raul Santos's [Godot .NET Web draft](https://github.com/godotengine/godot/pull/106125).
Source commits and tool versions are pinned in [versions.env](versions.env).
See [NOTICE.md](NOTICE.md) for Godot and .NET license notices.
