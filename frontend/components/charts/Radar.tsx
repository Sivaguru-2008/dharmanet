import { DIM_LABEL } from "@/lib/format";

interface Series { label: string; color: string; values: number[] }

/** Ethical-profile radar: one polygon per action on a 0-10 scale. */
export function Radar({ dims, series, size = 340 }: { dims: string[]; series: Series[]; size?: number }) {
  const pad = 70;
  const W = size + pad * 2;
  const c = W / 2;
  const R = size / 2;
  const ang = (i: number) => -Math.PI / 2 + (i * 2 * Math.PI) / dims.length;
  const pt = (i: number, v: number) => [c + Math.cos(ang(i)) * (R * v) / 10, c + Math.sin(ang(i)) * (R * v) / 10];
  return (
    <svg viewBox={`0 0 ${W} ${W}`} className="w-full max-w-[460px]" role="img" aria-label="Ethical profile radar chart">
      {[2, 4, 6, 8, 10].map((g) => (
        <polygon key={g} points={dims.map((_, i) => pt(i, g).join(",")).join(" ")} fill="none" className="stroke-sky-200" strokeWidth={1} />
      ))}
      {dims.map((d, i) => {
        const [x, y] = pt(i, 10);
        const [lx, ly] = pt(i, 11.6);
        return (
          <g key={d}>
            <line x1={c} y1={c} x2={x} y2={y} className="stroke-sky-200" />
            <text x={lx} y={ly} textAnchor={Math.abs(lx - c) < 5 ? "middle" : lx > c ? "start" : "end"} dominantBaseline="middle" className="fill-slate-600 font-semibold" fontSize={11}>
              {DIM_LABEL[d] ?? d}
            </text>
          </g>
        );
      })}
      {series.map((s) => (
        <g key={s.label}>
          <polygon points={s.values.map((v, i) => pt(i, v).join(",")).join(" ")} fill={s.color} fillOpacity={0.12} stroke={s.color} strokeWidth={2} />
          {s.values.map((v, i) => {
            const [x, y] = pt(i, v);
            return <circle key={i} cx={x} cy={y} r={3} fill={s.color}><title>{`${s.label} · ${DIM_LABEL[dims[i]]}: ${v.toFixed(1)}`}</title></circle>;
          })}
        </g>
      ))}
    </svg>
  );
}
