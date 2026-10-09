"""Deterministic decision engine: weight normalisation, aggregation, ranking, recommendation.

No LLM is involved here. All functions are pure and unit-tested.
"""
from __future__ import annotations

import math

from app.schemas.decision import (
    DecisionMatrix, MatrixCell, Recommendation, WeightedScore,
)
from app.schemas.dharma import DharmaEvaluation
from app.schemas.evaluation import DIMENSIONS, FrameworkEvaluation

Cells = dict[str, dict[str, MatrixCell]]


def normalize_weights(weights: dict[str, float], dimensions: list[str]) -> dict[str, float]:
    w = {d: max(0.0, float(weights.get(d, 0.0))) for d in dimensions}
    total = sum(w.values())
    if total <= 0:
        return {d: 1.0 / len(dimensions) for d in dimensions}
    return {d: v / total for d, v in w.items()}


def equal_weights(dimensions: list[str]) -> dict[str, float]:
    return {d: 1.0 / len(dimensions) for d in dimensions}


def build_cells(evaluations: list[FrameworkEvaluation], dharma: DharmaEvaluation | None,
                action_ids: list[str], include_dharma: bool) -> tuple[list[str], Cells]:
    dims = [d for d in DIMENSIONS if include_dharma or d != "dharma"]
    cells: Cells = {a: {} for a in action_ids}
    for ev in evaluations:
        for s in ev.scores:
            if s.action_id in cells:
                cells[s.action_id][s.dimension] = MatrixCell(score=s.score, uncertainty=s.uncertainty, confidence=s.confidence)
    if include_dharma and dharma is not None:
        for r in dharma.readings:
            if r.action_id in cells:
                cells[r.action_id]["dharma"] = MatrixCell(score=r.score, uncertainty=r.uncertainty, confidence=r.confidence)
    dims = [d for d in dims if all(d in cells[a] for a in action_ids)]
    return dims, cells


def aggregate(cells: Cells, weights: dict[str, float], dims: list[str]) -> dict[str, tuple[float, float, float]]:
    """Weighted score, propagated ± (assumes independent cell errors), weighted confidence."""
    out = {}
    for a, row in cells.items():
        s = sum(weights[d] * row[d].score for d in dims)
        u = math.sqrt(sum((weights[d] * row[d].uncertainty) ** 2 for d in dims))
        c = sum(weights[d] * row[d].confidence for d in dims)
        out[a] = (s, u, c)
    return out


def rank(agg: dict[str, tuple[float, float, float]], order: list[str]) -> list[WeightedScore]:
    """Sort by score desc; ties broken by original action order (deterministic)."""
    ids = sorted(agg, key=lambda a: (-round(agg[a][0], 9), order.index(a)))
    return [WeightedScore(action_id=a, score=round(agg[a][0], 3), uncertainty=round(agg[a][1], 3),
                          confidence=round(agg[a][2], 3), rank=i + 1) for i, a in enumerate(ids)]


def recommend(ranking: list[WeightedScore], labels: dict[str, str]) -> Recommendation:
    top = ranking[0]
    if len(ranking) == 1:
        return Recommendation(action_id=top.action_id, runner_up_id=None, margin=0.0, clear_preference=False,
                              statement="Only one action was evaluated; no comparison is possible.")
    second = ranking[1]
    margin = top.score - second.score
    threshold = max(0.3, 0.5 * math.sqrt(top.uncertainty ** 2 + second.uncertainty ** 2))
    clear = margin >= threshold
    if clear:
        st = (f"Under these weights, '{labels[top.action_id]}' scores highest ({top.score:.2f}), "
              f"{margin:.2f} ahead of '{labels[second.action_id]}'.")
    else:
        st = (f"'{labels[top.action_id]}' and '{labels[second.action_id]}' are within the estimated "
              f"uncertainty of each other (margin {margin:.2f} < {threshold:.2f}); DharmaNet does not "
              f"express a clear preference between them.")
    return Recommendation(action_id=top.action_id, runner_up_id=second.action_id, margin=round(margin, 3),
                          clear_preference=clear, statement=st)


def build_matrix(evaluations: list[FrameworkEvaluation], dharma: DharmaEvaluation | None,
                 action_ids: list[str], labels: dict[str, str], weights: dict[str, float],
                 include_dharma: bool = True) -> DecisionMatrix:
    dims, cells = build_cells(evaluations, dharma, action_ids, include_dharma)
    w = normalize_weights(weights, dims)
    eq = equal_weights(dims)
    r_user = rank(aggregate(cells, w, dims), action_ids)
    r_eq = rank(aggregate(cells, eq, dims), action_ids)
    return DecisionMatrix(
        dimensions=dims, actions=action_ids, cells=cells, weights={d: round(v, 6) for d, v in w.items()},
        weighted=r_user, equal_weighted=r_eq,
        recommendation=recommend(r_user, labels), equal_weight_recommendation=recommend(r_eq, labels),
    )
