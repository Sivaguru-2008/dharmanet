"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { KBEntry } from "@/types/api";
import { KBCard } from "@/components/analysis/KBCard";

export default function Knowledge() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState<KBEntry[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    const t = setTimeout(() => api.knowledge(q).then(setItems).catch((e) => setErr(e.message)), 250);
    return () => clearTimeout(t);
  }, [q]);

  return (
    <div className="space-y-5">
      <div className="border-b border-sky-100 pb-3">
        <h1 className="text-2xl font-extrabold text-sky-950">Dharma Knowledge Base</h1>
        <p className="max-w-3xl text-xs text-slate-500 mt-1 leading-relaxed">
          Structured records of selected Bhagavad Gita verses and Mahābhārata episodes. Texts are short paraphrases written for this
          project, not translations. Mahābhārata episodes are cited at parva (book) level because verse numbering differs between
          editions. All entries await scholarly review.
        </p>
      </div>
      <div>
        <input className="input max-w-md shadow-sm" placeholder="Search (e.g. silence, loyalty, truth, duty)…" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      {err && <p className="text-sm text-rose-600 bg-rose-50 border border-rose-200 p-3 rounded-lg">{err}</p>}
      <div className="grid gap-4 md:grid-cols-2">
        {items.map((e) => <KBCard key={e.id} e={e} />)}
      </div>
    </div>
  );
}
