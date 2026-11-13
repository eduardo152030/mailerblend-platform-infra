import { useEffect, useState } from 'react';
import type { Availability } from './ct627Policy';
/** Candidate only. No preloads; failed or timed-out requests hide unavailable engines. */
export function useCT627Capabilities(): Availability {
  const [caps, setCaps] = useState<Availability>({});
  useEffect(() => {
    let alive = true;
    let inFlight: AbortController | undefined;
    const refresh = async () => {
      if (inFlight) return;
      const controller = new AbortController();
      inFlight = controller;
      const deadline = setTimeout(() => controller.abort(), 4000);
      try {
        const response = await fetch('/tts-capabilities', { cache: 'no-store', signal: controller.signal });
        if (!response.ok) throw new Error('capabilities unavailable');
        const value: Availability = await response.json();
        if (alive) setCaps(value);
      } catch {
        if (alive) setCaps({});
      } finally {
        clearTimeout(deadline);
        inFlight = undefined;
      }
    };
    void refresh();
    const timer = setInterval(() => void refresh(), 5000);
    return () => { alive = false; inFlight?.abort(); clearInterval(timer); };
  }, []);
  return caps;
}
