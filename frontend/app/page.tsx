import Link from "next/link";

const BENCHMARKS = [
  {
    id: "insulin-pump",
    title: "Medical Device Firmware Bug",
    domain: "Healthcare / Engineering",
    preview:
      "A senior engineer finds a bug in an insulin pump that may cause incorrect dosages in rare cases. Management wants to silently patch it in six months. Whistleblowing violates an NDA and threatens 400 jobs.",
    tensions: "Public Safety vs. Corporate Loyalty & Livelihoods",
    query:
      "I am a senior firmware engineer at a small medical device company. I found a bug that may cause our insulin pumps to deliver an incorrect dose in rare cases; we are not sure how often it happens, and no patient injury has been confirmed yet. Management, including the CEO who mentored me, wants to fix it silently in a software update in six months. A public recall could bankrupt the company and cost about 400 employees their jobs. I signed an NDA, and if I report this to the regulator I might lose my job and my career in the industry.",
    role: "senior firmware engineer",
  },
  {
    id: "ai-bias",
    title: "AI Hiring Algorithm Bias",
    domain: "AI Ethics / Tech Governance",
    preview:
      "A new automated hiring model achieves high performance but demonstrates systemic disparity against minority applicants. Product launch is tomorrow, and fixing the bias will delay the product by 3 months.",
    tensions: "Algorithmic Fairness vs. Business Deadlines",
    query:
      "Our team built an AI hiring model that performs well overall, but our validation tests suggest it systematically rates applicants from underrepresented minority backgrounds lower. The commercial product launch is scheduled for tomorrow morning. Leadership says fixing the bias will delay the product release by three months and could jeopardize our next funding round.",
    role: "machine learning engineer",
  },
  {
    id: "exam-cheating",
    title: "Academic Integrity & Friendship",
    domain: "Education / Social Ethics",
    preview:
      "A student witnesses a close friend cheating on a curved final exam. Reporting protects honest peers but will cause the friend to lose an essential financial-aid scholarship.",
    tensions: "Distributive Justice vs. Relational Loyalty",
    query:
      "I saw my close friend and roommate cheating during the final examination. The entire exam is graded on a strict competitive bell curve, so their inflated score directly reduces the final course grades of other honest students. However, my friend has been struggling with severe family financial emergencies and could lose their vital academic scholarship if reported.",
    role: "student",
  },
  {
    id: "elderly-driver",
    title: "Elderly Parent Autonomy vs Safety",
    domain: "Family / Public Safety",
    preview:
      "An aging parent is no longer safe to drive but refuses to give up the keys because it is their last remaining independence. Siblings suggest secretly disabling the vehicle.",
    tensions: "Individual Autonomy vs. Harm Prevention & Deception",
    query:
      "My elderly father is no longer safe to drive due to declining cognitive reflexes, but he refuses to give up his car because driving represents his independence. My siblings are pressuring me to secretly disable his vehicle engine to stop him from driving without confrontation.",
    role: "adult child",
  },
];

const FRAMEWORKS = [
  {
    name: "Consequentialism (Utilitarian)",
    origin: "Bentham & J.S. Mill",
    question: "What produces the greatest net well-being and minimal overall suffering?",
    metric: "Aggregate utility across all stakeholders.",
  },
  {
    name: "Deontological Ethics (Duty)",
    origin: "Immanuel Kant",
    question: "Does the action uphold universal moral duties, honesty, and rights?",
    metric: "Categorical imperative, truth-telling, non-exploitation.",
  },
  {
    name: "Fairness & Justice (Rawlsian)",
    origin: "John Rawls",
    question: "How are benefits and burdens distributed under the veil of ignorance?",
    metric: "Equity and special protection for the most vulnerable.",
  },
  {
    name: "Virtue Ethics (Character)",
    origin: "Aristotle",
    question: "What moral character, integrity, and practical wisdom does this demonstrate?",
    metric: "Courage, honesty, temperance, moral excellence.",
  },
  {
    name: "Ethics of Care (Relational)",
    origin: "Carol Gilligan",
    question: "How does the action preserve relationships and respond to vulnerability?",
    metric: "Trust, empathy, interdependence, and personal care.",
  },
  {
    name: "Stakeholder Impact Matrix",
    origin: "R. Edward Freeman",
    question: "What is the net injury or gain experienced by each affected party?",
    metric: "Granular stakeholder-by-stakeholder benefit/harm delta.",
  },
  {
    name: "Classical Dharma Perspective",
    origin: "Bhagavad Gita & Mahābhārata",
    question: "How does the action align with role-duty (Kartavya) and public good (Loka-samgraha)?",
    metric: "Source-grounded textual retrieval with citation validation.",
  },
];

const PIPELINE_STEPS = [
  {
    step: "1",
    title: "Deconstruct Dilemma",
    desc: "Transforms free text into editable stakeholders, rights, conflicts, constraints, and context cues.",
  },
  {
    step: "2",
    title: "Generate Options",
    desc: "Generates ≥7 candidate actions spanning direct action, escalation, compromise, information gathering, and delay.",
  },
  {
    step: "3",
    title: "Parallel Evaluation",
    desc: "6 Western ethical frameworks score every option with rationale, assumptions, ± uncertainty, and disagreement.",
  },
  {
    step: "4",
    title: "Dharma & RAG Layer",
    desc: "Applies classical Sanskrit concepts (Kartavya, Loka-samgraha, Ahimsa) with strict citation validation.",
  },
  {
    step: "5",
    title: "Deterministic Aggregation",
    desc: "Calculates weighted rankings, Monte Carlo stability tests, and exact weight-flip boundaries.",
  },
  {
    step: "6",
    title: "Human Decision Authority",
    desc: "The system explains its reasoning and stops. The human user retains 100% final moral decision authority.",
  },
];

export default function Home() {
  return (
    <div className="space-y-10 pb-12">
      {/* Hero Section */}
      <section className="card relative overflow-hidden border border-sky-100 bg-gradient-to-br from-white via-sky-50/40 to-white p-8 md:p-12 shadow-sm shadow-sky-100">
        <div className="max-w-3xl space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="chip bg-sky-100 font-semibold text-sky-800 border border-sky-200">
              Explainable Decision Support
            </span>
            <span className="chip bg-white text-slate-700 border border-slate-200">
              Deterministic Math · Source-Grounded
            </span>
          </div>

          <h1 className="text-3xl font-extrabold tracking-tight text-sky-950 md:text-5xl">
            An ethics analyst beside you — not a black box telling you what is right.
          </h1>

          <p className="text-base leading-relaxed text-slate-600 md:text-lg">
            DharmaNet deconstructs agonizing moral dilemmas, evaluates actions across seven independent ethical frameworks,
            and validates philosophical claims against cited classical texts.
            <strong className="block mt-2 font-semibold text-sky-900">
              Deterministic code handles scoring and sensitivity; final decision authority stays with the human.
            </strong>
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-3">
            <Link href="/new" className="btn-primary">
              Analyse a Dilemma
            </Link>
            <Link href="/presentation" className="btn-secondary font-medium">
              Presentation Walkthrough
            </Link>
            <Link href="/knowledge" className="btn-secondary">
              Browse Knowledge Base (28 Sources)
            </Link>
          </div>
        </div>
      </section>

      {/* The Core Problem vs. DharmaNet Solution */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-sky-950">
            Why DharmaNet? Standard LLMs vs. Structured Decision Support
          </h2>
          <p className="text-sm text-slate-500">
            Asking ChatGPT or Claude "What should I do?" introduces hidden biases and hallucinated moral authority.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="card border-rose-200 bg-rose-50/40 p-5">
            <div className="flex items-center gap-2 font-semibold text-rose-800">
              <span className="grid h-6 w-6 place-items-center rounded-full bg-rose-200 text-xs text-rose-800 font-bold">
                ✕
              </span>
              Standard Generative AI Chatbots
            </div>
            <ul className="mt-4 space-y-2.5 text-xs text-slate-700">
              <li className="flex items-start gap-2">
                <span className="font-bold text-rose-500">•</span>
                <span><strong>Single Fluent Verdict:</strong> Provides one confident recommendation while hiding dissenting ethical philosophies.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold text-rose-500">•</span>
                <span><strong>Opaque Black Box:</strong> Weights, assumptions, and principles remain completely invisible to the user.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold text-rose-500">•</span>
                <span><strong>Fragile Wording Sensitivity:</strong> Slight prompt phrasing changes flip the moral answer with no stability score.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold text-rose-500">•</span>
                <span><strong>Hallucinated Citations:</strong> Generates plausible-sounding but unverifiable ethical quotes.</span>
              </li>
            </ul>
          </div>

          <div className="card border-sky-200 bg-sky-50/50 p-5">
            <div className="flex items-center gap-2 font-semibold text-sky-800">
              <span className="grid h-6 w-6 place-items-center rounded-full bg-sky-200 text-xs text-sky-800 font-bold">
                ✓
              </span>
              The DharmaNet Explainable Pipeline
            </div>
            <ul className="mt-4 space-y-2.5 text-xs text-slate-700">
              <li className="flex items-start gap-2">
                <span className="font-bold text-sky-600">•</span>
                <span><strong>7 Independent Lenses:</strong> Evaluates trade-offs across Utilitarian, Kantian, Rawlsian, Virtue, Care, and Dharma frameworks.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold text-sky-600">•</span>
                <span><strong>Transparent Aggregation:</strong> Deterministic mathematics calculate weighted rankings; user adjusts priorities.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold text-sky-600">•</span>
                <span><strong>Monte Carlo Stability Testing:</strong> Rigorously flags whether the winning choice is <em>Stable</em> or <em>Fragile</em>.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold text-sky-600">•</span>
                <span><strong>Source-Grounded Citation Validator:</strong> Every Dharma claim cites verifiable Gita/Mahabharata verses; uncited claims are dropped.</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* One-Click Benchmark Dilemmas */}
      <section className="space-y-4">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-sky-950">
              Explore Live Benchmark Dilemmas
            </h2>
            <p className="text-sm text-slate-500">
              Click any realistic dilemma to test the full 7-framework evaluation pipeline instantly.
            </p>
          </div>
          <Link href="/history" className="text-xs font-semibold text-sky-700 hover:underline">
            View all past runs in History →
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {BENCHMARKS.map((b) => (
            <div key={b.id} className="card flex flex-col justify-between p-5 space-y-4 border border-sky-100 hover:border-sky-300 transition shadow-sm">
              <div>
                <div className="flex items-center justify-between gap-2 text-xs">
                  <span className="chip bg-sky-50 text-sky-800 border border-sky-200 font-semibold">{b.domain}</span>
                  <span className="text-slate-500 font-medium">{b.role}</span>
                </div>
                <h3 className="mt-2 text-base font-bold text-sky-950">{b.title}</h3>
                <p className="mt-1 text-xs text-slate-600 leading-relaxed">{b.preview}</p>
                <div className="mt-3 rounded-lg bg-sky-50/70 border border-sky-200 p-2.5 text-xs text-sky-900">
                  <span className="font-bold">Central tension: </span>{b.tensions}
                </div>
              </div>

              <div className="pt-2">
                <Link
                  href={`/new?example=${encodeURIComponent(b.id)}`}
                  className="btn-secondary w-full justify-center text-xs font-bold"
                >
                  Load Dilemma into Analyzer →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* The 5-Stage System Pipeline */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-sky-950">
            System Architecture: The 6-Step Pipeline
          </h2>
          <p className="text-sm text-slate-500">
            How DharmaNet transforms a free-text dilemma into structured, transparent decision support.
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {PIPELINE_STEPS.map((s) => (
            <div key={s.step} className="card p-4 space-y-2 border border-sky-100">
              <div className="flex items-center gap-2">
                <span className="grid h-6 w-6 place-items-center rounded-full bg-sky-100 text-xs font-bold text-sky-800 border border-sky-200">
                  {s.step}
                </span>
                <h3 className="font-bold text-sm text-sky-950">{s.title}</h3>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* The 7 Evaluative Frameworks */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-sky-950">
            The 7 Evaluative Ethical Frameworks
          </h2>
          <p className="text-sm text-slate-500">
            Each candidate action is evaluated independently across these ethical traditions.
          </p>
        </div>

        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {FRAMEWORKS.map((f, i) => (
            <div
              key={f.name}
              className={`card p-4 text-xs space-y-2 border border-sky-100 ${
                i === 6
                  ? "md:col-span-2 lg:col-span-3 border-sky-200 bg-sky-50/40"
                  : ""
              }`}
            >
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-sm text-sky-950">{f.name}</h4>
                <span className="chip bg-sky-50 text-sky-700 border border-sky-200">{f.origin}</span>
              </div>
              <p className="text-slate-700 italic">"{f.question}"</p>
              <p className="text-slate-500"><span className="font-semibold text-slate-700">Metric:</span> {f.metric}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Foundational Principle & Human Agency */}
      <section className="card border-sky-200 bg-white p-6 shadow-sm shadow-sky-100 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-sky-950">
            Foundational Principle: Preserving Human Decision Authority
          </h3>
          <span className="chip bg-sky-100 text-sky-800 border border-sky-200 font-semibold text-xs">
            Bhagavad Gita 18.63
          </span>
        </div>
        <p className="text-sm text-slate-700 leading-relaxed">
          In Chapter 18, Verse 63 of the Bhagavad Gita, Krishna presents his full philosophical counsel to Arjuna and concludes:
          <em className="block my-2 font-medium text-sky-900">"iti te jñānam ākhyātaṁ guhyād guhyataraṁ mayā, vimṛśyaitad aśeṣeṇa yathecchasi tathā kuru"</em>
          ("Thus has wisdom more secret than all secrets been declared to you by Me. Reflect on it fully, and then act as you choose.")
        </p>
        <p className="text-xs text-slate-500">
          DharmaNet operationalizes this principle as its architectural mandate: AI serves as a transparent analytical instrument,
          not an automated moral decision-maker. The human user retains ultimate ethical responsibility.
        </p>
      </section>
    </div>
  );
}
