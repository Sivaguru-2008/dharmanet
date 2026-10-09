"use client";
import { useState } from "react";
import type { Ctx } from "./ctx";
import { api } from "@/lib/api";
import { f2 } from "@/lib/format";

const LIKERT = [
  ["usefulness", "The analysis was useful for my decision"],
  ["transparency", "I understand why options were scored as they were"],
  ["trust_calibration", "The stated uncertainty matched how confident I should be"],
  ["cultural_relevance", "The Dharma-inspired perspective was relevant and respectful"],
  ["decision_confidence", "I feel more confident in my own decision"],
] as const;

export function DecisionView({ r, setR, label }: Ctx) {
  const rec = r.matrix.recommendation;
  const alt = rec.runner_up_id;
  const [choice, setChoice] = useState<string>(r.decision?.choice ?? "");
  const [actionId, setActionId] = useState<string>(r.decision?.action_id ?? alt ?? "");
  const [note, setNote] = useState(r.decision?.note ?? "");
  const [msg, setMsg] = useState("");
  const [useful, setUseful] = useState<boolean | null>(null);
  const [ratings, setRatings] = useState<Record<string, number>>({});
  const [comment, setComment] = useState("");
  const [fbDone, setFbDone] = useState(false);

  async function record() {
    try {
      const d = await api.decide(r.id, choice, choice === "accept" ? rec.action_id : choice === "reject" ? null : actionId, note);
      setR({ ...r, decision: d as never });
      setMsg(String(d.statement));
    } catch (e) { setMsg((e as Error).message); }
  }

  const options = [
    ["accept", "Accept analysis", "Go with the highest-scoring option."],
    ["alternative", "Choose alternative", "Pick a different analysed option."],
    ["modify", "Modify decision", "Use an option as a base, with your own changes."],
    ["reject", "Reject recommendation", "None of these; I will decide otherwise."],
  ] as const;

  return (
    <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
      <div className="space-y-4">
        <section className="card space-y-3 text-sm">
          <h2 className="card-title">DharmaNet recommendation</h2>
          <div><span className="font-medium">Recommended option: </span>{label(rec.action_id)} ({f2(r.matrix.weighted[0].score)} ± {f2(r.matrix.weighted[0].uncertainty)})</div>
          <div><span className="font-medium">Why: </span>{r.explanation.principles.slice(0, 2).join(" ") || r.explanation.why}</div>
          <div><span className="font-medium">Important uncertainties: </span>{r.structured.uncertainties.slice(0, 2).join(" ")} Stability: {r.sensitivity.label}.</div>
          {alt && <div><span className="font-medium">Alternative: </span>{label(alt)} (margin {f2(rec.margin)}{rec.clear_preference ? "" : " — within uncertainty"})</div>}
          <p className="rounded-xl border border-sky-100 bg-sky-50/70 p-3.5 text-xs text-slate-600 leading-relaxed">
            “Reflect on this fully, then act as you choose” — a paraphrase of Bhagavad Gita 18.63, which DharmaNet adopts as its design
            principle. This analysis is decision support, not an autonomous moral judgment.
          </p>
        </section>

        <section className="card space-y-3">
          <h2 className="card-title">Human decision</h2>
          <div className="grid gap-2 sm:grid-cols-2">
            {options.map(([k, t, d]) => (
              <button key={k} onClick={() => setChoice(k)}
                className={`rounded-xl border p-3.5 text-left text-sm transition ${choice === k ? "border-sky-500 bg-sky-50/80 text-sky-950 shadow-sm" : "border-sky-100 bg-white text-slate-700 hover:border-sky-200"}`}>
                <div className="font-bold">{t}</div><div className="text-xs text-slate-500 mt-0.5">{d}</div>
              </button>
            ))}
          </div>
          {(choice === "alternative" || choice === "modify") && (
            <select className="input" value={actionId} onChange={(e) => setActionId(e.target.value)}>
              {r.matrix.weighted.map((w) => <option key={w.action_id} value={w.action_id}>#{w.rank} {label(w.action_id)}</option>)}
            </select>
          )}
          <textarea className="input min-h-[80px]" placeholder="Your reasoning or modifications (optional)" value={note} onChange={(e) => setNote(e.target.value)} />
          <div className="flex items-center gap-3">
            <button className="btn-primary" disabled={!choice} onClick={record}>Record my decision</button>
            {msg && <span className="text-sm font-semibold text-emerald-700">{msg}</span>}
          </div>
          {r.decision && <p className="text-xs text-slate-500">Recorded: <strong className="text-sky-900">{r.decision.choice}</strong>{r.decision.action_id ? ` → ${label(r.decision.action_id)}` : ""}. Nothing is executed automatically.</p>}
        </section>
      </div>

      <section className="card space-y-3 text-sm">
        <h2 className="card-title">Was this analysis useful?</h2>
        <div className="flex gap-2">
          <button className={`btn-secondary ${useful === true ? "ring-2 ring-sky-500 font-bold text-sky-700 border-sky-300" : ""}`} onClick={() => setUseful(true)}>Useful</button>
          <button className={`btn-secondary ${useful === false ? "ring-2 ring-sky-500 font-bold text-sky-700 border-sky-300" : ""}`} onClick={() => setUseful(false)}>Not useful</button>
        </div>
        {LIKERT.map(([k, q]) => (
          <div key={k}>
            <div className="mb-1 text-xs font-medium text-slate-700">{q}</div>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((v) => (
                <button key={v} onClick={() => setRatings({ ...ratings, [k]: v })}
                  className={`h-8 w-8 rounded-lg border text-xs font-semibold transition ${ratings[k] === v ? "border-sky-600 bg-sky-600 text-white shadow-sm" : "border-sky-100 bg-white text-slate-700 hover:border-sky-300"}`}>{v}</button>
              ))}
            </div>
          </div>
        ))}
        <p className="text-xs text-slate-500">1 = strongly disagree, 5 = strongly agree</p>
        <textarea className="input min-h-[60px]" placeholder="Comments (optional)" value={comment} onChange={(e) => setComment(e.target.value)} />
        <button className="btn-secondary" disabled={fbDone || (useful === null && !Object.keys(ratings).length)}
          onClick={async () => { await api.feedback(r.id, useful, ratings, comment); setFbDone(true); }}>
          {fbDone ? "Thank you — recorded" : "Submit feedback"}
        </button>
        <div className="border-t border-sky-100 pt-3 text-xs">
          <a className="text-sky-700 font-semibold hover:underline" href={api.exportUrl(r.id)} target="_blank" rel="noreferrer">Export research record (JSON) ↗</a>
          <div className="mt-1 text-slate-500">Run {r.id} · {Object.entries(r.versions).filter(([k]) => !k.startsWith("prompt:")).map(([k, v]) => `${k.replace(/_version/, "")} ${v}`).join(" · ")}</div>
        </div>
      </section>
    </div>
  );
}
