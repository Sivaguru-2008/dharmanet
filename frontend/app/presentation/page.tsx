"use client";
import Link from "next/link";
import { useState, useEffect } from "react";

interface Slide {
  id: string;
  badge: string;
  title: string;
  subtitle: string;
  content: React.ReactNode;
}

export default function PresentationPage() {
  const [current, setCurrent] = useState(0);

  const slides: Slide[] = [
    {
      id: "title",
      badge: "Project Overview · System Defense",
      title: "DharmaNet: Explainable Multi-Framework Ethical AI",
      subtitle: "A Culturally Contextualized, Source-Grounded Decision Support System",
      content: (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="card border-l-4 border-l-sky-500 bg-sky-50/50 border-sky-100">
              <h4 className="font-bold text-sky-900">Core Thesis</h4>
              <p className="mt-1 text-xs text-slate-700 leading-relaxed">
                Ethical decisions should not be delegated to black-box conversational chatbots. Systems must provide structured decomposition, multi-framework trade-offs, and source-grounded reasoning while preserving <strong>human decision authority</strong>.
              </p>
            </div>
            <div className="card border-l-4 border-l-blue-600 bg-blue-50/50 border-blue-100">
              <h4 className="font-bold text-blue-900">7 Evaluative Lenses</h4>
              <p className="mt-1 text-xs text-slate-700 leading-relaxed">
                Evaluates every candidate action across 6 classical Western ethical frameworks (Consequences, Duty, Fairness, Virtue, Care, Stakeholders) plus a dedicated <strong>source-grounded Dharma perspective</strong> (Bhagavad Gita & Mahābhārata).
              </p>
            </div>
            <div className="card border-l-4 border-l-teal-500 bg-teal-50/50 border-teal-100">
              <h4 className="font-bold text-teal-900">Deterministic Math</h4>
              <p className="mt-1 text-xs text-slate-700 leading-relaxed">
                Aggregation, rankings, and Monte Carlo sensitivity analyses are executed by <strong>deterministic code</strong>, not LLM opinion. Every philosophical claim is validated against cited textual sources.
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-sky-200 bg-white p-4 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-semibold text-slate-600">
              <span>FOUNDATIONAL PRINCIPLE: Bhagavad Gita 18.63</span>
              <span className="chip bg-sky-100 text-sky-800 border border-sky-200">
                vimṛśyaitad aśeṣeṇa yathecchasi tathā kuru
              </span>
            </div>
            <p className="mt-2 text-xs italic text-slate-700">
              "Reflect on this fully, in its entirety, and then act as you choose." — DharmaNet provides rigorous structured analysis; the human retains 100% moral responsibility.
            </p>
          </div>
        </div>
      ),
    },
    {
      id: "problem",
      badge: "The Problem Space",
      title: "Why Standard LLMs Fail at Moral Advice",
      subtitle: "The dangers of prompting a single black-box model with 'What should I do?'",
      content: (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="card border-rose-200 bg-rose-50/40">
              <div className="flex items-center gap-2 text-rose-800 font-bold text-sm">
                <span className="grid h-5 w-5 place-items-center rounded-full bg-rose-200 text-xs text-rose-800">✕</span>
                Current Paradigm: Black-Box Chatbots
              </div>
              <ul className="mt-3 space-y-2 text-xs text-slate-700">
                <li className="flex items-start gap-2">
                  <span className="font-bold text-rose-500">•</span>
                  <span><strong>Moral Monism & Sycophancy:</strong> Produces a single fluent answer matching user bias or RLHF safety defaults without showing alternative philosophies.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-rose-500">•</span>
                  <span><strong>Hidden Trade-Offs:</strong> Obscures why one duty was prioritized over another (e.g. saving company jobs vs. protecting public health).</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-rose-500">•</span>
                  <span><strong>Prompt Wording Fragility:</strong> Small phrasing tweaks invert the recommendation with zero stability metric.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-rose-500">•</span>
                  <span><strong>Hallucinated Authority:</strong> Generates authoritative-sounding moral advice with no traceable citations.</span>
                </li>
              </ul>
            </div>

            <div className="card border-sky-200 bg-sky-50/40">
              <div className="flex items-center gap-2 text-sky-800 font-bold text-sm">
                <span className="grid h-5 w-5 place-items-center rounded-full bg-sky-200 text-xs text-sky-800">✓</span>
                DharmaNet's Structured Approach
              </div>
              <ul className="mt-3 space-y-2 text-xs text-slate-700">
                <li className="flex items-start gap-2">
                  <span className="font-bold text-sky-600">•</span>
                  <span><strong>Pluralistic Multi-Framework Evaluation:</strong> Scores candidate actions across 7 distinct ethical paradigms simultaneously.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-sky-600">•</span>
                  <span><strong>Explicit Decomposition:</strong> Separates stakeholders, rights, conflicts, constraints, and assumptions for user inspection.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-sky-600">•</span>
                  <span><strong>Monte Carlo Sensitivity Analysis:</strong> Mathematically flags whether recommendations are <em>Stable</em> or <em>Highly Sensitive</em> to weight changes.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-sky-600">•</span>
                  <span><strong>Strict Citation Validation:</strong> Dropping any religious or philosophical claim that lacks a verified knowledge-base citation.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "architecture",
      badge: "System Architecture",
      title: "The 5-Stage Processing Pipeline",
      subtitle: "From free-text dilemma to multi-framework scoring and sensitivity analysis",
      content: (
        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-5">
            {[
              {
                step: "01",
                name: "Structuring",
                desc: "Extracts stakeholders, salience, rights, ethical tensions, context cues, and constraints into editable structured schema.",
                color: "border-sky-200 bg-sky-50/70",
              },
              {
                step: "02",
                name: "Option Space",
                desc: "Generates ≥7 diverse actions: direct response, internal escalation, external reporting, compromise, inquiry, delay, status quo.",
                color: "border-blue-200 bg-blue-50/60",
              },
              {
                step: "03",
                name: "Multi-Framework Scoring",
                desc: "6 Western ethical frameworks score all options with stated principles, ± uncertainties, assumptions, and counter-arguments.",
                color: "border-indigo-200 bg-indigo-50/60",
              },
              {
                step: "04",
                name: "Dharma & RAG Grounding",
                desc: "Retrieves cited concepts from 28-entry curated KB. Citation validator drops any claim without verified textual source.",
                color: "border-sky-200 bg-sky-50/70",
              },
              {
                step: "05",
                name: "Deterministic Aggregation",
                desc: "Normalizes user weights, calculates ranking, computes exact weight-flip thresholds and Monte Carlo stability labels.",
                color: "border-teal-200 bg-teal-50/60",
              },
            ].map((s) => (
              <div key={s.step} className={`rounded-lg border p-3 ${s.color}`}>
                <div className="text-xs font-mono font-bold text-sky-800">{s.step}</div>
                <h5 className="font-bold text-sm mt-1 text-sky-950">{s.name}</h5>
                <p className="mt-1 text-xs text-slate-600">{s.desc}</p>
              </div>
            ))}
          </div>

          <div className="card text-xs space-y-2 bg-white border border-sky-100">
            <div className="font-bold text-sky-950">Technical Implementation Highlights:</div>
            <div className="grid gap-2 md:grid-cols-3 text-slate-600">
              <div>• <strong>Backend:</strong> FastAPI, Pydantic v2, SQLAlchemy ORM, SQLite/PostgreSQL storage.</div>
              <div>• <strong>Deterministic Engine:</strong> Instant local heuristic path (~100ms response time).</div>
              <div>• <strong>Frontend:</strong> Next.js 15 App Router, TypeScript, Tailwind CSS, SVG Radar & Scorebars.</div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "frameworks",
      badge: "Philosophical Rigor",
      title: "The 7 Evaluative Ethical Frameworks",
      subtitle: "Parallel independent evaluation preventing ethical bias",
      content: (
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {[
            {
              name: "Consequentialism / Utilitarianism",
              author: "Bentham, Mill",
              question: "Which action produces the greatest net well-being and minimizes total aggregate harm?",
              focus: "Long-term vs. short-term stakeholder utility balance.",
            },
            {
              name: "Deontological Ethics",
              author: "Immanuel Kant",
              question: "Does the action conform to universalizable moral duties, contracts, and rights?",
              focus: "Categorical imperative, truthfulness, non-instrumentalization of humans.",
            },
            {
              name: "Justice & Fairness",
              author: "John Rawls",
              question: "Is the distribution of benefits and burdens equitable under the veil of ignorance?",
              focus: "Protection of the most vulnerable and marginalized parties.",
            },
            {
              name: "Virtue Ethics",
              author: "Aristotle",
              question: "What kind of moral character and practical wisdom (phronesis) does this action embody?",
              focus: "Integrity, courage, temperance, moral excellence.",
            },
            {
              name: "Ethics of Care",
              author: "Carol Gilligan",
              question: "How does the action sustain relationships, relational trust, and contextual empathy?",
              focus: "Interdependence, responsiveness, care for affected individuals.",
            },
            {
              name: "Stakeholder Impact Matrix",
              author: "R. Edward Freeman",
              question: "What is the net gain or injury experienced by each affected party?",
              focus: "Granular breakdown of harm/benefit across all identified stakeholders.",
            },
            {
              name: "Classical Dharma Ethics",
              author: "Bhagavad Gita & Mahābhārata",
              question: "How does this action align with role-duty (Kartavya), universal welfare, and detached action?",
              focus: "Loka-samgraha (public good), Nishkama Karma (unselfish action), Ahimsa (non-harm).",
            },
          ].map((f, i) => (
            <div key={f.name} className={`card p-4 text-xs border border-sky-100 ${i === 6 ? "md:col-span-2 lg:col-span-3 border-sky-200 bg-sky-50/40" : ""}`}>
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-sm text-sky-950">{f.name}</h4>
                <span className="chip bg-sky-50 text-sky-700 border border-sky-200 font-medium">{f.author}</span>
              </div>
              <p className="mt-2 text-slate-700 font-medium italic">"{f.question}"</p>
              <p className="mt-1 text-slate-500">Core focus: {f.focus}</p>
            </div>
          ))}
        </div>
      ),
    },
    {
      id: "dharma-rag",
      badge: "Cultural Grounding & Verification",
      title: "The Dharma Knowledge Base & Citation Validator",
      subtitle: "Preventing AI hallucination through verified textual retrieval",
      content: (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="card space-y-3 border border-sky-100">
              <h4 className="font-bold text-sm text-sky-950">Grounded Knowledge Base (28 Curated Records)</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Rather than letting an LLM invent religious opinions, DharmaNet maintains a structured corpus of Bhagavad Gita verses and Mahābhārata parvas. Each record stores:
              </p>
              <div className="space-y-1.5 text-xs">
                <div className="p-2 rounded bg-sky-50 border border-sky-100 font-mono text-sky-900">
                  • <strong>Concept:</strong> Kartavya, Loka-samgraha, Nishkama Karma, Ahimsa, Satya, Dharma Sankata
                </div>
                <div className="p-2 rounded bg-sky-50 border border-sky-100 font-mono text-sky-900">
                  • <strong>Citation:</strong> Specific chapter & verse (e.g. BG 3.20, BG 2.47, MBh Udyoga 37)
                </div>
                <div className="p-2 rounded bg-sky-50 border border-sky-100 font-mono text-sky-900">
                  • <strong>Verification Status:</strong> peer_reviewed / canonical_consensus
                </div>
              </div>
            </div>

            <div className="card border-sky-200 bg-sky-50/40 space-y-3">
              <h4 className="font-bold text-sm text-sky-950">The Automated Citation Validator</h4>
              <p className="text-xs text-slate-700 leading-relaxed">
                Whenever the system generates a Dharma-inspired reading, a deterministic validator verifies each claim:
              </p>
              <div className="space-y-2 text-xs text-slate-700">
                <div className="flex items-start gap-2">
                  <span className="font-bold text-sky-600">1.</span>
                  <span>Checks that the referenced concept exists in the loaded Knowledge Base.</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="font-bold text-sky-600">2.</span>
                  <span>Verifies chapter/verse citations against canonical database indices.</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="font-bold text-sky-600">3.</span>
                  <span><strong>Automatic Pruning:</strong> If a generated claim cannot be grounded in an entry, it is discarded, and recorded in <code>dropped_claims</code>.</span>
                </div>
              </div>
              <div className="text-[11px] text-slate-500 italic">
                Result: Zero hallucinated scriptures or fabricated religious doctrines.
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "sensitivity",
      badge: "Mathematical Rigor",
      title: "Deterministic Aggregation & Sensitivity Analysis",
      subtitle: "Proving whether a recommendation is robust or fragile",
      content: (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="card p-4 border border-sky-100">
              <h4 className="font-bold text-sm text-sky-950">Weighted Multi-Criteria Scoring</h4>
              <p className="mt-1 text-xs text-slate-500">
                Scores across all 7 dimensions are normalized:
              </p>
              <div className="my-2 p-2 rounded bg-sky-50 border border-sky-100 font-mono text-xs text-center text-sky-900">
                {"Score(a) = Σ (w_d · s_{a,d}) / Σ w_d"}
              </div>
              <p className="text-xs text-slate-500">
                Calculated simultaneously with user-customized weights AND equal weights baseline to reveal personal priority bias.
              </p>
            </div>

            <div className="card p-4 border border-sky-100">
              <h4 className="font-bold text-sm text-sky-950">Exact Weight-Flip Boundaries</h4>
              <p className="mt-1 text-xs text-slate-500">
                Solves exact algebraic thresholds:
              </p>
              <div className="my-2 p-2 rounded bg-sky-50 border border-sky-100 text-xs text-sky-900">
                "Duty weight would need to increase from 0.20 to 0.47 for Action B to surpass Action A."
              </div>
              <p className="text-xs text-slate-500">
                Tells the decision-maker precisely what philosophical shift would reverse their choice.
              </p>
            </div>

            <div className="card p-4 border border-sky-100">
              <h4 className="font-bold text-sm text-sky-950">Monte Carlo Stability Testing</h4>
              <p className="mt-1 text-xs text-slate-500">
                Runs 1,000 seeded stochastic perturbations over scores and weights:
              </p>
              <div className="my-2 space-y-1 text-xs font-semibold">
                <span className="chip bg-emerald-50 text-emerald-800 border border-emerald-200">Stable (&gt;75% win share)</span>
                <span className="chip bg-sky-50 text-sky-800 border border-sky-200">Moderately Sensitive (50-75%)</span>
                <span className="chip bg-amber-50 text-amber-800 border border-amber-200">Highly Sensitive (&lt;50%)</span>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-sky-200 bg-sky-50/50 p-3 text-xs text-sky-900">
            <strong>Key Benefit:</strong> If top options are within overlapping ± uncertainty whiskers, DharmaNet explicitly reports <em>"No clear preference — leading options are within uncertainty"</em>, avoiding false precision!
          </div>
        </div>
      ),
    },
    {
      id: "demo-case",
      badge: "Real-World Benchmark",
      title: "Case Study: Medical Device Firmware Bug",
      subtitle: "A real high-stakes engineering dilemma analyzed end-to-end",
      content: (
        <div className="space-y-4">
          <div className="card text-xs space-y-2 border border-sky-100">
            <div className="font-bold text-sky-950 text-sm">The Dilemma Scenario:</div>
            <p className="italic text-slate-700">
              "A senior firmware engineer finds a bug in an insulin pump that may cause incorrect dosages in rare cases. Management wants to patch it silently in six months. A public recall could bankrupt the company (costing 400 jobs). Reporting to the regulator violates an NDA and could ruin the engineer's career."
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 text-xs">
            <div className="card border-sky-200 bg-sky-50/40">
              <div className="font-bold text-sky-950">Action A: Internal Escalation with Deadline</div>
              <div className="mt-1 text-slate-700">
                Score: <strong>6.86 ± 0.72</strong>. Maximizes Duty (gives company chance to rectify) and Care.
              </div>
            </div>
            <div className="card border-teal-200 bg-teal-50/40">
              <div className="font-bold text-teal-950">Action B: Immediate Whistleblowing to Regulator</div>
              <div className="mt-1 text-slate-700">
                Score: <strong>6.66 ± 0.74</strong>. Dominates in Virtue & Public Safety (Loka-samgraha), but causes immediate severe job loss.
              </div>
            </div>
            <div className="card border-rose-200 bg-rose-50/40">
              <div className="font-bold text-rose-950">Action C: Silent Compliance with Management</div>
              <div className="mt-1 text-slate-700">
                Score: <strong>3.12 ± 0.65</strong>. Fails on Deontology, Virtue, and Ahimsa due to unmitigated patient risk.
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between rounded-lg bg-sky-50 border border-sky-200 p-3 text-xs">
            <span className="text-sky-950">
              Actions A and B are within mutual uncertainty (margin 0.20 &lt; uncertainty 0.72). DharmaNet highlights this as a <strong>genuine ethical tension</strong> rather than fabricating a false clear winner.
            </span>
            <Link href="/new" className="btn-primary text-xs shrink-0 ml-3">
              Test This Case Live →
            </Link>
          </div>
        </div>
      ),
    },
    {
      id: "summary",
      badge: "Conclusion & Defense",
      title: "Summary of Key Scientific Contributions",
      subtitle: "Why DharmaNet advances the state of AI ethics and decision support",
      content: (
        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2 text-xs">
            <div className="card p-3 border border-sky-100">
              <h4 className="font-bold text-sm text-sky-950">1. Pluralistic Ethical Modeling</h4>
              <p className="mt-1 text-slate-600">
                Replaces black-box moral monism with 7 distinct philosophical frameworks evaluating decisions in parallel.
              </p>
            </div>
            <div className="card p-3 border border-sky-100">
              <h4 className="font-bold text-sm text-sky-950">2. Culturally Grounded & Hallucination-Free</h4>
              <p className="mt-1 text-slate-600">
                First system to integrate classical Indian ethics (Bhagavad Gita & Mahābhārata) with a strict textual citation validator.
              </p>
            </div>
            <div className="card p-3 border border-sky-100">
              <h4 className="font-bold text-sm text-sky-950">3. Mathematical Sensitivity Analysis</h4>
              <p className="mt-1 text-slate-600">
                Deterministic Monte Carlo stability testing and exact weight-flip boundaries expose recommendation fragility.
              </p>
            </div>
            <div className="card p-3 border border-sky-100">
              <h4 className="font-bold text-sm text-sky-950">4. Complete Human Decision Agency</h4>
              <p className="mt-1 text-slate-600">
                Preserves user authority: the human can Accept, Choose an Alternative, Modify, or Reject. The AI never acts autonomously.
              </p>
            </div>
          </div>

          <div className="card text-center p-6 bg-white border border-sky-200 shadow-sm shadow-sky-100">
            <h3 className="text-base font-bold text-sky-950">
              Ready to Explore DharmaNet Live?
            </h3>
            <p className="mt-1 text-xs text-slate-500 max-w-lg mx-auto">
              Analyze a custom dilemma or load one of the pre-computed benchmark case studies.
            </p>
            <div className="mt-4 flex justify-center gap-3">
              <Link href="/new" className="btn-primary text-sm shadow-sm">
                Launch Live Dilemma Analysis
              </Link>
              <Link href="/history" className="btn-secondary text-sm">
                View Analysis History
              </Link>
              <Link href="/knowledge" className="btn-secondary text-sm">
                Explore Knowledge Base
              </Link>
            </div>
          </div>
        </div>
      ),
    },
  ];

  const slide = slides[current];

  // Arrow key navigation
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") {
        setCurrent((c) => Math.min(slides.length - 1, c + 1));
      } else if (e.key === "ArrowLeft") {
        setCurrent((c) => Math.max(0, c - 1));
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [slides.length]);

  return (
    <div className="mx-auto max-w-5xl space-y-6 py-2">
      {/* Top Slide Navigation Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-sky-100 pb-4">
        <div className="flex items-center gap-2">
          <span className="chip bg-sky-100 text-sky-800 font-bold border border-sky-200">
            Presentation Mode
          </span>
          <span className="text-xs text-slate-500 font-medium">
            Slide {current + 1} of {slides.length}
          </span>
        </div>

        {/* Slide Dots / Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {slides.map((s, idx) => (
            <button
              key={s.id}
              onClick={() => setCurrent(idx)}
              className={`h-2.5 rounded-full transition-all ${
                current === idx
                  ? "w-8 bg-sky-600 shadow-sm"
                  : "w-2.5 bg-sky-200 hover:bg-sky-300"
              }`}
              title={`Slide ${idx + 1}: ${s.title}`}
            />
          ))}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrent((c) => Math.max(0, c - 1))}
            disabled={current === 0}
            className="btn-secondary px-3 py-1.5 text-xs disabled:opacity-30"
          >
            ← Previous
          </button>
          <button
            onClick={() => setCurrent((c) => Math.min(slides.length - 1, c + 1))}
            disabled={current === slides.length - 1}
            className="btn-primary px-3 py-1.5 text-xs disabled:opacity-30"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Main Slide Card */}
      <div className="card min-h-[460px] p-6 md:p-8 shadow-sm shadow-sky-100 border border-sky-100 space-y-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-sky-700">
            {slide.badge}
          </span>
          <h2 className="mt-1 text-2xl font-extrabold tracking-tight text-sky-950 md:text-3xl">
            {slide.title}
          </h2>
          <p className="mt-1 text-sm text-slate-500 font-medium">
            {slide.subtitle}
          </p>
        </div>

        <div className="pt-2">{slide.content}</div>
      </div>

      {/* Slide footer keyboard guide */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>Use Left / Right arrow keys or spacebar to navigate slides</span>
        <Link href="/" className="hover:underline text-sky-700 font-semibold">
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}
