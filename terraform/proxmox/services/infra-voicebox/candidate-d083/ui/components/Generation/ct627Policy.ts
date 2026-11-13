/** Candidate-only UI contract. A package/label alone never enables a heavy engine. */
export type Availability = Record<string, { ready: boolean; languages?: string[]; model_sizes?: string[] }>;
export function isOptionAvailable(option: { engine: string; value: string }, caps: Availability): boolean {
  if (caps[option.engine]?.ready !== true) return false;
  if (option.engine === 'qwen') return option.value === 'qwen:0.6B';
  return ['kokoro', 'piper', 'chatterbox', 'chatterbox_turbo'].includes(option.engine);
}
