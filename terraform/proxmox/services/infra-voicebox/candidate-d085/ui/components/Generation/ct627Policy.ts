/** Candidate-only UI contract. A package/label alone never enables a heavy engine. */
export type Availability = Record<string, { ready: boolean; languages?: string[]; model_sizes?: string[] }>;
export function isOptionAvailable(option: { engine: string; value: string }, caps: Availability): boolean {
  if (caps[option.engine]?.ready !== true) return false;
  if (option.engine === 'qwen') return option.value === 'qwen:0.6B';
  return ['kokoro', 'piper', 'chatterbox', 'chatterbox_turbo'].includes(option.engine);
}

// Admission limit only; complete generation at this length is not validated.
export const CHATTERBOX_MAX_CHARS = 1200;
export function textLimit(engine: string): number { return engine === 'chatterbox' ? CHATTERBOX_MAX_CHARS : engine === 'qwen' ? 1200 : 50000; }
