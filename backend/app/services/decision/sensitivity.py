"""Deterministic sensitivity analysis.

1. Exact flip thresholds: for each dimension d, vary its weight t∈[0,1] while scaling the other
   weights proportionally. Each action's score is then linear in t, so the range of t over which
   the current leader stays on top is found exactly from pairwise line crossings.
2. Weight stability: seeded Monte-Carlo over Dirichlet-perturbed weights centred on the user's weights.
3. Score stability: seeded Monte-Carlo with each cell score perturbed by its stated ± (normal, sd=±/2).
"""
from __future__ import annotations

import random

from app.schemas.decision import DecisionMatrix, FlipThreshold, Sensitivity

CONCENTRATION = 25.0
SMOOTHING = 0.3


def _leader(scores: dict[str, float], order: list[str]) -> str:
    return min(scores, key=lambda a: (-round(scores[a], 9), order.index(a)))


def flip_threshold(m: DecisionMatrix, dim: str) -> FlipThreshold:
    w, dims, acts = m.weights, m.dimensions, m.actions
    wd = w[dim]
    rest = 1.0 - wd
    lines = {}
    for a in acts:
        s_d = m.cells[a][dim].score
        if rest > 1e-12:
            r = sum(w[x] * m.cells[a][x].score for x in dims if x != dim) / rest
        else:  # all weight on this dimension: other dims share equally when it is lowered
            others = [x for x in dims if x != dim]
            r = sum(m.cells[a][x].score for x in others) / max(1, len(others))
        lines[a] = (s_d - r, r)  # score(t) = r + t*(s_d - r)

    def leader_at(t: float) -> str:
        return _leader({a: lines[a][1] + t * lines[a][0] for a in acts}, acts)

    pts = {0.0, 1.0}
    for i, a in enumerate(acts):
        for b in acts[i + 1:]:
            da, db = lines[a][0] - lines[b][0], lines[b][1] - lines[a][1]
            if abs(da) > 1e-12:
                t = db / da
                if 0 < t < 1:
                    pts.add(t)
    bps = sorted(pts)
    current = leader_at(wd)
    lo, hi = 0.0, 1.0
    for x0, x1 in zip(bps, bps[1:]):
        mid = (x0 + x1) / 2
        if x1 <= wd and leader_at(mid) != current:
            lo = x1
        if x0 >= wd and leader_at(mid) != current and hi == 1.0:
            hi = x0
    below = leader_at(max(0.0, lo - 1e-6)) if lo > 0 else None
    above = leader_at(min(1.0, hi + 1e-6)) if hi < 1 else None
    margin = min(wd - lo if lo > 0 else 1.0, hi - wd if hi < 1 else 1.0)
    return FlipThreshold(dimension=dim, current_weight=round(wd, 4), stays_top_from=round(lo, 4),
                         stays_top_to=round(hi, 4), below_leader=below if below != current else None,
                         above_leader=above if above != current else None, margin_to_flip=round(margin, 4))


def _dirichlet(rng: random.Random, alphas: list[float]) -> list[float]:
    g = [rng.gammavariate(a, 1.0) for a in alphas]
    s = sum(g) or 1.0
    return [x / s for x in g]


def analyze(m: DecisionMatrix, samples: int = 2000, seed: int = 7) -> Sensitivity:
    dims, acts = m.dimensions, m.actions
    leader = m.weighted[0].action_id
    rng = random.Random(seed)

    wins_w = {a: 0 for a in acts}
    alphas = [CONCENTRATION * m.weights[d] + SMOOTHING for d in dims]
    for _ in range(samples):
        ws = _dirichlet(rng, alphas)
        sc = {a: sum(wi * m.cells[a][d].score for wi, d in zip(ws, dims)) for a in acts}
        wins_w[_leader(sc, acts)] += 1

    wins_s = {a: 0 for a in acts}
    for _ in range(samples):
        sc = {}
        for a in acts:
            tot = 0.0
            for d in dims:
                c = m.cells[a][d]
                v = min(10.0, max(0.0, rng.gauss(c.score, c.uncertainty / 2)))
                tot += m.weights[d] * v
            sc[a] = tot
        wins_s[_leader(sc, acts)] += 1

    ws_share = wins_w[leader] / samples
    ss_share = wins_s[leader] / samples
    worst = min(ws_share, ss_share)
    label = "Stable" if worst >= 0.8 else "Moderately Sensitive" if worst >= 0.55 else "Highly Sensitive"
    return Sensitivity(
        leader=leader,
        flip_thresholds=[flip_threshold(m, d) for d in dims],
        weight_stability=round(ws_share, 4), score_stability=round(ss_share, 4),
        win_share_weights={a: round(v / samples, 4) for a, v in wins_w.items()},
        win_share_scores={a: round(v / samples, 4) for a, v in wins_s.items()},
        label=label, samples=samples, seed=seed,
        method_note=(f"Weight stability: share of {samples} Dirichlet weight samples (concentration "
                     f"{CONCENTRATION}) around your weights in which the leader stays first. Score stability: "
                     f"share of {samples} samples with each cell perturbed by its ± (sd = ±/2). "
                     "Label uses the lower of the two: ≥0.80 Stable, ≥0.55 Moderately Sensitive, else Highly Sensitive."),
    )
