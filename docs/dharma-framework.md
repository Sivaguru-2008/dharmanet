# Dharma-inspired reasoning layer

## Position

The Dharma layer is **DharmaNet's computational interpretation** of selected concepts from the Bhagavad Gita and
Mahābhārata. It is kept separate from the established frameworks (its own dimension, tab, disclaimer and weight) so
that researchers and users can see — and switch off — its effect. It is *inspired by selected philosophical concepts
and textual interpretations*; it is not religious authority and not a definitive reading of Hindu philosophy.

Design commitments:
* **Svadharma is read as role/commitment-based responsibility, never by birth or caste.** Varna-based readings are named
  as the traditional context and explicitly rejected.
* The Gita is not reduced to "always do your duty": the layer combines duty with non-attachment, welfare of the world,
  non-harm, truthfulness, discernment under uncertainty, impartiality, and the epic's critique of complicit silence and
  rigid loyalty.
* Bhagavad Gita 18.63 (paraphrased: *reflect fully, then act as you choose*) grounds the human-authority principle.

## Knowledge base (`knowledge/dharma_kb.json`, v0.1)

28 records (21 Gita, 7 Mahābhārata). Schema: `id, concept, sanskrit_term, source, chapter, verse, citation, text_type,
paraphrase, interpretation, alternative_interpretations, ethical_dimension, applicability, keywords, limitations,
verification_status`.

Source rules:
* `paraphrase` fields are short paraphrases written for this project — **not translations, not quotations**.
* Gita references use standard chapter.verse numbering and are limited to widely cited verses (2.7, 2.31, 2.33, 2.38,
  2.47, 2.62–63, 3.8, 3.19, 3.20, 3.21, 3.35, 4.17, 4.18, 5.18, 6.32, 12.13, 16.1–3, 17.15, 18.25, 18.30, 18.63).
* Mahābhārata episodes are cited at **parva level only** (verse numbering differs between the BORI Critical Edition and
  vulgate). For primary text see the public-domain K. M. Ganguli translation.
* Every record is `needs_scholarly_review`. **A qualified scholar should verify all references and paraphrases before
  any publication.** The loader enforces structural checks (unique ids, Gita chapter 1–18, parva present).

## Pipeline

1. **Tags** from conflicts and cues (e.g. `organizational_loyalty_vs_public_safety → whistleblowing, public_welfare, …`).
2. **Retrieval** — TF-IDF cosine over concept/paraphrase/interpretation/keywords + keyword hits + tag overlap; top 12.
3. **Concept rules** (`RULES` in `services/dharma/engine.py`) — a rule contributes **only if at least one of its source
   entries was retrieved**; its effect is scaled by retrieval relevance and cites only retrieved entries.

| Concept | Entries | Effect (points, before relevance scaling) |
|---|---|---|
| Svadharma | 2.31, 3.35 | 2.0·(role_duty−.5) |
| Nishkama karma | 2.47, 3.19, 2.38 | 1.6·(.5−self_interest) + 0.6·(courage−.5) |
| Lokasangraha | 3.20, 3.21 | 2.0·(prevents−.5)·(0.5+0.5·scale) |
| Ahimsa & compassion | 6.32, 12.13, MBh Anushasana | 1.2·(protects_vuln−.5) + 1.2·(.5−causes) |
| Satya | 16.1–3, 17.15, MBh Drona, MBh Vidura | 2.0·(honesty−.5) |
| Viveka | 18.30, 18.25, 2.62–63 | uncertainty-weighted info-gain & reversibility; −0.8 for reckless action under high uncertainty |
| Inaction is a choice | 3.8, 2.33, 4.18 | −1.5·max(0,.5−timeliness)·2·severity |
| Complicity through silence | MBh Sabha | −1.2·vulnerability·max(0,.4−prevents)/.4 |
| Loyalty and its limits | MBh Adi (Bhishma), Udyoga (Karna) | 0.8·closeness·(relationships−.5) |
| Sama-darshana | 5.18, MBh Aranya (Yaksha) | 1.0·(due_process−.5) + 0.6·(protects_vuln−.5) |
| Apaddharma | MBh Shanti | 1.2·urgency·(timeliness−.5) |

Retrieval of 4.17 or 2.7 (the subtlety of action / moral perplexity) widens the ± of every Dharma reading.

4. **Citation validator** — any contribution citing an unknown or non-retrieved entry is removed and counted
   (`dropped_claims`). With an LLM, the model receives only retrieved entries and must cite their ids.

## Known tensions surfaced to users
* Nishkama karma vs. consequentialism (whether outcomes matter).
* "Holding the world together" (3.20) read as preserving order vs. as the welfare of all.
* Ahimsa as highest dharma vs. the epic's framing of a necessary war.
* Apaddharma's openness to abuse as a rationalisation.
