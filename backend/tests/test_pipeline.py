import pytest

from app.schemas.analysis import RevisionRequest
from app.schemas.dilemma import Action, DilemmaContext
from app.schemas.evaluation import DIMENSIONS
from app.services.dilemma.heuristic import structure_dilemma
from tests.conftest import BENCHMARK, WHISTLE

REQUIRED_KINDS = {"direct", "escalate_internal", "escalate_external", "compromise", "gather_info", "delay", "status_quo"}


@pytest.mark.parametrize("case", BENCHMARK, ids=[c["id"] for c in BENCHMARK])
def test_structuring_on_benchmark(case):
    d = structure_dilemma(case["dilemma"], DilemmaContext(**case["context"]))
    assert d.stakeholders[0].category == "decision_maker"
    assert len(d.stakeholders) >= 2 and d.conflicts and d.uncertainties and d.assumptions
    assert {a.kind for a in d.actions} == REQUIRED_KINDS  # no option type silently dropped


@pytest.mark.parametrize("case", BENCHMARK[::4], ids=[c["id"] for c in BENCHMARK[::4]])
def test_full_pipeline_outputs(pipeline, case):
    r = pipeline.run(case["dilemma"], DilemmaContext(**case["context"]))
    assert r.matrix.dimensions == list(DIMENSIONS)
    n = len(r.structured.actions)
    for ev in r.evaluations:
        assert len(ev.scores) == n
        for s in ev.scores:
            assert 0 <= s.score <= 10 and s.rationale and s.confidence_type == "model-estimated"
    assert r.dharma and all(c.entry_ids for rd in r.dharma.readings for c in rd.contributions)
    assert r.explanation.why and r.explanation.trace[-1].stage == "human"
    assert r.sensitivity.label in ("Stable", "Moderately Sensitive", "Highly Sensitive")
    assert len(r.comparison) == n
    assert "not determine objectively correct" in r.disclaimer


def test_explanation_exposes_no_hidden_reasoning_fields(pipeline):
    r = pipeline.run(WHISTLE)
    dumped = r.model_dump_json().lower()
    for banned in ("chain_of_thought", "scratchpad", "<thinking>"):
        assert banned not in dumped


def test_pipeline_is_deterministic(pipeline):
    a, b = pipeline.run(WHISTLE), pipeline.run(WHISTLE)
    assert a.matrix.model_dump() == b.matrix.model_dump()
    assert a.sensitivity.model_dump() == b.sensitivity.model_dump()


def test_without_dharma_layer(pipeline):
    r = pipeline.run(WHISTLE, include_dharma=False)
    assert "dharma" not in r.matrix.dimensions and r.dharma is None
    assert sum(r.matrix.weights.values()) == pytest.approx(1.0)


def test_full_weight_on_one_dimension_selects_that_dimensions_leader(pipeline):
    r = pipeline.run(WHISTLE)
    for dim in ("duty", "care", "consequences"):
        w = {d: (1.0 if d == dim else 0.0) for d in DIMENSIONS}
        rr = pipeline.rescore(r, w)
        best = max(r.matrix.actions, key=lambda a: (r.matrix.cells[a][dim].score, -r.matrix.actions.index(a)))
        assert rr.matrix.weighted[0].action_id == best


def test_equal_weight_and_user_weight_both_reported(pipeline):
    r = pipeline.run(WHISTLE, weights={"duty": 1, "consequences": 0, "fairness": 0, "virtue": 0, "care": 0,
                                       "stakeholder_impact": 0, "dharma": 0})
    assert r.matrix.weights["duty"] == pytest.approx(1.0)
    assert r.matrix.equal_weighted and r.matrix.equal_weight_recommendation


def test_revision_adds_user_action_and_links_parent(pipeline):
    r = pipeline.run(WHISTLE)
    acts = list(r.structured.actions) + [Action(id="u1", label="Consult a whistleblower lawyer", kind="gather_info")]
    rr = pipeline.revise(r, RevisionRequest(actions=acts, assumptions=["Evidence is documented."]))
    assert rr.parent_id == r.id
    new = next(a for a in rr.structured.actions if a.id == "u1")
    assert new.user_added and new.features.information_gain > 0.9  # template profile applied
    assert "u1" in rr.matrix.actions and rr.structured.assumptions == ["Evidence is documented."]


def test_irrelevant_name_swap_does_not_change_result(pipeline):
    base = "My colleague {n} told me our manager falsified safety test results for a product used by children."
    outs = [pipeline.run(base.format(n=n)) for n in ("Aarav", "Emily", "Kwame", "Mei")]
    assert len({o.matrix.recommendation.action_id for o in outs}) == 1
    assert len({o.matrix.weighted[0].score for o in outs}) == 1
