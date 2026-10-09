import type { Ctx } from "./ctx";

function Block({ q, items }: { q: string; items: string[] }) {
  return (
    <section className="card">
      <h2 className="card-title">{q}</h2>
      {items.length ? <ul className="list-disc space-y-1.5 pl-5 text-sm">{items.map((x) => <li key={x}>{x}</li>)}</ul> : <p className="text-sm muted">Nothing notable.</p>}
    </section>
  );
}

export function ExplanationView({ r }: Ctx) {
  const e = r.explanation;
  return (
    <div className="space-y-4">
      <section className="card">
        <h2 className="card-title">Why this evaluation?</h2>
        <p className="text-sm leading-relaxed">{e.why}</p>
      </section>
      <div className="grid gap-4 md:grid-cols-2">
        <Block q="Which principles drive it?" items={e.principles} />
        <Block q="Who is affected most?" items={e.key_stakeholders} />
        <Block q="What could change the result?" items={e.what_could_change} />
        <Block q="Where do frameworks disagree?" items={e.disagreements} />
      </div>
      <Block q="What was assumed?" items={e.assumptions} />
      <section className="card">
        <h2 className="card-title">Reasoning trace</h2>
        <ol className="space-y-2.5">
          {e.trace.map((t) => (
            <li key={t.step} className="grid grid-cols-[28px_110px_1fr] items-center gap-2 text-sm">
              <span className="grid h-6 w-6 place-items-center rounded-full bg-sky-100 text-xs font-bold text-sky-800 border border-sky-200">{t.step}</span>
              <span className="text-xs uppercase tracking-wider font-semibold text-sky-900">{t.stage}</span>
              <span className="text-slate-700">{t.summary}</span>
            </li>
          ))}
        </ol>
        <p className="mt-4 border-t border-sky-100 pt-3 text-xs text-slate-500">{e.note}</p>
      </section>
    </div>
  );
}
