/** Existing DSP presets; selection affects this generation, never the voice reference. */
export const REQUESTED_EFFECTS = ['Robotic', 'Radio', 'Echo Chamber', 'Deep Voice'] as const;
export function prioritizeGenerationEffects<T extends { name: string }>(presets: readonly T[]): T[] {
  const priority = new Map<string, number>(REQUESTED_EFFECTS.map((name, index) => [name, index] as const));
  return [...presets].sort((a, b) => (priority.get(a.name) ?? 1000) - (priority.get(b.name) ?? 1000));
}
