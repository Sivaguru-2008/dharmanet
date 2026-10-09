"use client";
import { useState } from "react";
import type { Ctx } from "./ctx";

function List({ items, tone }: { items: string[]; tone?: string }) {
  if (!items.length) return <span className="muted">—</span>;
  return <ul className={`list-disc space-y-0.5 pl-4 ${tone ?? ""}`}>{items.map((x) => <li key={x}>{x}</li>)}</ul>;
}

export function CompareView({ r, label, color }: Ctx) {
  const order = r.matrix.weighted.map((w) => w.action_id);
  const [sel, setSel] = useState<string[]>(order.slice(0, 3));
  const rows: [string, (c: (typeof r.comparison)[number]) => React.ReactNode][] = [
    ["Best dimensions", (c) => c.best_dimensions.join(", ")],
    ["Weakest dimensions", (c) => c.worst_dimensions.join(", ")],
    ["Ethical strengths", (c) => <List items={c.strengths} />],
    ["Ethical weaknesses", (c) => <List items={c.weaknesses} />],
    ["Stakeholders helped", (c) => <List items={c.stakeholders_helped} tone="text-emerald-700 dark:text-emerald-400" />],
    ["Stakeholders harmed", (c) => <List items={c.stakeholders_harmed} tone="text-rose-700 dark:text-rose-400" />],
    ["Short-term", (c) => c.short_term],
    ["Long-term", (c) => c.long_term],
    ["Risks", (c) => <List items={c.risks} />],
    ["Uncertainty", (c) => c.uncertainty],
    ["Framework disagreement", (c) => c.framework_disagreement],
    ["Dharma-inspired view", (c) => c.dharma_view || <span className="muted">not included</span>],
  ];
  const cols = sel.map((a) => r.comparison.find((c) => c.action_id === a)!).filter(Boolean);
  return (
    <div className="space-y-4">
      <section className="card">
        <h2 className="card-title">Choose up to 3 actions to compare</h2>
        <div className="flex flex-wrap gap-2">
          {order.map((a) => (
            <button key={a} disabled={!sel.includes(a) && sel.length >= 3}
              onClick={() => setSel(sel.includes(a) ? sel.filter((x) => x !== a) : [...sel, a])}
              className={`chip border px-3 py-1 text-sm disabled:opacity-30 ${sel.includes(a) ? "" : "opacity-50"}`} style={{ borderColor: color(a), color: color(a) }}>
              {label(a)}
            </button>
          ))}
        </div>
      </section>
      <section className="card overflow-x-auto">
        <table className="w-full min-w-[720px] text-sm">
          <thead>
            <tr>
              <th className="w-44" />
              {cols.map((c) => (
                <th key={c.action_id} className="p-2 text-left align-top">
                  <div className="mb-1 h-1 rounded" style={{ background: color(c.action_id) }} />
                  <div className="font-semibold">{c.label}</div>
                  <div className="text-xs font-normal muted">rank #{r.matrix.weighted.find((w) => w.action_id === c.action_id)?.rank}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map(([k, f]) => (
              <tr key={k} className="border-t border-sky-100 hover:bg-sky-50/30 transition">
                <td className="p-2.5 align-top text-xs font-semibold text-slate-700 bg-sky-50/20">{k}</td>
                {cols.map((c) => <td key={c.action_id} className="p-2.5 align-top text-slate-700 leading-relaxed">{f(c)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
