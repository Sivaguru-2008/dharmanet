import type { KBEntry } from "@/types/api";

export function KBCard({ e, relevance }: { e: KBEntry; relevance?: number }) {
  return (
    <article className="card space-y-2 text-sm border border-sky-100 bg-white shadow-sm shadow-sky-100/50">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-bold text-sky-950">{e.concept}</h3>
          <div className="text-xs text-slate-400">
            {e.citation}
            {e.sanskrit_term && <> · <span className="italic text-sky-700">{e.sanskrit_term}</span></>}
          </div>
        </div>
        {relevance !== undefined && (
          <span className="chip bg-sky-50 text-sky-800 border border-sky-200 font-semibold">
            relevance {relevance.toFixed(2)}
          </span>
        )}
      </div>
      <p className="border-l-2 border-sky-400 pl-3 italic text-slate-700 bg-sky-50/30 py-1 rounded-r">
        {e.paraphrase} <span className="not-italic text-xs text-slate-400">(paraphrase)</span>
      </p>
      <p className="text-xs text-slate-600">
        <strong className="text-sky-950">DharmaNet interpretation: </strong>{e.interpretation}
      </p>
      {e.alternative_interpretations.length > 0 && (
        <div className="text-xs text-slate-500">
          <strong className="text-slate-700">Other readings: </strong>{e.alternative_interpretations.join(" ")}
        </div>
      )}
      <div className="text-xs text-slate-500">
        <strong className="text-slate-700">Limitations: </strong>{e.limitations.join(" ")}
      </div>
      <div className="flex flex-wrap gap-1.5 pt-1">
        {e.applicability.map((t) => (
          <span key={t} className="chip bg-sky-50 text-sky-700 border border-sky-100 font-medium">
            {t.replace(/_/g, " ")}
          </span>
        ))}
        <span className="chip bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold">
          {e.verification_status.replace(/_/g, " ")}
        </span>
      </div>
    </article>
  );
}
