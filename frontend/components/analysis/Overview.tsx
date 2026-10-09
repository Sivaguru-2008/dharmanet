"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { Ctx } from "./ctx";
import { api } from "@/lib/api";
import { humanize, pct } from "@/lib/format";
import type { Action, Stakeholder } from "@/types/api";

const KINDS = ["direct", "escalate_internal", "escalate_external", "compromise", "gather_info", "delay", "status_quo", "custom"];
const ROLES = ["primary", "secondary", "vulnerable", "decision_maker", "direct", "indirect"];

export function Overview({ r, color }: Ctx) {
  const router = useRouter();
  const d = r.structured;
  const [sh, setSh] = useState<Stakeholder[]>(d.stakeholders);
  const [acts, setActs] = useState<Action[]>(d.actions);
  const [assumptions, setAssumptions] = useState(d.assumptions.join("\n"));
  const [extra, setExtra] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [newAct, setNewAct] = useState({ label: "", description: "", kind: "custom" });
  const [newSh, setNewSh] = useState("");

  const dirty = JSON.stringify(sh) !== JSON.stringify(d.stakeholders) || JSON.stringify(acts) !== JSON.stringify(d.actions)
    || assumptions !== d.assumptions.join("\n") || extra.trim() !== "";

  async function rerun() {
    setBusy(true); setErr("");
    try {
      const nr = await api.revise(r.id, {
        stakeholders: sh, actions: acts,
        assumptions: assumptions.split("\n").map((s) => s.trim()).filter(Boolean),
        additional_context: extra.trim() || undefined,
      });
      router.push(`/analysis/${nr.id}`);
    } catch (e) { setErr((e as Error).message); setBusy(false); }
  }

  const updSh = (i: number, patch: Partial<Stakeholder>) => setSh(sh.map((s, j) => (j === i ? { ...s, ...patch } : s)));

  return (
    <div className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
        <section className="card">
          <h2 className="card-title">Dilemma</h2>
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{d.dilemma_text}</p>
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            <span className="chip border border-sky-200 bg-sky-50 text-sky-800 font-semibold">Domain: {humanize(d.domain)}</span>
            <span className="chip border border-sky-200 bg-sky-50 text-sky-800 font-semibold">Decision-maker: {d.decision_maker}</span>
          </div>
          {d.constraints.length > 0 && (
            <div className="mt-3 text-sm"><span className="font-semibold text-slate-800">Constraints: </span><span className="text-slate-600">{d.constraints.join(" · ")}</span></div>
          )}
        </section>
        <section className="card">
          <h2 className="card-title">Context signals (estimated)</h2>
          <div className="space-y-1.5">
            {(["severity", "vulnerability", "urgency", "scale", "relational_closeness", "legal_dimension"] as const).map((k) => (
              <div key={k} className="grid grid-cols-[130px_1fr_36px] items-center gap-2 text-xs">
                <span className="text-slate-600 font-medium">{humanize(k)}</span>
                <div className="h-2 rounded-full bg-sky-100"><div className="h-2 rounded-full bg-sky-500" style={{ width: pct(d.cues[k]) }} /></div>
                <span className="text-right tabular-nums font-semibold text-sky-950">{d.cues[k].toFixed(2)}</span>
              </div>
            ))}
          </div>
          {d.cues.evidence.length > 0 && <p className="mt-2.5 text-xs text-slate-500">Evidence: {d.cues.evidence.join("; ")}</p>}
        </section>
      </div>

      <section className="card">
        <h2 className="card-title">Ethical conflicts</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {d.conflicts.map((c) => (
            <div key={c.id} className="rounded-xl border border-sky-100 bg-white p-3.5 shadow-sm">
              <div className="flex items-center justify-between gap-2">
                <div className="font-bold text-sky-950">{c.title}</div>
                <span className="text-xs text-slate-500">intensity {c.intensity.toFixed(2)}</span>
              </div>
              <div className="my-2 h-1.5 rounded-full bg-sky-100"><div className="h-1.5 rounded-full bg-rose-500" style={{ width: pct(c.intensity) }} /></div>
              <p className="text-sm text-slate-600 leading-relaxed">{c.description}</p>
              {c.between.length > 0 && <p className="mt-1.5 text-xs text-slate-500">Between: {c.between.map((b) => sh.find((s) => s.id === b)?.name ?? b).join(" ↔ ")}</p>}
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="card-title mb-0">Stakeholders <span className="normal-case tracking-normal text-xs text-slate-500 font-normal">(editable)</span></h2>
        </div>
        <div className="space-y-3">
          {sh.map((s, i) => (
            <div key={s.id} className="rounded-xl border border-sky-100 bg-white p-3.5 shadow-sm">
              <div className="flex flex-wrap items-center gap-2">
                <input className="input max-w-xs font-semibold text-sky-950" value={s.name} onChange={(e) => updSh(i, { name: e.target.value })} />
                <label className="flex items-center gap-1 text-xs text-slate-600 font-medium">salience
                  <input type="range" min={0} max={1} step={0.05} value={s.salience} onChange={(e) => updSh(i, { salience: +e.target.value })} />
                  <span className="w-8 tabular-nums font-semibold text-sky-900">{s.salience.toFixed(2)}</span>
                </label>
                {s.category !== "decision_maker" && (
                  <button className="btn-ghost px-2 py-1 text-xs text-rose-600" onClick={() => setSh(sh.filter((_, j) => j !== i))}>Remove</button>
                )}
                {s.user_edited && <span className="chip border border-sky-200 bg-sky-50 text-sky-700 font-semibold">edited</span>}
              </div>
              <div className="mt-2.5 flex flex-wrap gap-1">
                {ROLES.map((role) => (
                  <button key={role} onClick={() => updSh(i, { roles: s.roles.includes(role) ? s.roles.filter((x) => x !== role) : [...s.roles, role] })}
                    className={`chip border transition ${s.roles.includes(role) ? (role === "vulnerable" ? "border-rose-300 bg-rose-50 text-rose-700 font-semibold" : "border-sky-300 bg-sky-50 text-sky-800 font-semibold") : "border-slate-200 text-slate-500"}`}>
                    {role.replace("_", " ")}
                  </button>
                ))}
              </div>
              <dl className="mt-2.5 grid gap-x-4 gap-y-1 text-xs md:grid-cols-3">
                {([["Interests", s.interests], ["Rights", s.rights], ["Responsibilities", s.responsibilities], ["Vulnerabilities", s.vulnerabilities], ["Potential benefits", s.potential_benefits], ["Potential harms", s.potential_harms]] as const).map(([k, v]) =>
                  v.length ? <div key={k}><dt className="font-semibold text-slate-700">{k}</dt><dd className="text-slate-500">{v.join("; ")}</dd></div> : null)}
              </dl>
            </div>
          ))}
          <div className="flex gap-2">
            <input className="input max-w-xs" placeholder="Add a stakeholder…" value={newSh} onChange={(e) => setNewSh(e.target.value)} />
            <button className="btn-secondary" disabled={!newSh.trim()} onClick={() => {
              setSh([...sh, { id: `u${Date.now().toString(36)}`, name: newSh.trim(), category: "other", roles: ["secondary"], interests: [], rights: [], responsibilities: [], vulnerabilities: [], potential_benefits: [], potential_harms: [], salience: 0.5, user_edited: true }]);
              setNewSh("");
            }}>Add</button>
          </div>
        </div>
      </section>

      <section className="card">
        <h2 className="card-title">Candidate actions <span className="normal-case tracking-normal text-xs text-slate-500 font-normal">(add or remove — none are removed automatically)</span></h2>
        <div className="space-y-2.5">
          {acts.map((a) => (
            <div key={a.id} className="flex items-start gap-3 rounded-xl border border-sky-100 bg-white p-3.5 shadow-sm">
              <span className="mt-1 h-3 w-3 shrink-0 rounded-full" style={{ background: color(a.id) }} />
              <div className="min-w-0 flex-1">
                <div className="font-bold text-sky-950">{a.label} <span className="chip ml-1 border border-sky-200 bg-sky-50 text-sky-800 font-medium">{a.kind.replace(/_/g, " ")}</span>
                  {a.user_added && <span className="chip ml-1 border border-sky-200 bg-sky-100 text-sky-800 font-bold">added by you</span>}</div>
                <p className="text-sm text-slate-600 mt-0.5">{a.description}</p>
              </div>
              <button className="btn-ghost px-2 py-1 text-xs text-rose-600" disabled={acts.length <= 2} onClick={() => setActs(acts.filter((x) => x.id !== a.id))}>Remove</button>
            </div>
          ))}
          <div className="grid gap-2 rounded-xl border border-dashed border-sky-200 bg-sky-50/40 p-3.5 md:grid-cols-[1fr_1.5fr_160px_auto]">
            <input className="input" placeholder="New action label" value={newAct.label} onChange={(e) => setNewAct({ ...newAct, label: e.target.value })} />
            <input className="input" placeholder="Description" value={newAct.description} onChange={(e) => setNewAct({ ...newAct, description: e.target.value })} />
            <select className="input" value={newAct.kind} onChange={(e) => setNewAct({ ...newAct, kind: e.target.value })}>
              {KINDS.map((k) => <option key={k} value={k}>{k.replace(/_/g, " ")}</option>)}
            </select>
            <button className="btn-secondary" disabled={!newAct.label.trim()} onClick={() => {
              setActs([...acts, { id: `u${Date.now().toString(36)}`, label: newAct.label.trim(), description: newAct.description, kind: newAct.kind, features: {}, user_added: true }]);
              setNewAct({ label: "", description: "", kind: "custom" });
            }}>Add</button>
          </div>
          <p className="text-xs text-slate-500">New actions take the feature profile of their type; “custom” actions start neutral (0.5) in the offline engine.</p>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2">
        <section className="card">
          <h2 className="card-title">Assumptions (one per line, editable)</h2>
          <textarea className="input min-h-[120px]" value={assumptions} onChange={(e) => setAssumptions(e.target.value)} />
        </section>
        <section className="card">
          <h2 className="card-title">Uncertainties & additional context</h2>
          <ul className="mb-3 list-disc space-y-1 pl-5 text-sm text-slate-600">{d.uncertainties.map((u) => <li key={u}>{u}</li>)}</ul>
          <textarea className="input min-h-[70px]" placeholder="Add facts that might resolve these uncertainties…" value={extra} onChange={(e) => setExtra(e.target.value)} />
        </section>
      </div>

      <div className="sticky bottom-4 flex items-center justify-end gap-3">
        {err && <span className="text-sm text-rose-600">{err}</span>}
        <button className="btn-primary shadow-lg" disabled={!dirty || busy} onClick={rerun}>
          {busy ? "Re-analysing…" : dirty ? "Re-analyse with my edits" : "Edit above to re-analyse"}
        </button>
      </div>
    </div>
  );
}
