'use client';

import { useEffect, useRef, useState } from 'react';

/**
 * Renders `format(value)`. When `value` changes after the first render, it animates from the
 * previous value to the new one. The first render shows the real number with no animation, so
 * server-rendered numbers never flash. Respects reduced motion.
 */
export function CountUp({
  value,
  format,
  duration = 900,
}: {
  value: number;
  format: (n: number) => string;
  duration?: number;
}) {
  const [shown, setShown] = useState(value);
  const from = useRef(value);

  useEffect(() => {
    const start = from.current;
    from.current = value;
    if (start === value || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setShown(value);
      return;
    }
    let frame = 0;
    const t0 = performance.now();
    const tick = (t: number) => {
      const p = Math.min(1, (t - t0) / duration);
      setShown(start + (value - start) * (1 - Math.pow(1 - p, 3)));
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    // Cleanup leaves the final value, so a cancelled run never sticks part-way.
    return () => {
      cancelAnimationFrame(frame);
      setShown(value);
    };
  }, [value, duration]);

  return <>{format(shown)}</>;
}
