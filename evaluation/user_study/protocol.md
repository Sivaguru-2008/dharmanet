# User study protocol (draft — NOT YET CONDUCTED)

**Status:** design only. No participants have been recruited and no results exist. Obtain institutional ethics
(IRB) approval before running.

## Design
Within-subjects, counterbalanced. Each participant analyses 4 benchmark dilemmas (2 per condition), order and
case-to-condition assignment counterbalanced (Latin square).

| Condition | What participants see |
|---|---|
| LLM-only | the free-text answer to "Analyze this ethical dilemma." from the same LLM used by DharmaNet |
| DharmaNet | the full interface (matrix, Dharma perspective, explanation, sensitivity, decision screen) |

## Participants
Target n ≥ 24 (pilot n = 6). Adults; mix of professional backgrounds; record familiarity with Indian philosophy
(none / some / substantial) because it moderates the cultural-relevance measure. No sensitive demographics required.

## Procedure
1. Consent; 2-minute tutorial for each interface.
2. For each dilemma: read → use the assigned condition (max 10 min) → record own decision and confidence → questionnaire.
3. Final comparative questions and a short semi-structured interview.

## Measures
Likert items in `questionnaire.md` (usefulness, transparency, trust calibration, explanation quality, consistency,
ease of understanding, cultural relevance, decision confidence, willingness to use), time on task, decision changes,
and agreement with the system's leading option (to detect over-reliance).

## Analysis plan
Wilcoxon signed-rank per construct (Holm correction); report effect sizes and medians; qualitative thematic analysis
of interviews. Pre-register before data collection.

## Ethics
Use benchmark dilemmas only — participants must not enter real personal dilemmas. Remind participants that DharmaNet
is decision support, not advice. Debrief on the system's limitations.
