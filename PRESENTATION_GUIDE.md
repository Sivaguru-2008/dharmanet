# DharmaNet — Presentation Defense Guide & Walkthrough

> **Prepared for your project presentation.** Use this guide to deliver a clean, authoritative, and scientifically grounded presentation that avoids "AI slop" or vague buzzwords.

---

## 1. The 90-Second Elevator Pitch

> *"When people face complex, agonizing ethical dilemmas, asking standard AI chatbots like ChatGPT gives a single, confident answer. But that answer is a dangerous black box: it hides ethical trade-offs, suffers from moral sycophancy, changes completely if you reword the prompt, and hallucinates moral authority.*
>
> *We built **DharmaNet**: an explainable, multi-framework ethical decision-support system. Instead of telling you what to do, DharmaNet decomposes the dilemma, generates diverse action choices, and evaluates them across **seven independent ethical frameworks** — including classical Western traditions and a source-grounded **Dharma perspective** rooted in the Bhagavad Gita and Mahābhārata.*
>
> *Aggregation, rankings, and Monte Carlo sensitivity testing are handled by **deterministic mathematics**, not LLM opinion. And true to its core philosophical foundation from Bhagavad Gita 18.63 — 'Reflect on this fully, then act as you choose' — **DharmaNet never takes autonomous action; the human retains 100% final moral decision authority.**"*

---

## 2. The Core Problem vs. DharmaNet's Solution

| Flaw of Standard LLM Chatbots | How DharmaNet Solves It |
|---|---|
| **Moral Monism & Sycophancy** (Gives 1 biased opinion) | **Pluralistic Evaluation**: Evaluates all options across 7 distinct ethical paradigms simultaneously. |
| **Hidden Assumptions & Trade-offs** | **Explicit Decomposition**: Deconstructs stakeholders, rights, conflicts, and constraints into editable components. |
| **Fragile Prompt Sensitivity** | **Deterministic Sensitivity Analysis**: Monte Carlo tests reveal whether a choice is genuinely robust or fragile. |
| **Hallucinated Religious/Moral Claims** | **Automated Citation Validator**: Strictly validates all Dharma claims against 28 curated classical verses; uncited claims are dropped. |
| **Machine Usurpation of Agency** | **Human-in-the-Loop Authority**: The human user explicitly records Accept, Alternative, Modify, or Reject. |

---

## 3. The 7 Evaluative Ethical Frameworks

Be ready to name and briefly define each framework:

1. **Consequentialism (Utilitarianism - Bentham/Mill)**: Evaluates net aggregate well-being vs harm across all stakeholders.
2. **Deontological Ethics (Kantian Duty - Kant)**: Checks adherence to universal moral duties, truth-telling, contracts, and rights.
3. **Fairness & Justice (Rawlsian - Rawls)**: Analyzes equity and distribution of harm/benefit under the veil of ignorance, protecting the most vulnerable.
4. **Virtue Ethics (Aristotelian - Aristotle)**: Evaluates what moral character, honesty, courage, and practical wisdom the action reflects.
5. **Ethics of Care (Relational - Carol Gilligan)**: Focuses on preserving relationships, trust, and responsiveness to human vulnerability.
6. **Stakeholder Impact Matrix (Freeman)**: Granular matrix scoring harm (−1) to benefit (+1) for every identified stakeholder (with vulnerable stakeholders weighted 1.5×).
7. **Classical Dharma Ethics (Bhagavad Gita & Mahābhārata)**: Contextual Indian philosophical lens balancing:
   - *Kartavya* (role-based ethical duty)
   - *Loka-samgraha* (universal welfare of society)
   - *Nishkama Karma* (action performed without selfish attachment to fruit)
   - *Ahimsa* (avoidance of injury)

---

## 4. Live Demonstration Script (Step-by-Step)

During your presentation, open `http://localhost:3005` (or double-click `start.bat` / run `start.ps1`):

### Step 1: Landing Page (`/`)
- Show the clean hero and the side-by-side comparison: *Standard LLM vs DharmaNet*.
- Highlight the **7 Frameworks** and the **System Architecture**.
- Click **"Presentation Walkthrough"** to show the 8-slide defense overview if using slides.

### Step 2: Select a Live Case (`/new`)
- Click **"Medical Device Firmware Bug"** from the Preset Cases on the right.
- Point out to the audience:
  - Role: `senior firmware engineer` (informs professional duty).
  - Domain: `healthcare`.
  - The conflict: 400 jobs & company survival vs patient safety.
- Click **"Run Full Multi-Framework Analysis"**.

### Step 3: Structuring Tab (`Step 1: Structuring`)
- Show how free text was broken into:
  - **Stakeholders**: Engineer, Patients, CEO/Mentor, 400 Coworkers, Regulatory Body.
  - **Context Signals**: Severity, Vulnerability, Uncertainty, Urgency.
  - **Candidate Actions**: Not just binary choices, but:
    1. *Escalate internally with a strict deadline*
    2. *Report immediately to the regulator (whistleblow)*
    3. *Seek independent clinical / ethics committee review*
    4. *Attempt an expedited out-of-band firmware hotfix*
    5. *Comply silently with management*

### Step 4: Ethical Matrix Tab (`Step 2: Ethical Matrix`)
- Show the 7x7 matrix.
- Click on the cells:
  - *Reporting to Regulator* scores high on Virtue (6.9) and Deontology, but low on Care/Coworker Stakeholders.
  - *Escalate Internally with Deadline* balances Duty with Care.
- Show the interactive **Radar Chart** comparing ethical profiles.

### Step 5: Dharma Perspective Tab (`Step 3: Dharma Perspective`)
- Show that every claim has a **verifiable scripture citation** (e.g. BG 3.20 for *Loka-samgraha*, BG 2.47 for *Nishkama Karma*).
- Point out the **Citation Validator**: if the AI generated an ungrounded claim, it is automatically dropped.

### Step 6: Weights & Sensitivity Tab (`Step 6: Weights & Sensitivity`)
- **This is the killer feature!**
- Click **"Duty-First (Kant)"** vs **"Outcome-First (Utilitarian)"** vs **"Equal (1:1)"**.
- Show how the rankings update **live in deterministic math**.
- Explain the **Stability Label**: *"Highly Sensitive"* means options are within uncertainty bounds, proving to the user that this dilemma genuinely has no simple black-and-white answer!

### Step 7: Human Decision Tab (`Step 7: Human Decision`)
- Read the quote from **Bhagavad Gita 18.63**:
  *"Reflect on this fully, then act as you choose."*
- Click **"Accept"** or **"Choose Alternative"**, enter your rationale, and record it.
- Show that the machine does not execute actions — the human retains final moral authority.

---

## 5. Answers to Tough Questions from Evaluators

**Q: Why include the Dharma perspective alongside Western frameworks?**
> *"Most AI ethics benchmarks are purely Western-centric (primarily Utilitarian or Kantian). The Dharma tradition provides a sophisticated, duty-and-context-based framework (concept of Dharma Sankata / moral dilemmas, Loka-samgraha / societal welfare, and Nishkama Karma / detached duty) that directly addresses tensions between organizational loyalty and public good. Crucially, we keep it in a separate, clearly cited layer rather than blending it into a generic soup."*

**Q: What prevents the AI from hallucinating religious texts or moral claims?**
> *"Our pipeline has an automated citation validator: every Dharma claim must match an entry in our versioned 28-record knowledge base. If an LLM attempts to generate an uncited or unverifiable verse, the validator prunes it and records the dropped claim in the audit log."*

**Q: Why not let the LLM calculate the final ranking and decision?**
> *"LLM aggregation is vulnerable to hallucination, sycophancy, and prompt instability. In DharmaNet, the LLM is only used for semantic structuring. The aggregation, ranking, exact weight-flip boundaries, and Monte Carlo sensitivity testing are 100% deterministic code."*

**Q: Can DharmaNet run completely offline?**
> *"Yes. DharmaNet includes a transparent offline heuristic engine that uses rule-based parsing and feature tables. The entire benchmark suite runs offline in milliseconds with zero API costs."*

---

## 6. How to Start the System Tomorrow Morning

In the project folder, simply run:
```powershell
.\start.ps1
```
or double-click `start.bat` in Windows File Explorer.
This automatically starts:
- FastAPI backend on `http://localhost:8005`
- Next.js frontend on `http://localhost:3005`
- Opens your browser ready to present!
