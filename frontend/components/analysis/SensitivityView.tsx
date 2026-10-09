"use client";
import { useEffect, useRef, useState } from "react";
import type { Ctx } from "./ctx";
import { api } from "@/lib/api";
import { DIM_LABEL, f2, pct, stabilityTone } from "@/lib/format";
import { RangeBar, ScoreBar } from "@/components/charts/ScoreBar";
import type { WeightedScore } from "@/types/api";

const DEFAULTS: Record<string, number> = { consequences: 0.2, duty: 0.2, fairness: 0.15, virtue: 0.1, care: 0.1, stakeholder_impact: 0.15, dharma: 0.1 };

function Ranking({ title, list, label, color, top }: { title: string; list: WeightedScore[]; label: (a: string) => string; color: (a: string) => string; top: string }) {
  return (
    <div>
      <h3 className="mb-2 text-xs font-bold uppercase tracking-wider text-sky-950">{title}</h3>
      <div className="space-y-2">
        {list.map((w) => (
          <div key={w.action_id} className="grid grid-cols-[22px_minmax(0,1fr)_120px_76px] items-center gap-2 text-xs">
            <span className="text-slate-400 font-semibold">#{w.rank}</span>
            <span className={`truncate ${w.action_id === top ? "font-bold text-sky-950" : "text-slate-700"}`} title={label(w.action_id)}>{label(w.action_id)}</span>
            <ScoreBar score={w.score} pm={w.uncertainty} color={color(w.action_id)} highlight={w.rank === 1} />
            <span className="text-right tabular-nums text-slate-700 font-medium">{f2(w.score)} ±{f2(w.uncertainty)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SensitivityView({ r, setR, label, color }: Ctx) {
  const m = r.matrix;
  const s = r.sensitivity;
  const [w, setW] = useState<Record<string, number>>(m.weights);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const first = useRef(true);

  useEffect(() => {
    if (first.current) { first.current = false; return; }
    const t = setTimeout(async () => {
      setBusy(true);
      try { setR(await api.rescore(r.id, w)); setErr(""); } catch (e) { setErr((e as Error).message); }
      setBusy(false);
    }, 350);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [w]);

  const total = m.dimensions.reduce((acc, d) => acc + (w[d] ?? 0), 0) || 1;
  const preset = (vals: Record<string, number>) => setW(Object.fromEntries(m.dimensions.map((d) => [d, vals[d] ?? 0])));
  const changed = m.recommendation.action_id !== m.equal_weight_recommendation.action_id;

  return (
    <div className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-[360px_1fr]">
        <section className="card border border-sky-100 bg-white shadow-sm shadow-sky-100/50">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="card-title mb-0">Your Ethical Priorities</h2>
            {busy && <span className="text-xs text-sky-600 font-medium">updating…</span>}
          </div>
          <div className="space-y-3">
            {m.dimensions.map((d) => (
              <div key={d}>
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-800">{DIM_LABEL[d]}</span>
                  <span className="tabular-nums text-sky-700 font-bold">{pct((w[d] ?? 0) / total)}</span>
                </div>
                <input aria-label={`${DIM_LABEL[d]} weight`} type="range" min={0} max={1} step={0.01} value={w[d] ?? 0} className="w-full accent-sky-600"
                  onChange={(e) => setW({ ...w, [d]: +e.target.value })} />
              </div>
            ))}
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <button className="btn-secondary px-2.5 py-1 text-xs font-semibold" onClick={() => preset(DEFAULTS)}>Default</button>
            <button className="btn-secondary px-2.5 py-1 text-xs font-semibold" onClick={() => preset(Object.fromEntries(m.dimensions.map((d) => [d, 1])))}>Equal (1:1)</button>
            <button className="btn-secondary px-2.5 py-1 text-xs font-semibold" onClick={() => preset({ ...Object.fromEntries(m.dimensions.map((d) => [d, 0.1])), duty: 0.6 })}>Duty-first</button>
            <button className="btn-secondary px-2.5 py-1 text-xs font-semibold" onClick={() => preset({ ...Object.fromEntries(m.dimensions.map((d) => [d, 0.1])), consequences: 0.6 })}>Outcome-first</button>
            <button className="btn-secondary px-2.5 py-1 text-xs font-semibold" onClick={() => preset({ ...Object.fromEntries(m.dimensions.map((d) => [d, 0.1])), fairness: 0.6 })}>Fairness-first</button>
            <button className="btn-secondary px-2.5 py-1 text-xs font-semibold" onClick={() => preset({ ...Object.fromEntries(m.dimensions.map((d) => [d, 0.1])), dharma: 0.6 })}>Dharma-first</button>
          </div>
          <p className="mt-3 text-xs text-slate-500 leading-relaxed">
            Weights are automatically normalised to 100%. Re-ranking uses pure deterministic mathematics.
          </p>
          {err && <p className="mt-2 text-xs text-rose-600 bg-rose-50 p-2 rounded">{err}</p>}
        </section>
        <section className="card space-y-5 border border-sky-100 bg-white shadow-sm shadow-sky-100/50">
          <div className="grid gap-6 xl:grid-cols-2">
            <Ranking title="Your weights" list={m.weighted} label={label} color={color} top={m.recommendation.action_id} />
            <Ranking title="Equal weights" list={m.equal_weighted} label={label} color={color} top={m.equal_weight_recommendation.action_id} />
          </div>
          <p className={`rounded-lg p-3 text-sm border ${changed ? "bg-sky-50 border-sky-200 text-sky-950" : "bg-slate-50 border-slate-200 text-slate-700"}`}>
            {changed
              ? <>Your priorities change the leading option: <strong>{label(m.recommendation.action_id)}</strong> under your weights vs. <strong>{label(m.equal_weight_recommendation.action_id)}</strong> with equal weights.</>
              : <>The leading option is the same under your weights and equal weights.</>}
          </p>
        </section>
      </div>

      <section className="card border border-sky-100 bg-white shadow-sm shadow-sky-100/50">
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <h2 className="card-title mb-0">Recommendation Stability</h2>
          <span className={`chip px-3 py-1 text-sm font-semibold ${stabilityTone(s.label)}`}>{s.label}</span>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {([["Under weight perturbations", s.weight_stability, s.win_share_weights], ["Under score uncertainty", s.score_stability, s.win_share_scores]] as const).map(([t, v, share]) => (
            <div key={t}>
              <div className="text-sm text-slate-700"><span className="font-semibold text-sky-950">{t}:</span> leader stays first in <strong>{pct(v)}</strong> of samples</div>
              <div className="mt-2 space-y-1.5">
                {Object.entries(share).filter(([, x]) => x > 0).sort((a, b) => b[1] - a[1]).map(([a, x]) => (
                  <div key={a} className="grid grid-cols-[minmax(0,1fr)_1fr_40px] items-center gap-2 text-xs">
                    <span className="truncate font-medium text-slate-800">{label(a)}</span>
                    <div className="h-2 rounded bg-sky-50 border border-sky-100"><div className="h-2 rounded" style={{ width: pct(x), background: color(a) }} /></div>
                    <span className="text-right tabular-nums text-slate-600 font-semibold">{pct(x)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
