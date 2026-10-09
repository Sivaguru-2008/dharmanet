"use client";
import { useEffect, useState } from "react";
import type { Ctx } from "./ctx";
import { api } from "@/lib/api";
import { f1, pct } from "@/lib/format";
import type { KBEntry } from "@/types/api";
import { KBCard } from "./KBCard";

export function DharmaView({ r, label, color }: Ctx) {
  const [kb, setKb] = useState<Record<string, KBEntry>>({});
  useEffect(() => { api.knowledge().then((es) => setKb(Object.fromEntries(es.map((e) => [e.id, e])))); }, []);
  const dh = r.dharma;
  if (!dh) return <div className="card text-sm muted">The Dharma-inspired layer was not included in this analysis (ablation: “DharmaNet without Dharma”).</div>;
  const order = r.matrix.weighted.map((w) => w.action_id);
  const maxEffect = Math.max(0.5, ...dh.readings.flatMap((x) => x.contributions.map((c) => Math.abs(c.effect))));

  return (
    <div className="space-y-4">
      <section className="card border-sky-200 bg-sky-50/70 text-sm text-slate-800 shadow-sm">
        <p className="font-bold text-sky-950">A culturally contextualized interpretive layer — distinct from established Western ethical frameworks.</p>
        <p className="mt-1 text-slate-600">{dh.disclaimer} Every claim below cites a verified knowledge-base entry; {dh.dropped_claims > 0 ? `${dh.dropped_claims} unsupported claim(s) were removed by the citation validator.` : "no claims needed to be removed by the citation validator."} Source: <span className="font-semibold text-sky-900">{dh.source}</span>, KB v{dh.kb_version}.</p>
        <p className="mt-2 text-slate-700 font-medium leading-relaxed">{dh.overview}</p>
      </section>

      <section className="card">
        <h2 className="card-title">Reading of each action</h2>
        <div className="space-y-4">
          {order.map((a) => {
            const rd = dh.readings.find((x) => x.action_id === a)!;
            return (
              <div key={a} className="rounded-xl border border-sky-100 bg-white p-4 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="font-bold text-sky-950 flex items-center"><span className="mr-2 inline-block h-2.5 w-2.5 rounded-full" style={{ background: color(a) }} />{label(a)}</div>
                  <span className="text-xs text-slate-500">Dharma-inspired score <strong className="text-sky-900">{f1(rd.score)}</strong> ± {f1(rd.uncertainty)} · confidence {pct(rd.confidence)} (model-estimated)</span>
                </div>
                <p className="mt-2 text-sm text-slate-700 leading-relaxed">{rd.interpretation}</p>
                <div className="mt-3 space-y-1.5">
                  {rd.contributions.map((c) => (
                    <div key={c.concept} className="grid grid-cols-[minmax(0,1fr)_160px] items-center gap-3 text-xs md:grid-cols-[260px_160px_minmax(0,1fr)]">
                      <span className="truncate font-semibold text-sky-950" title={c.concept}>{c.concept}</span>
                      <div className="relative h-2 rounded-full bg-sky-100">
                        <div className="absolute inset-y-0 left-1/2 w-px bg-slate-400" />
                        <div className={`absolute inset-y-0 rounded-full ${c.effect >= 0 ? "bg-emerald-500" : "bg-rose-500"}`}
                          style={c.effect >= 0 ? { left: "50%", width: `${(c.effect / maxEffect) * 50}%` } : { right: "50%", width: `${(-c.effect / maxEffect) * 50}%` }} />
                      </div>
                      <span className="col-span-2 text-slate-600 md:col-span-1">{c.note} <span className="text-sky-700 font-medium">[{c.entry_ids.map((i) => kb[i]?.citation ?? i).join("; ")}]</span></span>
                    </div>
                  ))}
                </div>
                {rd.limitations.length > 0 && <p className="mt-2.5 text-xs text-slate-500"><span className="font-semibold text-slate-700">Limitations: </span>{rd.limitations.join(" ")}</p>}
              </div>
            );
          })}
        </div>
      </section>

      <section>
        <h2 className="card-title">Retrieved sources (ranked by relevance)</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {dh.retrieved.map((x) => kb[x.entry_id] ? <KBCard key={x.entry_id} e={kb[x.entry_id]} relevance={x.relevance} /> : (
            <div key={x.entry_id} className="card text-sm border-sky-100">{x.citation} — {x.concept}</div>
          ))}
        </div>
      </section>
    </div>
  );
}
