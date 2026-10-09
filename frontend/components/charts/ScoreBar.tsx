/** Horizontal score bar with ± whisker on a 0-max scale. */
export function ScoreBar({ score, pm, max = 10, color = "#0284c7", highlight = false }: { score: number; pm: number; max?: number; color?: string; highlight?: boolean }) {
  const p = (v: number) => `${Math.max(0, Math.min(100, (v / max) * 100))}%`;
  return (
    <div className="relative h-3 w-full rounded-full bg-sky-100" title={`${score.toFixed(2)} ± ${pm.toFixed(2)}`}>
      <div className="absolute inset-y-0 left-0 rounded-full" style={{ width: p(score), background: color, opacity: highlight ? 1 : 0.8 }} />
      <div className="absolute top-1/2 h-[2px] -translate-y-1/2 bg-slate-700" style={{ left: p(score - pm), width: `calc(${p(score + pm)} - ${p(score - pm)})` }} />
      <div className="absolute top-0 h-3 w-[2px] bg-slate-700" style={{ left: p(score - pm) }} />
      <div className="absolute top-0 h-3 w-[2px] bg-slate-700" style={{ left: p(score + pm) }} />
    </div>
  );
}

/** Weight range over which the current leader stays on top, with the current weight marked. */
export function RangeBar({ from, to, current }: { from: number; to: number; current: number }) {
  return (
    <div className="relative h-3 w-full rounded-full bg-rose-100">
      <div className="absolute inset-y-0 rounded-full bg-emerald-500/80" style={{ left: `${from * 100}%`, width: `${(to - from) * 100}%` }} />
      <div className="absolute -top-1 h-5 w-[3px] rounded bg-sky-950" style={{ left: `calc(${current * 100}% - 1px)` }} />
    </div>
  );
}
