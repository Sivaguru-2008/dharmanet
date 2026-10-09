import json

import pytest
from pydantic import BaseModel

from app.llm.base import LLMError
from app.llm.structured import StructuredOutputError, extract_json, generate_structured
from app.services.pipeline import AnalysisPipeline
from tests.conftest import WHISTLE, FakeProvider


class M(BaseModel):
    x: int


def test_extract_json_handles_fences_and_prose():
    assert extract_json('Sure!\n```json\n{"x": 1, "s": "a}b"}\n```') == {"x": 1, "s": "a}b"}
    with pytest.raises(ValueError):
        extract_json("no json here")


def test_retry_then_repair_succeeds():
    outs = iter(["not json", '{"x": "oops"}', '{"x": 3}'])
    p = FakeProvider(lambda u: next(outs))
    assert generate_structured(p, "give x", M, max_retries=2).x == 3
    assert "previous output was invalid" in p.calls[2].lower()


def test_fails_safely_after_retries():
    p = FakeProvider(lambda u: '{"y": 1}')
    with pytest.raises(StructuredOutputError):
        generate_structured(p, "give x", M, max_retries=1)


def test_provider_errors_are_retried():
    state = {"n": 0}

    def resp(u):
        state["n"] += 1
        if state["n"] == 1:
            raise LLMError("network")
        return '{"x": 5}'
    assert generate_structured(FakeProvider(resp), "p", M, 1).x == 5


def test_broken_llm_falls_back_to_heuristic_and_records_it(settings, kb):
    pipe = AnalysisPipeline(settings, kb, FakeProvider(lambda u: "I refuse to answer in JSON"))
    r = pipe.run(WHISTLE)
    assert r.provider.is_llm
    assert any("heuristic" in f for f in r.fallbacks)
    assert all(ev.source == "heuristic_fallback" for ev in r.evaluations)
    assert len(r.structured.actions) == 7


def _good_llm(user: str) -> str:
    if "Structure the following" in user:
        return json.dumps({"summary": "S", "domain": "workplace", "decision_maker": "Engineer",
                           "cues": {k: 0.5 for k in ["severity", "vulnerability", "relational_closeness", "uncertainty",
                                                     "legal_dimension", "urgency", "scale"]}})
    if "Identify ALL stakeholders" in user:
        return json.dumps({"stakeholders": [{"name": "Engineer", "category": "decision_maker", "roles": ["decision_maker"]},
                                            {"name": "Customers", "category": "customers", "roles": ["primary", "vulnerable"]}]})
    if "ethical conflicts" in user:
        return json.dumps({"conflicts": [{"type": "truth_vs_loyalty", "title": "Truth vs loyalty", "between": ["Customers"]}]})
    if "candidate actions" in user:
        f = {k: 0.5 for k in ["prevents_harm", "causes_harm", "honesty", "role_duty", "due_process", "protects_vulnerable",
                              "preserves_relationships", "self_interest", "reversibility", "information_gain",
                              "timeliness", "courage"]}
        return json.dumps({"actions": [{"label": "Report", "kind": "direct", "features": {**f, "honesty": 0.9}},
                                       {"label": "Say nothing", "kind": "status_quo", "features": f},
                                       {"label": "Ask around", "kind": "custom", "features": f}]})
    if "ONE ethical framework" in user:
        ids = [line.split(":")[0] for line in user.splitlines() if line[:1] == "a" and ":" in line[:4]]
        return json.dumps({"scores": [{"action_id": i, "score": 6, "uncertainty": 1, "confidence": 0.6,
                                       "rationale": "r"} for i in ids]})
    if "Dharma-inspired reading" in user:
        ids = [line.split(":")[0] for line in user.splitlines() if line[:1] == "a" and ":" in line[:4]]
        first_entry = next(line.split(" | ")[0] for line in user.splitlines() if " | " in line and "id |" not in line)
        return json.dumps({"readings": [{"action_id": i, "score": 5, "uncertainty": 1, "confidence": 0.5,
                                         "interpretation": "i", "contributions": [
                                             {"concept": "invented", "entry_ids": ["bg-42-1"], "effect": 1, "note": "n"},
                                             {"concept": "real", "entry_ids": [first_entry], "effect": 1, "note": "n"}]}
                                        for i in ids]})
    return "{}"


def test_llm_path_validates_and_backfills_required_options(settings, kb):
    pipe = AnalysisPipeline(settings, kb, FakeProvider(_good_llm))
    r = pipe.run(WHISTLE)
    kinds = [a.kind for a in r.structured.actions]
    for k in ("escalate_internal", "compromise", "gather_info", "delay"):
        assert k in kinds  # required option types never silently missing
    assert r.structured.summary == "S"
    assert all(ev.source == "llm" for ev in r.evaluations)
    assert r.dharma.source == "llm"
    # fabricated citation dropped; only claims citing a retrieved entry survive
    first = r.dharma.retrieved[0].entry_id
    assert r.dharma.dropped_claims == len(r.structured.actions)
    assert all(c.entry_ids == [first] for rd in r.dharma.readings for c in rd.contributions)
    assert any(k.startswith("prompt:") for k in r.versions)
