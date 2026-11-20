'use client';

/**
 * Shared chart utilities — library-agnostic.
 *
 * Import these into any chart component (Recharts, Nivo, etc.) to avoid
 * the two most common usability issues in generated apps:
 *   1. Y-axis labels clipped for large numbers  → getYAxisWidth
 *   2. Tooltip text illegible on dark backgrounds → ChartTooltip
 *   3. Colors that ignore the theme              → CHART_COLORS / CHART_THEME
 *
 * Add the chart library of your choice to package.json separately.
 */

/**
 * Series colors from the --chart-1..5 tokens in app/globals.css. They follow
 * the brand color and switch automatically in dark mode.
 *
 * Recharts:  <Bar dataKey="orders" fill={CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
 */
export const CHART_COLORS = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-4)',
  'var(--chart-5)',
] as const;

/**
 * Grid and axis styling that matches the theme.
 *
 * Recharts:  <CartesianGrid stroke={CHART_THEME.grid} vertical={false} />
 *            <XAxis tick={CHART_THEME.tick} axisLine={false} tickLine={false} />
 */
export const CHART_THEME = {
  grid: 'var(--chart-grid)',
  axis: 'var(--chart-axis)',
  tick: { fill: 'var(--chart-axis)', fontSize: 12 },
} as const;

/**
 * Compute the pixel width needed for a chart's Y-axis so tick labels never
 * overflow the SVG boundary. Measures the widest formatted label using the
 * Canvas 2D API; falls back to a character-width estimate for SSR.
 *
 * Recharts:  <YAxis width={getYAxisWidth(data, "revenue")} tickFormatter={formatTick} />
 * Nivo:      margin={{ left: getYAxisWidth(data, "revenue") }}
 */
export function getYAxisWidth(data: Record<string, unknown>[], key: string, fontSize = 12): number {
  const maxVal = Math.max(...data.map((d) => Math.abs(Number(d[key]) || 0)));
  const label = formatTick(maxVal);

  if (typeof document !== 'undefined') {
    try {
      const ctx = document.createElement('canvas').getContext('2d');
      if (ctx) {
        ctx.font = `${fontSize}px sans-serif`;
        return Math.ceil(ctx.measureText(label).width) + 20;
      }
    } catch {
      // SSR or canvas unavailable — fall through to estimate
    }
  }

  return Math.max(40, label.length * 8 + 20); // ~8 px/char fallback
}

/**
 * Format a numeric tick value with K/M abbreviation.
 * Pass this to the YAxis `tickFormatter` prop alongside `getYAxisWidth`.
 */
export function formatTick(value: number): string {
  return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 2 }).format(
    value,
  );
}

/**
 * Round, evenly spaced axis ticks that fit the data, so a trend is visible
 * instead of flattened against zero. Pass `includeZero` for bar charts, whose
 * bars must start at zero.
 *
 * Recharts:  const ticks = niceTicks(min, max)
 *            <YAxis domain={[ticks[0], ticks.at(-1)!]} ticks={ticks} tickFormatter={formatTick} />
 * For bytes or money, use lib/format.ts (formatBytes, formatCurrency) as the tickFormatter.
 */
export function niceTicks(min: number, max: number, count = 5, includeZero = false): number[] {
  let lo = includeZero ? Math.min(0, min) : min;
  let hi = includeZero ? Math.max(0, max) : max;
  if (lo === hi) {
    lo -= 1;
    hi += 1;
  }
  const raw = (hi - lo) / Math.max(1, count - 1);
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = ([1, 2, 2.5, 5, 10].find((m) => m * mag >= raw) ?? 10) * mag;
  const start = Math.floor(lo / step) * step;
  const ticks: number[] = [];
  for (let v = start; v <= hi + step / 2; v += step) ticks.push(Number(v.toPrecision(12)));
  return ticks;
}

interface TooltipPayloadEntry {
  name: string;
  value: number;
  color: string;
  dataKey: string;
}

interface ChartTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}

/**
 * Chart tooltip with explicit popover styles.
 *
 * Default chart tooltips inherit colors from the DOM, which produces
 * near-invisible text when both the tooltip and chart canvas are dark.
 * This component uses CSS variables from globals.css and is readable on
 * any background theme.
 *
 * Recharts:  <Tooltip content={<ChartTooltip />} />
 * Nivo:      tooltip={({ ... }) => <ChartTooltip active ... />}
 */
export function ChartTooltip({ active, payload, label }: ChartTooltipProps) {
  if (!active || !payload?.length) return null;

  return (
    <div
      style={{
        background: 'var(--popover)',
        color: 'var(--popover-foreground)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '8px 12px',
        fontSize: 12,
        boxShadow: '0 8px 24px rgba(15,23,42,0.18)',
        minWidth: 120,
      }}
    >
      {label && <p style={{ marginBottom: 4, fontWeight: 600, marginTop: 0 }}>{label}</p>}
      {payload.map((entry) => (
        <p key={entry.dataKey} style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: 2, background: entry.color }} />
          <span style={{ color: 'var(--muted-foreground)' }}>{entry.name}</span>
          <span style={{ marginLeft: 'auto', fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>
            {Number(entry.value).toLocaleString()}
          </span>
        </p>
      ))}
    </div>
  );
}
