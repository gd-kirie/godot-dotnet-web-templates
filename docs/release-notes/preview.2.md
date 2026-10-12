Preview 2 adds complete, platform-specific toolchains for Linux x64 and Apple
Silicon macOS. Each archive contains a matching patched Godot editor,
`GodotSharp`, Web templates, local Godot NuGet packages, the required export
patch, a schema v2 manifest, and license notices.

The Kirie CLI can install a published toolchain through `kirie doctor fix`.
Users do not need to compile Godot. The macOS editor has an ad hoc signature;
it is not notarized.

This remains an experimental build based on the unfinished official Godot
Draft pull request #106125. The Web templates do not use threads or
optimizations.
