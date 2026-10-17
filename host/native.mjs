import Godot from './godot-native.mjs';
export default function createNative(configure) {
  let resolveReady, rejectReady;
  const ready = new Promise((resolve, reject) => { resolveReady = resolve; rejectReady = reject; });
  const native = Godot(original => configure({ ...original, ready }));
  native.then(resolveReady, rejectReady);
  return native;
}
