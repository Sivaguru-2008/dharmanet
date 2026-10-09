"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { humanize, stabilityTone } from "@/lib/format";
import type { AnalysisSummary } from "@/types/api";

export default function History() {
  const [items, setItems] = useState<AnalysisSummary[] | null>(null);
  const [err, setErr] = useState("");

  const load = () => api.list().then(setItems).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);

  async function remove(id: string) {
    if (!confirm("Permanently delete this analysis and its records?")) return;
    await api.remove(id);
    load();
  }

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between border-b border-sky-100 pb-3">
        <div>
          <h1 className="text-2xl font-extrabold text-sky-950">Analysis History</h1>
          <p className="text-xs text-slate-500 mt-1">Every run stores its model, versions, weights and seed so it can be reproduced.</p>
        </div>
        <Link href="/new" className="btn-primary text-xs shadow-sm">New Dilemma</Link>
      </div>
      {err && <p className="text-sm text-rose-600 bg-rose-50 border border-rose-200 p-3 rounded-lg">{err}</p>}
      {items && items.length === 0 && <div className="card text-sm text-slate-500 border border-sky-100 p-6 text-center">No analyses yet.</div>}
      <div className="space-y-2.5">
        {items?.map((a) => (
          <div key={a.id} className="card flex flex-col gap-2 p-4 md:flex-row md:items-center md:justify-between border border-sky-100 hover:border-sky-300 transition shadow-sm">
            <Link href={`/analysis/${a.id}`} className="min-w-0 flex-1">
              <div className="truncate font-bold text-sky-950">{a.summary}</div>
              <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
                <span>{new Date(a.created_at).toLocaleString()}</span>
                <span>· {humanize(a.domain)}</span>
                <span>· {a.provider}</span>
                {a.parent_id && <span className="text-sky-600">· revision of {a.parent_id}</span>}
              </div>
            </Link>
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="chip bg-sky-50 text-sky-800 border border-sky-200 font-semibold">Top: {a.recommended_label}</span>
              <span className={`chip font-semibold ${stabilityTone(a.stability)}`}>{a.stability}</span>
              {a.decision && <span className="chip bg-blue-100 text-blue-900 border border-blue-200 font-bold">Decision: {a.decision}</span>}
              <button className="btn-ghost px-2 py-1 text-xs text-rose-600 hover:bg-rose-50" onClick={() => remove(a.id)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
