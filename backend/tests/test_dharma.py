import json

import pytest

from app.rag.knowledge import KnowledgeBaseError, kb_index, load_kb
from app.schemas.dharma import ConceptContribution, DharmaActionReading, DharmaEvaluation
from app.services.dharma.engine import RULES, DharmaEngine, validate_citations
from app.services.dilemma.heuristic import structure_dilemma
from tests.conftest import WHISTLE


def test_kb_integrity(kb):
    idx = kb_index(kb)
    assert len(idx) == len(kb.entries) >= 25
    for e in kb.entries:
        assert e.text_type == "paraphrase" and e.paraphrase and e.interpretation and e.limitations
        if e.source == "Mahabharata":
            assert e.verse is None, "Mahabharata entries are cited at parva level only"
        else:
            assert 1 <= int(e.chapter) <= 18


def test_every_rule_cites_existing_entries(kb):
    idx = kb_index(kb)
    for r in RULES:
        assert r.entry_ids and all(e in idx for e in r.entry_ids)


def test_kb_loader_rejects_duplicates(tmp_path, settings):
    data = json.loads(open(settings.knowledge_path, encoding="utf-8").read())
    data["entries"].append(data["entries"][0])
    p = tmp_path / "kb.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(KnowledgeBaseError):
        load_kb(p)


def test_retrieval_finds_relevant_concepts(kb):
    d = structure_dilemma(WHISTLE)
    ids = [r.entry_id for r in DharmaEngine(kb).retrieve(d)]
    assert "bg-3-20" in ids  # lokasangraha / public welfare
    assert any(i in ids for i in ("bg-2-38", "bg-2-47"))  # attachment to personal outcome (job loss)


def test_all_dharma_claims_are_grounded_in_retrieved_entries(kb):
    d = structure_dilemma(WHISTLE)
    eng = DharmaEngine(kb)
    ev = eng.evaluate(d)
    retrieved = {r.entry_id for r in ev.retrieved}
    assert ev.readings and ev.dropped_claims == 0
    for r in ev.readings:
        for c in r.contributions:
            assert c.entry_ids and set(c.entry_ids) <= retrieved


def test_validator_drops_fabricated_citations(kb):
    ev = DharmaEvaluation(kb_version=kb.version, retrieved=[], overview="", readings=[DharmaActionReading(
        action_id="a1", score=5, uncertainty=1, confidence=0.5, interpretation="",
        contributions=[ConceptContribution(concept="fake", entry_ids=["bg-99-1"], effect=1, note="x"),
                       ConceptContribution(concept="real", entry_ids=["bg-2-47", "made-up"], effect=1, note="y")])])
    out = validate_citations(ev, kb)
    assert out.dropped_claims == 1
    assert out.readings[0].contributions[0].entry_ids == ["bg-2-47"]


def test_status_quo_scores_lowest_on_dharma_for_serious_harm(kb):
    d = structure_dilemma(WHISTLE)
    ev = DharmaEngine(kb).evaluate(d)
    by_kind = {a.kind: next(r.score for r in ev.readings if r.action_id == a.id) for a in d.actions}
    assert by_kind["status_quo"] == min(by_kind.values())
