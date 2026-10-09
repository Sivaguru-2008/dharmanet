"""Dharma-inspired reasoning layer (culturally contextualized interpretive layer).

Pipeline: dilemma → tags → retrieve KB entries → apply concept rules ONLY for concepts whose
source entries were retrieved → per-action reading with citations → citation validator.

This layer is explicitly distinguished from the established ethical frameworks: it is DharmaNet's
computational interpretation of selected concepts, not an authoritative reading of the texts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.schemas.dharma import (
    ConceptContribution, DharmaActionReading, DharmaEvaluation, KnowledgeBase, RetrievedEntry,
)
from app.schemas.dilemma import ActionFeatures, ContextCues, StructuredDilemma
from app.rag.knowledge import kb_index
from app.rag.retriever import LexicalRetriever, Retriever

CONFLICT_TAGS: dict[str, list[str]] = {
    "organizational_loyalty_vs_public_safety": ["whistleblowing", "public_welfare", "conflict_of_loyalty", "organization"],
    "truth_vs_loyalty": ["truthfulness", "conflict_of_loyalty", "relationships", "deception"],
    "individual_vs_collective": ["public_welfare", "fairness"],
    "legal_vs_moral": ["role_duty", "authority"],
    "justice_vs_mercy": ["compassion", "fairness"],
    "self_interest_vs_social_responsibility": ["self_interest", "outcome_attachment", "fear", "courage"],
    "autonomy_vs_beneficence": ["autonomy", "compassion"],
    "privacy_vs_safety": ["harm", "truthfulness"],
    "short_vs_long_term": ["consequences"],
    "duty_vs_consequence": ["role_duty", "consequences"],
}


def dilemma_tags(d: StructuredDilemma) -> list[str]:
    tags = {"role_duty", "inaction", "deliberation"}
    for c in d.conflicts:
        tags.update(CONFLICT_TAGS.get(c.type, []))
    cu = d.cues
    if cu.uncertainty >= 0.45:
        tags.update(["uncertainty", "deliberation"])
    if cu.urgency >= 0.6:
        tags.update(["crisis", "urgency"])
    if cu.vulnerability >= 0.5:
        tags.update(["vulnerable", "compassion", "harm"])
    if cu.relational_closeness >= 0.4:
        tags.update(["family", "relationships"])
    if cu.severity >= 0.6:
        tags.add("harm")
    return sorted(tags)


Effect = Callable[[ActionFeatures, ContextCues], float]


@dataclass(frozen=True)
class ConceptRule:
    concept: str
    entry_ids: tuple[str, ...]
    effect: Effect
    positive: str
    negative: str


RULES: list[ConceptRule] = [
    ConceptRule("Svadharma (role-based duty)", ("bg-2-31", "bg-3-35"),
                lambda f, c: 2.0 * (f.role_duty - 0.5),
                "honours the responsibilities of the decision-maker's role",
                "steps away from the responsibilities of the decision-maker's role"),
    ConceptRule("Nishkama karma (action without attachment to personal reward)", ("bg-2-47", "bg-3-19", "bg-2-38"),
                lambda f, c: 1.6 * (0.5 - f.self_interest) + 0.6 * (f.courage - 0.5),
                "is not driven by personal gain or fear of personal loss",
                "appears motivated by personal safety or gain rather than what ought to be done"),
    ConceptRule("Lokasangraha (welfare of the wider community)", ("bg-3-20", "bg-3-21"),
                lambda f, c: 2.0 * (f.prevents_harm - 0.5) * (0.5 + 0.5 * c.scale),
                "serves the welfare of the wider community",
                "leaves the wider community exposed"),
    ConceptRule("Ahimsa and compassion (non-harm)", ("bg-6-32", "bg-12-13", "mbh-ahimsa"),
                lambda f, c: 1.2 * (f.protects_vulnerable - 0.5) + 1.2 * (0.5 - f.causes_harm),
                "protects the vulnerable while limiting collateral harm",
                "causes or permits harm to those affected"),
    ConceptRule("Satya (truthfulness)", ("bg-16-1-3", "bg-17-15", "mbh-drona-ashvatthama", "mbh-vidura-counsel"),
                lambda f, c: 2.0 * (f.honesty - 0.5),
                "is truthful and transparent",
                "relies on concealment or partial truth (cf. the cost of Yudhishthira's half-truth)"),
    ConceptRule("Viveka / sattvic discernment", ("bg-18-30", "bg-18-25", "bg-2-62-63"),
                lambda f, c: (1.5 * c.uncertainty * (f.information_gain - 0.5)
                              + 1.0 * c.uncertainty * (f.reversibility - 0.5)
                              - (0.8 if (f.timeliness > 0.85 and f.information_gain < 0.3 and c.uncertainty > 0.5) else 0.0)),
                "reflects discernment proportionate to the uncertainty",
                "risks acting without adequate discernment given the uncertainty"),
    ConceptRule("Inaction is also a choice", ("bg-3-8", "bg-2-33", "bg-4-18"),
                lambda f, c: -1.5 * max(0.0, 0.5 - f.timeliness) * 2 * c.severity,
                "engages responsibly rather than withdrawing",
                "amounts to withdrawal, which the Gita treats as a consequential choice"),
    ConceptRule("Complicity through silence", ("mbh-sabha-draupadi",),
                lambda f, c: -1.2 * c.vulnerability * max(0.0, 0.4 - f.prevents_harm) / 0.4,
                "does not stand by while the vulnerable are wronged",
                "resembles the assembly's silence while a vulnerable person was wronged"),
    ConceptRule("Loyalty and its limits", ("mbh-bhishma-vow", "mbh-karna-loyalty"),
                lambda f, c: 0.8 * c.relational_closeness * (f.preserves_relationships - 0.5),
                "honours genuine bonds of loyalty",
                "strains bonds of loyalty (which the epic shows can bind people to wrong causes)"),
    ConceptRule("Sama-darshana (impartiality)", ("bg-5-18", "mbh-yaksha-impartiality"),
                lambda f, c: 1.0 * (f.due_process - 0.5) + 0.6 * (f.protects_vulnerable - 0.5),
                "treats those affected impartially",
                "risks partiality toward some stakeholders"),
    ConceptRule("Apaddharma (conduct in emergencies)", ("mbh-shanti-apaddharma",),
                lambda f, c: 1.2 * c.urgency * (f.timeliness - 0.5),
                "responds to genuine urgency (the burden of proving an emergency remains)",
                "may be too slow if the emergency is real"),
]

UNCERTAINTY_ENTRIES = ("bg-4-17", "bg-2-7")


class DharmaEngine:
    def __init__(self, kb: KnowledgeBase, retriever: Retriever | None = None, k: int = 12):
        self.kb = kb
        self.index = kb_index(kb)
        self.retriever = retriever or LexicalRetriever(kb)
        self.k = k

    def retrieve(self, d: StructuredDilemma) -> list[RetrievedEntry]:
        query = " ".join([d.dilemma_text, d.context.additional, " ".join(c.title for c in d.conflicts)])
        return self.retriever.retrieve(query, dilemma_tags(d), self.k)

    def evaluate(self, d: StructuredDilemma, retrieved: list[RetrievedEntry] | None = None) -> DharmaEvaluation:
        retrieved = retrieved if retrieved is not None else self.retrieve(d)
        rel = {r.entry_id: r.relevance for r in retrieved}
        max_rel = max(rel.values(), default=1.0)
        subtle = any(e in rel for e in UNCERTAINTY_ENTRIES)
        readings = []
        for a in d.actions:
            contribs = []
            for rule in RULES:
                cited = [e for e in rule.entry_ids if e in rel]
                if not cited:
                    continue  # concept not grounded in retrieved sources → not used
                scale = 0.5 + 0.5 * max(rel[e] for e in cited) / max_rel
                effect = round(rule.effect(a.features, d.cues) * scale, 3)
                if abs(effect) < 0.05:
                    continue
                contribs.append(ConceptContribution(
                    concept=rule.concept, entry_ids=cited, effect=effect,
                    note=f"This option {rule.positive if effect > 0 else rule.negative}."))
            score = max(0.0, min(10.0, 5 + sum(c.effect for c in contribs)))
            pm = round(0.9 + 1.4 * d.cues.uncertainty + (0.4 if subtle else 0.0), 1)
            conf = round(max(0.3, min(0.8, 0.75 - 0.35 * d.cues.uncertainty - (0.05 if subtle else 0))), 2)
            readings.append(DharmaActionReading(
                action_id=a.id, score=round(score, 2), uncertainty=pm, confidence=conf,
                interpretation=self._interpret(a.label, contribs),
                contributions=sorted(contribs, key=lambda c: -abs(c.effect)),
                limitations=self._limitations(contribs),
            ))
        ev = DharmaEvaluation(
            source="heuristic", kb_version=self.kb.version, retrieved=retrieved, readings=readings,
            overview=self._overview(retrieved, subtle),
        )
        return validate_citations(ev, self.kb, allowed=set(rel))

    @staticmethod
    def _interpret(label: str, contribs: list[ConceptContribution]) -> str:
        if not contribs:
            return f"No retrieved concept bears strongly on '{label}'."
        pos = [c for c in sorted(contribs, key=lambda c: -c.effect) if c.effect > 0][:2]
        neg = [c for c in sorted(contribs, key=lambda c: c.effect) if c.effect < 0][:1]
        parts = []
        if pos:
            parts.append("Read through " + " and ".join(c.concept.split(" (")[0] for c in pos)
                         + f", '{label}' " + "; it ".join(c.note[len('This option '):].rstrip('.') for c in pos) + ".")
        if neg:
            parts.append(f"A tension: through {neg[0].concept.split(' (')[0]}, it {neg[0].note[len('This option '):]}")
        return " ".join(parts)

    def _limitations(self, contribs: list[ConceptContribution]) -> list[str]:
        out: list[str] = []
        for c in contribs[:3]:
            for eid in c.entry_ids[:1]:
                for lim in self.index[eid].limitations[:1]:
                    if lim not in out:
                        out.append(lim)
        return out

    @staticmethod
    def _overview(retrieved: list[RetrievedEntry], subtle: bool) -> str:
        names = ", ".join(dict.fromkeys(r.concept for r in retrieved[:5]))
        s = f"Most relevant retrieved concepts: {names}."
        if subtle:
            s += (" The Gita itself stresses that the nature of right action is hard to discern (4.17), "
                  "so these readings carry wide uncertainty.")
        return s


def validate_citations(ev: DharmaEvaluation, kb: KnowledgeBase, allowed: set[str] | None = None) -> DharmaEvaluation:
    """Drop any Dharma claim that cites an unknown KB entry (or one that was not retrieved).
    Claims left with no valid citation are removed entirely and counted."""
    known = set(kb_index(kb))
    ok_ids = known & allowed if allowed is not None else known
    dropped = 0
    for r in ev.readings:
        kept = []
        for c in r.contributions:
            ids = [i for i in c.entry_ids if i in ok_ids]
            if ids:
                kept.append(c.model_copy(update={"entry_ids": ids}))
            else:
                dropped += 1
        r.contributions = kept
    ev.retrieved = [x for x in ev.retrieved if x.entry_id in known]
    ev.dropped_claims += dropped
    return ev
