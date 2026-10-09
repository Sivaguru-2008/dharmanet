# Limitations

## System
* **Heuristic engine is shallow.** Keyword rules and authored feature profiles; it does not understand negation,
  hypotheticals or contradictions, and action options are templates per situation type. Scores therefore reflect the
  authors' profile table as much as the dilemma. Use an LLM provider for semantic analysis.
* **LLM path is less tested than the heuristic path.** It is covered by tests with a scripted fake provider (validation,
  retry, repair, fallback, citation dropping) but has not been evaluated against real models.
* **Scores are not calibrated.** "Confidence" and "±" are model-estimated and labelled as such; they are not probabilities.
* **Linear compensatory aggregation** can let high scores elsewhere offset a rights violation (flagged, not vetoed).
* **Score-noise stability assumes independent cell errors**, which overstates independence between related frameworks.

## Dharma layer
* A computational interpretation of 28 selected passages — not a representation of Hindu philosophy as a whole, nor of
  any particular tradition (Advaita, Vishishtadvaita, Dvaita, modern readings, …).
* Paraphrases and references are written by the authors and **await scholarly review**. Mahābhārata episodes are cited
  at parva level only.
* Concept-to-feature mappings (e.g. svadharma ↔ role duty) are interpretive design choices.

## Evaluation
* Benchmark (22 cases) and annotations are author-written, not expert-validated; coverage metrics partly measure
  agreement with the authors' own lexicon (circularity).
* Free-text baselines are scored with keyword proxies.
* LLM baselines, model-change robustness and the human study are **NOT YET EVALUATED**.

## Privacy & security
* Anonymisation redacts emails, phone numbers and URLs only — **names are not redacted**.
* Rate limiting is in-memory per process; the optional bearer token is a single shared secret, not user accounts.
  The `users` table is auth-ready but there is no login.
* Dilemma text is stored by default (set `DHARMANET_STORE_DILEMMA_TEXT=false` to disable; revision then loses access to the original text).

## Deployment
* The Docker configuration was validated with `docker compose config` but the images were not built in the
  development environment (Docker daemon unavailable). PostgreSQL support uses standard SQLAlchemy types but was not
  exercised by the automated tests (SQLite only).
