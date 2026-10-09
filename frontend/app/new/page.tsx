"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { api } from "@/lib/api";

const EXAMPLES = [
  {
    id: "insulin-pump",
    title: "Insulin Pump Firmware Defect",
    role: "senior firmware engineer",
    domain: "healthcare",
    timePressure: "high",
    text:
      "I am a senior firmware engineer at a small medical device company. I found a bug that may cause our insulin pumps to deliver an incorrect dose in rare cases; we are not sure how often it happens, and no patient injury has been confirmed yet. Management, including the CEO who mentored me, wants to fix it silently in a software update in six months. A public recall could bankrupt the company and cost about 400 employees their jobs. I signed an NDA, and if I report this to the regulator I might lose my job and my career in the industry.",
  },
  {
    id: "ai-bias",
    title: "Biased AI Hiring Model",
    role: "machine learning engineer",
    domain: "ai_ethics",
    timePressure: "high",
    text:
      "Our team built an AI hiring model that performs well overall, but our validation tests suggest it systematically rates applicants from underrepresented minority backgrounds lower. The commercial product launch is scheduled for tomorrow morning. Leadership says fixing the bias will delay the product release by three months and could jeopardize our next funding round.",
  },
  {
    id: "exam-cheating",
    title: "Friend Cheating on Curved Exam",
    role: "student",
    domain: "education",
    timePressure: "medium",
    text:
      "I saw my close friend and roommate cheating during the final examination. The entire exam is graded on a strict competitive bell curve, so their inflated score directly reduces the final course grades of other honest students. However, my friend has been struggling with severe family financial emergencies and could lose their vital academic scholarship if reported.",
  },
  {
    id: "elderly-driver",
    title: "Elderly Parent Driving Safety",
    role: "adult child",
    domain: "family_social",
    timePressure: "medium",
    text:
      "My elderly father is no longer safe to drive due to declining cognitive reflexes, but he refuses to give up his car because driving represents his independence. My siblings are pressuring me to secretly disable his vehicle engine to stop him from driving without confrontation.",
  },
];

const DOMAINS = [
  "",
  "healthcare",
  "workplace",
  "business",
  "education",
  "ai_ethics",
  "privacy",
  "environment",
  "public_policy",
  "family_social",
  "professional",
  "technology_governance",
];

function NewDilemmaForm() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [text, setText] = useState("");
  const [role, setRole] = useState("");
  const [domain, setDomain] = useState("");
  const [culture, setCulture] = useState("");
  const [timePressure, setTimePressure] = useState("");
  const [additional, setAdditional] = useState("");
  const [dharma, setDharma] = useState(true);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    const exId = searchParams.get("example");
    if (exId) {
      const found = EXAMPLES.find((e) => e.id === exId);
      if (found) {
        setText(found.text);
        setRole(found.role);
        setDomain(found.domain);
        setTimePressure(found.timePressure);
      }
    }
  }, [searchParams]);

  async function submit() {
    if (text.trim().length < 20) return;
    setBusy(true);
    setErr("");
    try {
      const r = await api.create(
        text,
        { role, domain, cultural_context: culture, time_pressure: timePressure, additional },
        dharma
      );
      router.push(`/analysis/${r.id}`);
    } catch (e) {
      setErr((e as Error).message);
      setBusy(false);
    }
  }

  const tooShort = text.trim().length < 20;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
      <div className="card space-y-5 p-6 border border-sky-100 shadow-sm shadow-sky-100/50">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-sky-700">
            Dilemma Input
          </span>
          <h1 className="mt-1 text-2xl font-extrabold text-sky-950">Describe Your Moral Dilemma</h1>
          <p className="mt-1 text-xs text-slate-500">
            Specify the core conflict, who is impacted, and what duties or consequences pull in opposing directions.
          </p>
        </div>

        <div>
          <label className="label font-semibold">
            Dilemma statement <span className="text-rose-500">*</span>
          </label>
          <textarea
            className="input min-h-[220px] text-sm leading-relaxed"
            placeholder="e.g. I discovered that my company is hiding a safety defect in a medical product. Reporting it will protect patients but cause 400 coworkers to lose their jobs..."
            value={text}
            maxLength={8000}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="mt-1 flex justify-between text-xs text-slate-400">
            <span>{tooShort ? `Minimum 20 characters required (${text.trim().length}/20)` : `${text.length} / 8000 characters`}</span>
            <span>Avoid sharing personally identifying names</span>
          </div>
          {tooShort && (
            <div className="mt-2 flex flex-wrap items-center justify-between gap-2 rounded-lg border border-sky-200 bg-sky-50/70 p-3 text-xs text-sky-900">
              <span>💡 <strong>Quick Demo:</strong> Don't want to type? Click any preset dilemma on the right to test immediately.</span>
              <button
                type="button"
                onClick={() => {
                  setText(EXAMPLES[0].text);
                  setRole(EXAMPLES[0].role);
                  setDomain(EXAMPLES[0].domain);
                  setTimePressure(EXAMPLES[0].timePressure);
                }}
                className="chip bg-sky-600 text-white font-semibold hover:bg-sky-700 cursor-pointer shadow-sm"
              >
                Auto-Fill Medical Case →
              </button>
            </div>
          )}
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label">Your role in this scenario</label>
            <input
              className="input"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. senior engineer, doctor, student, parent"
            />
            <span className="text-[11px] text-slate-400">Informs professional duty and relational obligations.</span>
          </div>

          <div>
            <label className="label">Domain (auto-detected if empty)</label>
            <select className="input" value={domain} onChange={(e) => setDomain(e.target.value)}>
              {DOMAINS.map((d) => (
                <option key={d} value={d}>
                  {d ? d.replace(/_/g, " ") : "Auto-detect domain"}
                </option>
              ))}
            </select>
            <span className="text-[11px] text-slate-400">Provides domain-specific regulatory and ethical norms.</span>
          </div>

          <div>
            <label className="label">Cultural / institutional context (optional)</label>
            <input
              className="input"
              value={culture}
              onChange={(e) => setCulture(e.target.value)}
              placeholder="e.g. medical device startup, academic lab in India"
            />
            <span className="text-[11px] text-slate-400">Contextual nuances for ethical interpretation.</span>
          </div>

          <div>
            <label className="label">Time urgency</label>
            <select className="input" value={timePressure} onChange={(e) => setTimePressure(e.target.value)}>
              <option value="">Unspecified</option>
              <option value="low">Low (months to deliberate)</option>
              <option value="medium">Medium (days / weeks)</option>
              <option value="high">High (immediate crisis / hours)</option>
            </select>
            <span className="text-[11px] text-slate-400">Affects feasibility of information gathering or delays.</span>
          </div>
        </div>

        <div>
          <label className="label">Additional context or constraints (optional)</label>
          <textarea
            className="input min-h-[60px] text-xs"
            placeholder="e.g. Legal NDA signed, financial dependencies, previous precedents..."
            value={additional}
            maxLength={2000}
            onChange={(e) => setAdditional(e.target.value)}
          />
        </div>

        <div className="rounded-lg border border-sky-200 bg-sky-50/50 p-3.5">
          <label className="flex items-center gap-2.5 text-xs font-semibold text-sky-950 cursor-pointer">
            <input
              type="checkbox"
              className="accent-sky-600 h-4 w-4 rounded"
              checked={dharma}
              onChange={(e) => setDharma(e.target.checked)}
            />
            <span>Include culturally contextualized Dharma-inspired perspective (Bhagavad Gita & Mahābhārata)</span>
          </label>
          <p className="mt-1 pl-6 text-[11px] text-slate-600">
            Grounds actions in concepts like Kartavya (duty), Loka-samgraha (public welfare), and Nishkama Karma with citation validation.
          </p>
        </div>

        {err && (
          <p className="rounded-lg bg-rose-50 border border-rose-200 p-3 text-xs text-rose-800">
            {err}
          </p>
        )}

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button
            className="btn-primary px-6 shadow-sm"
            disabled={busy || tooShort}
            onClick={submit}
          >
            {busy
              ? "Deconstructing & Analysing Dilemma…"
              : tooShort
              ? `Enter at least ${20 - text.trim().length} more characters to Analyse`
              : "Run Full Multi-Framework Analysis →"}
          </button>
          <span className="text-xs text-slate-500 font-medium">
            Offline deterministic engine: 0.1s response, no waiting.
          </span>
        </div>
      </div>

      {/* Right Column: Examples and Notes */}
      <aside className="space-y-4">
        <div className="card space-y-3 p-4 border border-sky-100 shadow-sm shadow-sky-100/50">
          <div className="flex items-center justify-between">
            <h2 className="card-title mb-0">Preset Cases</h2>
            <span className="text-[11px] font-semibold text-sky-600">1-Click Load</span>
          </div>
          <p className="text-xs text-slate-500">
            Select a verified benchmark dilemma to populate all fields immediately:
          </p>
          <div className="space-y-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex.id}
                className="w-full rounded-lg border border-sky-100 bg-white p-2.5 text-left text-xs transition hover:border-sky-400 hover:bg-sky-50 shadow-sm"
                onClick={() => {
                  setText(ex.text);
                  setRole(ex.role);
                  setDomain(ex.domain);
                  setTimePressure(ex.timePressure);
                }}
              >
                <div className="font-bold text-sky-950">{ex.title}</div>
                <div className="mt-1 line-clamp-2 text-[11px] text-slate-500">{ex.text}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="card space-y-2 text-xs text-slate-600 p-4 border border-sky-100">
          <h3 className="font-bold text-sky-950">Reproducibility Guarantee</h3>
          <p>
            Every analysis run is saved with explicit versioning, input text hashes, and deterministic seeds so results can be verified in academic research logs.
          </p>
        </div>
      </aside>
    </div>
  );
}

export default function NewDilemma() {
  return (
    <Suspense fallback={<div className="card p-8 text-center text-sm muted">Loading form…</div>}>
      <NewDilemmaForm />
    </Suspense>
  );
}
