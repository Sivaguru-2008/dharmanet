"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { ACTION_COLORS, f2, stabilityTone } from "@/lib/format";
import type { AnalysisResult } from "@/types/api";
import type { Ctx, Tab } from "@/components/analysis/ctx";
import { Overview } from "@/components/analysis/Overview";
import { MatrixView } from "@/components/analysis/MatrixView";
import { DharmaView } from "@/components/analysis/DharmaView";
import { ExplanationView } from "@/components/analysis/ExplanationView";
import { CompareView } from "@/components/analysis/CompareView";
import { SensitivityView } from "@/components/analysis/SensitivityView";
import { DecisionView } from "@/components/analysis/DecisionView";

const TABS: { id: Tab; step: string; label: string }[] = [
  { id: "overview", step: "1", label: "Structuring" },
  { id: "matrix", step: "2", label: "Ethical Matrix" },
  { id: "dharma", step: "3", label: "Dharma Perspective" },
  { id: "explanation", step: "4", label: "Reasoning Trace" },
  { id: "compare", step: "5", label: "Trade-off Compare" },
  { id: "sensitivity", step: "6", label: "Weights & Sensitivity" },
  { id: "decision", step: "7", label: "Human Decision" },
];

export default function AnalysisPage() {
  const { id } = useParams<{ id: string }>();
  const [r, setR] = useState<AnalysisResult | null>(null);
  const [err, setErr] = useState("");
  const [tab, setTab] = useState<Tab>("overview");

  useEffect(() => {
    const h = window.location.hash.slice(1) as Tab;
    if (TABS.some((t) => t.id === h)) setTab(h);
    api.get(id).then(setR).catch((e) => setErr(e.message));
  }, [id]);

  const go = (t: Tab) => {
    setTab(t);
    history.replaceState(null, "", `#${t}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const ctx = useMemo<Ctx | null>(() => {
    if (!r) return null;
    const labels = Object.fromEntries(r.structured.actions.map((a) => [a.id, a.label]));
    const colors = Object.fromEntries(
      r.structured.actions.map((a, i) => [a.id, ACTION_COLORS[i % ACTION_COLORS.length]])
    );
    return { r, setR, label: (i) => labels[i] ?? i, color: (i) => colors[i] ?? "#0284c7", go };
  }, [r]);

  if (err) return <div className="card text-rose-700 bg-rose-50 border border-rose-200 p-6">Could not load analysis: {err}</div>;
  if (!ctx || !r) return <div className="card animate-pulse p-8 text-center text-sm text-slate-500">Loading multi-framework analysis…</div>;

  const rec = r.matrix.recommendation;
  const top = r.matrix.weighted[0];
  const currentIndex = TABS.findIndex((t) => t.id === tab);

  return (
    <div className="space-y-5">
      {/* Top Header Card */}
      <section className="card border border-sky-100 bg-white p-5 md:p-6 shadow-sm shadow-sky-100/50">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0 flex-1 space-y-2">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="font-bold uppercase tracking-wider text-sky-800">
                {rec.clear_preference
                  ? "Leading Recommendation (Under Specified Weights)"
                  : "No Clear Preference — Multiple Options Within Uncertainty"}
              </span>
              <span className={`chip font-semibold ${stabilityTone(r.sensitivity.label)}`}>
                Stability: {r.sensitivity.label}
              </span>
              {r.parent_id && (
                <Link href={`/analysis/${r.parent_id}`} className="chip bg-sky-50 text-sky-700 border border-sky-200 hover:underline">
                  Revision of {r.parent_id}
                </Link>
              )}
            </div>

            <h1 className="text-2xl font-extrabold tracking-tight text-sky-950">
              {ctx.label(rec.action_id)}
            </h1>

            <p className="text-sm font-semibold text-slate-700">
              {rec.statement}
            </p>

            <p className="text-xs text-slate-600 leading-relaxed">
              {r.explanation.why.replace(rec.statement, "").trim()}
            </p>
          </div>

          {/* Right score card */}
          <div className="shrink-0 rounded-xl border border-sky-100 bg-sky-50/60 p-4 text-sm min-w-[210px] shadow-sm">
            <div className="text-xs font-semibold text-sky-800">Aggregate Weighted Score</div>
            <div className="mt-1 text-2xl font-black text-sky-950">
              {f2(top.score)} <span className="text-sm font-normal text-slate-500">± {f2(top.uncertainty)}</span>
            </div>
            <div className="mt-1 text-xs text-slate-500 font-medium">
              Confidence: {Math.round(top.confidence * 100)}% (model-estimated)
            </div>
            <button
              className="btn-primary mt-3 w-full text-xs font-bold shadow-sm"
              onClick={() => go("decision")}
            >
              Make Final Human Decision →
            </button>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between border-t border-sky-100 pt-3 text-xs text-slate-500">
          <span>
            Engine: <strong>{r.provider.provider}</strong> ({r.provider.model}) · Seed: {r.seed}
            {r.fallbacks.length > 0 && <> · Fallbacks: {r.fallbacks.join("; ")}</>}
          </span>
          <a
            href={api.exportUrl(r.id)}
            target="_blank"
            rel="noreferrer"
            className="hover:underline font-semibold text-sky-700"
          >
            Export Research Record JSON ↗
          </a>
        </div>
      </section>

      {/* Structured Tab Navigation */}
      <nav
        className="flex gap-1.5 overflow-x-auto rounded-xl border border-sky-100 bg-white p-1.5 shadow-sm shadow-sky-100/50"
        role="tablist"
      >
        {TABS.map((t) => {
          const active = tab === t.id;
          return (
            <button
              key={t.id}
              role="tab"
              aria-selected={active}
              onClick={() => go(t.id)}
              className={`flex items-center gap-2 whitespace-nowrap rounded-lg px-3.5 py-2 text-xs font-semibold transition ${
                active
                  ? "bg-sky-600 text-white shadow-sm shadow-sky-600/30"
                  : "text-slate-600 hover:bg-sky-50 hover:text-sky-900"
              }`}
            >
              <span
                className={`grid h-4 w-4 place-items-center rounded-full text-[10px] font-bold ${
                  active ? "bg-white/20 text-white" : "bg-sky-100 text-sky-800"
                }`}
              >
                {t.step}
              </span>
              <span>{t.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Active Tab Component */}
      <div className="pt-1">
        {tab === "overview" && <Overview {...ctx} />}
        {tab === "matrix" && <MatrixView {...ctx} />}
        {tab === "dharma" && <DharmaView {...ctx} />}
        {tab === "explanation" && <ExplanationView {...ctx} />}
        {tab === "compare" && <CompareView {...ctx} />}
        {tab === "sensitivity" && <SensitivityView {...ctx} />}
        {tab === "decision" && <DecisionView {...ctx} />}
      </div>

      {/* Sequential Next / Previous Tab Buttons */}
      <div className="flex items-center justify-between border-t border-sky-100 pt-4">
        <button
          onClick={() => currentIndex > 0 && go(TABS[currentIndex - 1].id)}
          disabled={currentIndex === 0}
          className="btn-secondary text-xs disabled:opacity-30"
        >
          ← Previous: {currentIndex > 0 ? TABS[currentIndex - 1].label : "Start"}
        </button>

        <span className="text-xs text-slate-400 font-medium">
          Step {currentIndex + 1} of {TABS.length}
        </span>

        <button
          onClick={() => currentIndex < TABS.length - 1 && go(TABS[currentIndex + 1].id)}
          disabled={currentIndex === TABS.length - 1}
          className="btn-secondary text-xs disabled:opacity-30"
        >
          Next: {currentIndex < TABS.length - 1 ? TABS[currentIndex + 1].label : "Complete"} →
        </button>
      </div>
    </div>
  );
}
