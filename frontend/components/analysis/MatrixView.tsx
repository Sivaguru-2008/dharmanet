"use client";
import { useState } from "react";
import type { Ctx } from "./ctx";
import { DIM_LABEL, f1, f2, heat, pct } from "@/lib/format";
import { Radar } from "@/components/charts/Radar";

export function MatrixView({ r, label, color }: Ctx) {
  const m = r.matrix;
  const [sel, setSel] = useState<{ a: string; d: string }>({ a: m.recommendation.action_id, d: m.dimensions[0] });
  const [shown, setShown] = useState<string[]>(m.weighted.slice(0, 3).map((w) => w.action_id));
  const ws = Object.fromEntries(m.weighted.map((w) => [w.action_id, w]));
  const order = m.weighted.map((w) => w.action_id);

  const detail = (() => {
    if (sel.d === "dharma") {
      const rd = r.dharma?.readings.find((x) => x.action_id === sel.a);
      return rd ? { kind: "dharma" as const, rd } : null;
    }
    for (const ev of r.evaluations) {
      const s = ev.scores.find((x) => x.action_id === sel.a && x.dimension === sel.d);
      if (s) return { kind: "fw" as const, s, ev };
    }
    return null;
  })();

  const impacts = r.evaluations.find((e) => e.stakeholder_impacts.length)?.stakeholder_impacts ?? [];

  return (
    <div className="space-y-4">
      <section className="card overflow-x-auto space-y-3 border border-sky-100 bg-white shadow-sm shadow-sky-100/50">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-sky-100 pb-3">
          <div>
            <h2 className="card-title mb-0">Multi-Framework Decision Matrix</h2>
            <p className="mt-1 text-xs text-slate-500">
              Click any cell to inspect its philosophical rationale, assumptions, strengths, and weaknesses. Columns are sorted by weighted rank.
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1.5 font-medium text-slate-600"><span className="h-3 w-3 rounded bg-sky-500/30 border border-sky-500" /> High alignment (&gt;6.0)</span>
            <span className="flex items-center gap-1.5 font-medium text-slate-600"><span className="h-3 w-3 rounded bg-slate-200 border border-slate-300" /> Mixed / neutral</span>
            <span className="flex items-center gap-1.5 font-medium text-slate-600"><span className="h-3 w-3 rounded bg-rose-500/30 border border-rose-500" /> Ethical concern (&lt;4.0)</span>
          </div>
        </div>
        <table className="w-full min-w-[720px] border-separate border-spacing-1 text-sm">
          <thead>
            <tr>
              <th className="w-44 text-left text-xs font-bold text-sky-900">Dimension (weight)</th>
              {order.map((a) => (
                <th key={a} className="align-bottom text-left text-xs font-bold text-sky-950">
                  <span className="mr-1.5 inline-block h-2 w-2 rounded-full" style={{ background: color(a) }} />{label(a)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {m.dimensions.map((d) => (
              <tr key={d}>
                <td className="text-xs py-1"><span className="font-semibold text-slate-800">{DIM_LABEL[d]}</span> <span className="text-slate-400">({pct(m.weights[d])})</span></td>
                {order.map((a) => {
                  const c = m.cells[a][d];
                  const active = sel.a === a && sel.d === d;
                  return (
                    <td key={a}>
                      <button onClick={() => setSel({ a, d })} style={{ background: heat(c.score) }}
                        className={`w-full rounded-lg px-2.5 py-2 text-left tabular-nums transition border ${active ? "ring-2 ring-sky-500 border-sky-500" : "border-transparent hover:border-sky-300"}`}
                        title={`${label(a)} · ${DIM_LABEL[d]}`}>
                        <span className="font-bold text-slate-900">{f1(c.score)}</span> <span className="text-xs text-slate-500">±{f1(c.uncertainty)}</span>
                      </button>
                    </td>
                  );
                })}
              </tr>
            ))}
            <tr>
              <td className="pt-3 text-xs font-bold text-sky-950">Weighted total</td>
              {order.map((a) => (
                <td key={a} className="pt-3 text-sm tabular-nums">
                  <span className="font-extrabold text-sky-950">{f2(ws[a].score)}</span> <span className="text-xs text-slate-400">±{f2(ws[a].uncertainty)} · #{ws[a].rank}</span>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </section>

      <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
        <section className="card border border-sky-100 bg-white shadow-sm shadow-sky-100/50">
          <h2 className="card-title">{label(sel.a)} · {DIM_LABEL[sel.d]}</h2>
          {detail?.kind === "fw" && (
            <div className="space-y-3 text-sm">
              <div className="flex flex-wrap gap-2 text-xs">
                <span className="chip bg-sky-50 text-sky-800 border border-sky-200 font-semibold">Score {f1(detail.s.score)} ± {f1(detail.s.uncertainty)}</span>
                <span className="chip bg-sky-50 text-sky-800 border border-sky-200">Confidence {pct(detail.s.confidence)}</span>
                <span className="chip bg-white border border-slate-200 text-slate-600">{detail.ev.framework_name} · {detail.ev.source}</span>
                {detail.s.flags.map((f) => <span key={f} className="chip bg-rose-50 text-rose-700 border border-rose-200">{f.replace(/_/g, " ")}</span>)}
              </div>
              <p><strong className="text-slate-800">Principle: </strong>{detail.s.principle}</p>
              <p><strong className="text-slate-800">Rationale: </strong>{detail.s.rationale}</p>
              {detail.s.strengths.length > 0 && <p><strong className="text-emerald-700">Strengths: </strong>{detail.s.strengths.join("; ")}</p>}
              {detail.s.weaknesses.length > 0 && <p><strong className="text-rose-700">Weaknesses: </strong>{detail.s.weaknesses.join("; ")}</p>}
              <p><strong className="text-slate-700">Assumptions: </strong><span className="text-slate-500">{detail.s.assumptions.join(" ")}</span></p>
              {detail.s.uncertainties.length > 0 && <p><strong className="text-slate-700">Uncertainty: </strong><span className="text-slate-500">{detail.s.uncertainties.join(" ")}</span></p>}
              {detail.s.evidence.length > 0 && <p><strong className="text-slate-700">Evidence used: </strong><span className="text-slate-500">{detail.s.evidence.join("; ")}</span></p>}
              <p><strong className="text-slate-700">Potential disagreement: </strong>{detail.s.potential_disagreement}</p>
            </div>
          )}
          {detail?.kind === "dharma" && (
            <div className="space-y-2 text-sm">
              <span className="chip bg-sky-50 text-sky-800 border border-sky-200 font-semibold">Score {f1(detail.rd.score)} ± {f1(detail.rd.uncertainty)}</span>
              <p className="text-slate-700">{detail.rd.interpretation}</p>
              <ul className="space-y-1">
                {detail.rd.contributions.map((c) => (
                  <li key={c.concept} className="text-xs"><span className={c.effect >= 0 ? "font-bold text-sky-600" : "font-bold text-rose-600"}>{c.effect >= 0 ? "+" : ""}{c.effect.toFixed(2)}</span> {c.concept} <span className="text-slate-400">[{c.entry_ids.join(", ")}]</span></li>
                ))}
              </ul>
              <p className="text-xs text-slate-400">See the Dharma perspective tab for sources and limitations.</p>
            </div>
          )}
        </section>

        <section className="card border border-sky-100 bg-white shadow-sm shadow-sky-100/50">
          <h2 className="card-title">Ethical Profile Radar</h2>
          <div className="mb-2 flex flex-wrap gap-1">
            {order.map((a) => (
              <button key={a} onClick={() => setShown(shown.includes(a) ? shown.filter((x) => x !== a) : [...shown, a])}
                className={`chip border text-xs font-semibold ${shown.includes(a) ? "bg-sky-50" : "opacity-40"}`} style={{ borderColor: color(a), color: color(a) }}>
                {label(a)}
              </button>
            ))}
          </div>
          <div className="flex justify-center pt-2">
            <Radar dims={m.dimensions} series={shown.map((a) => ({ label: label(a), color: color(a), values: m.dimensions.map((d) => m.cells[a][d].score) }))} />
          </div>
        </section>
      </div>

      {impacts.length > 0 && (
        <section className="card overflow-x-auto border border-sky-100 bg-white shadow-sm shadow-sky-100/50">
          <h2 className="card-title">Stakeholder Impact (−1 harmed … +1 helped)</h2>
          <table className="w-full min-w-[640px] border-separate border-spacing-1 text-xs">
            <thead><tr><th className="text-left font-bold text-slate-600">Stakeholder</th>{order.map((a) => <th key={a} className="text-left font-bold text-sky-950">{label(a)}</th>)}</tr></thead>
            <tbody>
              {r.structured.stakeholders.map((s) => (
                <tr key={s.id}>
                  <td className="whitespace-nowrap pr-2 font-medium text-slate-800">{s.name}{s.roles.includes("vulnerable") && <span className="ml-1 text-rose-600 font-bold">●</span>}</td>
                  {order.map((a) => {
                    const v = impacts.find((i) => i.action_id === a && i.stakeholder_id === s.id)?.impact ?? 0;
                    return <td key={a} className="rounded-md px-2.5 py-1.5 tabular-nums border border-slate-100" style={{ background: heat(5 + 5 * v) }} title={impacts.find((i) => i.action_id === a && i.stakeholder_id === s.id)?.note}>{v >= 0 ? "+" : ""}{v.toFixed(2)}</td>;
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-2 text-xs text-slate-400">● vulnerable stakeholder (weighted 1.5× in the stakeholder-impact dimension).</p>
        </section>
      )}
    </div>
  );
}
