# Research framing

## Research question
Can an explainable, structured AI ethical decision-support framework that combines established ethical theories with
culturally contextualized Mahābhārata-inspired reasoning provide more transparent, consistent, and
human-controllable ethical decision support than an unconstrained LLM response?

## Hypotheses (all NOT YET EVALUATED against LLM baselines or users)
* **H1 Transparency** — DharmaNet answers more of the six explanation questions than B1–B3.
* **H2 Consistency** — DharmaNet's leading action is more stable under ethically irrelevant perturbations.
* **H3 Coverage** — DharmaNet identifies more annotated stakeholders and conflicts.
* **H4 Usefulness & calibrated trust** — users rate DharmaNet more useful without increased over-trust.
* **H5 Cultural relevance** — the Dharma layer adds perspectives users find relevant and not misrepresentative.

## Candidate contributions
Listed in the master plan §1. **No novelty is claimed** until a literature review is completed. Areas to review:
machine ethics and computational moral reasoning; LLM moral-judgment consistency and prompt sensitivity;
multi-criteria decision analysis and weight sensitivity; explainable AI and trust calibration; value-sensitive design;
non-Western and Indian philosophical perspectives in AI ethics. (No citations are given here deliberately — they
should be added from an actual literature search, not from memory.)

## Design-level answers to the research problem
| Requirement | Mechanism |
|---|---|
| Structure ambiguous dilemma | staged extraction with editable output |
| Stakeholders, conflicts | typed schemas, user editing, conflict intensity |
| Multiple actions | ≥7 typed options; required types back-filled if an LLM omits them |
| Multiple frameworks | 6 isolated evaluators + Dharma layer |
| Cultural context | cited, paraphrase-only KB with alternative interpretations and limitations |
| Explain why | per-cell rationale + deterministic explanation + trace |
| Uncertainty/disagreement | ±, model-estimated confidence, disagreement annotations, "no clear preference" |
| Compare alternatives | comparison view, equal vs user weights |
| Human control | edits, weights, override, decision record; nothing executed |

## Threats to validity
See [limitations.md](limitations.md). The largest: authored feature profiles (heuristic engine), author-written
annotations, keyword-proxy scoring of baselines, and the absence of a user study.
