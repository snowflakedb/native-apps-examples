import { describe, expect, it } from 'vitest';
import { formatTick, niceTicks } from '../../components/chart-utils';

describe('niceTicks', () => {
  it('fits round ticks around the data instead of starting at zero', () => {
    expect(niceTicks(203, 228)).toEqual([200, 210, 220, 230]);
  });

  it('starts at zero when asked, for bar charts', () => {
    expect(niceTicks(40, 95, 5, true)).toEqual([0, 25, 50, 75, 100]);
  });

  it('handles a flat series', () => {
    expect(niceTicks(7, 7).length).toBeGreaterThan(1);
  });
});

describe('formatTick', () => {
  it('uses compact notation at every scale', () => {
    expect(formatTick(1_500)).toBe('1.5K');
    expect(formatTick(2_000_000_000)).toBe('2B');
    expect(formatTick(12)).toBe('12');
  });
});
