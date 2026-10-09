import pytest

from app.schemas.decision import DecisionMatrix, MatrixCell, Weights
from app.services.decision.engine import aggregate, normalize_weights, rank, recommend
from app.services.decision.sensitivity import analyze, flip_threshold


def cell(s, u=0.5, c=0.7):
    return MatrixCell(score=s, uncertainty=u, confidence=c)


def matrix(scores: dict[str, dict[str, float]], weights: dict[str, float], u=0.5) -> DecisionMatrix:
    dims = list(weights)
    acts = list(scores)
    cells = {a: {d: cell(scores[a][d], u) for d in dims} for a in acts}
    w = normalize_weights(weights, dims)
    r = rank(aggregate(cells, w, dims), acts)
    labels = {a: a for a in acts}
    rec = recommend(r, labels)
    return DecisionMatrix(dimensions=dims, actions=acts, cells=cells, weights=w, weighted=r, equal_weighted=r,
                          recommendation=rec, equal_weight_recommendation=rec)


def test_normalize_weights_sums_to_one_and_handles_zero():
    w = normalize_weights({"duty": 2, "care": 2}, ["duty", "care", "virtue"])
    assert w == {"duty": 0.5, "care": 0.5, "virtue": 0.0}
    assert normalize_weights({}, ["a", "b"]) == {"a": 0.5, "b": 0.5}


def test_weights_validation_rejects_bad_input():
    with pytest.raises(ValueError):
        Weights(values={"duty": -1})
    with pytest.raises(ValueError):
        Weights(values={"not_a_dim": 1})
    with pytest.raises(ValueError):
        Weights(values={"duty": 0})


def test_aggregate_and_uncertainty_propagation():
    cells = {"a": {"x": cell(8, 1.0, 0.8), "y": cell(4, 1.0, 0.6)}}
    s, u, c = aggregate(cells, {"x": 0.5, "y": 0.5}, ["x", "y"])["a"]
    assert s == pytest.approx(6.0)
    assert u == pytest.approx((0.5 ** 2 + 0.5 ** 2) ** 0.5)
    assert c == pytest.approx(0.7)


def test_rank_ties_broken_by_action_order():
    r = rank({"b": (5, 0, 0), "a": (5, 0, 0), "c": (6, 0, 0)}, ["a", "b", "c"])
    assert [x.action_id for x in r] == ["c", "a", "b"]


def test_recommendation_flags_close_calls():
    m = matrix({"a": {"x": 7.0}, "b": {"x": 6.9}}, {"x": 1})
    assert not m.recommendation.clear_preference
    m = matrix({"a": {"x": 9.0}, "b": {"x": 3.0}}, {"x": 1})
    assert m.recommendation.clear_preference


def test_ranking_changes_when_weights_change():
    scores = {"A": {"duty": 9, "cons": 3}, "B": {"duty": 3, "cons": 9}}
    assert matrix(scores, {"duty": 0.8, "cons": 0.2}).weighted[0].action_id == "A"
    assert matrix(scores, {"duty": 0.2, "cons": 0.8}).weighted[0].action_id == "B"


def test_flip_threshold_is_exact():
    # A: duty 9, cons 3 ; B: duty 3, cons 9. Leader A at duty weight .8; flips at exactly .5
    m = matrix({"A": {"duty": 9, "cons": 3}, "B": {"duty": 3, "cons": 9}}, {"duty": 0.8, "cons": 0.2})
    ft = flip_threshold(m, "duty")
    assert ft.stays_top_from == pytest.approx(0.5, abs=1e-4)
    assert ft.stays_top_to == 1.0
    assert ft.below_leader == "B" and ft.above_leader is None
    assert ft.margin_to_flip == pytest.approx(0.3, abs=1e-4)


def test_dominant_action_never_flips_and_is_stable():
    m = matrix({"A": {"x": 9, "y": 9}, "B": {"x": 2, "y": 2}}, {"x": 0.5, "y": 0.5}, u=0.2)
    s = analyze(m, samples=300, seed=1)
    assert s.label == "Stable"
    assert all(f.margin_to_flip == 1.0 for f in s.flip_thresholds)


def test_sensitivity_is_deterministic_for_seed():
    m = matrix({"A": {"x": 6, "y": 5}, "B": {"x": 5, "y": 6}}, {"x": 0.55, "y": 0.45}, u=1.5)
    a, b = analyze(m, 300, 3), analyze(m, 300, 3)
    assert a.model_dump() == b.model_dump()
    assert a.label in ("Moderately Sensitive", "Highly Sensitive")
