import { dotnet } from './dotnet.js';

export async function createGodot(moduleConfig, wasmResponse) {
  const response = await fetch(new URL('config.json', import.meta.url));
  if (!response.ok) throw new Error(`Cannot load .NET application config: ${response.status}`);
  const config = await response.json();
  config.pthreadPoolInitialSize = moduleConfig.emscriptenPoolSize;
  // Godot invokes managed callbacks on the UI thread. .NET 10 only allocates
  // jiterpreter tables on its managed workers, so use the Mono interpreter.
  config.runtimeOptions = [
    ...(config.runtimeOptions ?? []),
    '--no-jiterpreter-traces-enabled',
  ];
  const runtime = await dotnet
    .withConfig(config)
    .withModuleConfig(moduleConfig)
    .withResourceLoader((type) => type === 'dotnetwasm' ? wasmResponse : undefined)
    .create();
  return runtime.Module;
}
