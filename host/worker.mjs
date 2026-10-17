self.onmessage = async ({ data }) => {
  if (data.cmd !== 'load') throw new Error(`Expected worker load, received ${data.cmd}`);
  const { default: createDotnet } = await import('./dotnet.js');
  await createDotnet({
    ENVIRONMENT_IS_PTHREAD: true,
    wasmModule: data.wasmModule,
    wasmMemory: data.wasmMemory,
    godotWorkerLoad: data,
  });
};
