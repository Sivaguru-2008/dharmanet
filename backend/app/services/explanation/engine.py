"""Explanation engine: answers the six explanation questions and builds the structured reasoning
trace + per-action comparison from recorded pipeline outputs (never from hidden model reasoning)."""
from __future__ import annotations

from app.schemas.decision import ActionComparison, DecisionMatrix, Explanation, Sensitivity, TraceStep
from app.schemas.dharma import DharmaEvaluation
from app.schemas.dilemma import StructuredDilemma
from app.schemas.evaluation import DIMENSION_LABELS, DimensionScore, FrameworkEvaluation


def _cell_index(evaluations: list[FrameworkEvaluation]) -> dict[tuple[str, str], DimensionScore]:
    return {(s.action_id, s.dimension): s for ev in evaluations for s in ev.scores}


def annotate_disagreements(evaluations: list[FrameworkEvaluation], dharma: DharmaEvaluation | None) -> None:
    """Fill DimensionScore.potential_disagreement deterministically: name the dimension that
    diverges most from this cell for the same action."""
    scores: dict[str, dict[str, float]] = {}
    for ev in evaluations:
        for s in ev.scores:
            scores.setdefault(s.action_id, {})[s.dimension] = s.score
    if dharma:
        for r in dharma.readings:
            scores.setdefault(r.action_id, {})["dharma"] = r.score
    for ev in evaluations:
        for s in ev.scores:
            others = {d: v for d, v in scores[s.action_id].items() if d != s.dimension}
            if not others:
                continue
            d, v = max(others.items(), key=lambda kv: abs(kv[1] - s.score))
            if abs(v - s.score) >= 1.5:
                rel = "higher" if v > s.score else "lower"
                s.potential_disagreement = (f"{DIMENSION_LABELS[d]} rates this action {abs(v - s.score):.1f} "
                                            f"points {rel} ({v:.1f}/10).")
            else:
                s.potential_disagreement = "Other frameworks broadly agree on this action (within 1.5 points)."


def explain(d: StructuredDilemma, evaluations: list[FrameworkEvaluation], dharma: DharmaEvaluation | None,
            m: DecisionMatrix, sens: Sensitivity, fallbacks: list[str]) -> Explanation:
    labels = {a.id: a.label for a in d.actions}
    names = {s.id: s.name for s in d.stakeholders}
    rec = m.recommendation
    top = rec.action_id
    top_ws = m.weighted[0]
    cells = _cell_index(evaluations)

    leaders = {dim: max(m.actions, key=lambda a: (m.cells[a][dim].score, -m.actions.index(a))) for dim in m.dimensions}
    best_dims = [DIMENSION_LABELS[dim] for dim, a in leaders.items()
                 if a == top or m.cells[a][dim].score - m.cells[top][dim].score < 0.3]
    why = rec.statement + (f" It leads on: {', '.join(best_dims)}." if best_dims else
                           " It does not lead on any single dimension but has the best overall balance.")

    # contribution of each dimension relative to the mean action
    mean = {dim: sum(m.cells[a][dim].score for a in m.actions) / len(m.actions) for dim in m.dimensions}
    contrib = sorted(((m.weights[dim] * (m.cells[top][dim].score - mean[dim]), dim) for dim in m.dimensions), reverse=True)
    principles = []
    for val, dim in contrib[:3]:
        if val <= 0:
            continue
        if dim == "dharma" and dharma:
            r = next(r for r in dharma.readings if r.action_id == top)
            cites = ", ".join(sorted({e for c in r.contributions[:2] for e in c.entry_ids}))
            principles.append(f"Dharma-inspired reading ({cites}): {r.interpretation}")
        else:
            c = cells.get((top, dim))
            if c:
                principles.append(f"{DIMENSION_LABELS[dim]} — {c.principle} ({c.score:.1f}/10)")

    impacts = next((ev.stakeholder_impacts for ev in evaluations if ev.stakeholder_impacts), [])
    top_imp = sorted([i for i in impacts if i.action_id == top], key=lambda i: -abs(i.impact))[:4]
    key_stakeholders = [f"{names.get(i.stakeholder_id, i.stakeholder_id)}: "
                        f"{'helped' if i.impact > 0 else 'harmed'} ({i.impact:+.2f}; {i.note})" for i in top_imp]

    assumptions = list(d.assumptions)
    for dim in m.dimensions:
        c = cells.get((top, dim))
        for a in (c.assumptions if c else []):
            if a not in assumptions:
                assumptions.append(a)

    change = []
    for ft in sorted(sens.flip_thresholds, key=lambda f: f.margin_to_flip):
        if ft.margin_to_flip >= 0.3:
            continue
        lab = DIMENSION_LABELS[ft.dimension]
        if ft.above_leader:
            change.append(f"If the weight on {lab} rose above {ft.stays_top_to:.0%} (now {ft.current_weight:.0%}), "
                          f"'{labels[ft.above_leader]}' would rank first.")
        if ft.below_leader:
            change.append(f"If the weight on {lab} fell below {ft.stays_top_from:.0%} (now {ft.current_weight:.0%}), "
                          f"'{labels[ft.below_leader]}' would rank first.")
    if sens.score_stability < 0.8:
        alt = max((a for a in sens.win_share_scores if a != top), key=lambda a: sens.win_share_scores[a], default=None)
        if alt:
            change.append(f"Within the stated score uncertainty, '{labels[alt]}' comes out on top in "
                          f"{sens.win_share_scores[alt]:.0%} of samples.")
    change += [f"Clarifying: {u}" for u in d.uncertainties[:3]]

    disagreements = []
    for dim, a in leaders.items():
        if a != top and m.cells[a][dim].score - m.cells[top][dim].score >= 0.3:  # ignore near-ties
            disagreements.append(f"{DIMENSION_LABELS[dim]} favours '{labels[a]}' ({m.cells[a][dim].score:.1f}) "
                                 f"over '{labels[top]}' ({m.cells[top][dim].score:.1f}).")
    if not disagreements:
        disagreements.append("No dimension favours another action by 0.3 points or more; frameworks differ in degree, not direction.")

    trace = _trace(d, evaluations, dharma, m, sens, labels, leaders, fallbacks, top_ws.score)
    return Explanation(why=why, principles=principles, key_stakeholders=key_stakeholders,
                       assumptions=assumptions[:10], what_could_change=change, disagreements=disagreements,
                       trace=trace)


def _trace(d, evaluations, dharma, m, sens, labels, leaders, fallbacks, top_score) -> list[TraceStep]:
    steps: list[str] = []
    vul = [s.name for s in d.stakeholders if s.is_vulnerable]
    steps.append(("understanding", f"Structured the dilemma (domain: {d.domain}); identified {len(d.stakeholders)} "
                  f"stakeholders" + (f", vulnerable: {', '.join(vul)}" if vul else "") + "."))
    if d.conflicts:
        top_c = sorted(d.conflicts, key=lambda c: -c.intensity)[:3]
        steps.append(("conflicts", "Identified conflicts: " + "; ".join(f"{c.title} (intensity {c.intensity:.2f})" for c in top_c) + "."))
    steps.append(("actions", f"Generated {len(d.actions)} candidate actions including information-gathering, "
                  "compromise, escalation, delay and status-quo options; none were removed."))
    for ev in evaluations:
        best = max(ev.scores, key=lambda s: s.score)
        flags = sorted({f for s in ev.scores for f in s.flags})
        steps.append(("framework", f"{ev.framework_name} (evaluated independently) favoured '{labels[best.action_id]}' "
                      f"({best.score:.1f}/10)" + (f"; flags: {', '.join(flags)}" if flags else "") + "."))
    if dharma:
        concepts = list(dict.fromkeys(r.concept for r in dharma.retrieved[:4]))
        best = max(dharma.readings, key=lambda r: r.score)
        steps.append(("dharma", f"Retrieved {len(dharma.retrieved)} knowledge-base entries (top: {', '.join(concepts)}); "
                      f"Dharma-inspired reading favoured '{labels[best.action_id]}' ({best.score:.1f}/10)"
                      + (f"; citation validator removed {dharma.dropped_claims} unsupported claim(s)" if dharma.dropped_claims else "") + "."))
    steps.append(("aggregation", f"Combined {len(m.dimensions)} dimensions with weights "
                  + ", ".join(f"{DIMENSION_LABELS[k]} {v:.0%}" for k, v in m.weights.items())
                  + f"; '{labels[m.recommendation.action_id]}' scored {top_score:.2f}."))
    steps.append(("comparison", f"Equal-weight analysis ranks '{labels[m.equal_weight_recommendation.action_id]}' first."))
    steps.append(("sensitivity", f"Recommendation stability: {sens.label} (weight stability {sens.weight_stability:.0%}, "
                  f"score stability {sens.score_stability:.0%})."))
    if fallbacks:
        steps.append(("fallbacks", "Fallbacks used: " + "; ".join(fallbacks) + "."))
    steps.append(("human", "Final decision left to the human decision-maker."))
    return [TraceStep(step=i + 1, stage=s, summary=t) for i, (s, t) in enumerate(steps)]


def compare(d: StructuredDilemma, evaluations: list[FrameworkEvaluation], dharma: DharmaEvaluation | None,
            m: DecisionMatrix) -> list[ActionComparison]:
    names = {s.id: s.name for s in d.stakeholders}
    cells = _cell_index(evaluations)
    impacts = next((ev.stakeholder_impacts for ev in evaluations if ev.stakeholder_impacts), [])
    ws = {w.action_id: w for w in m.weighted}
    out = []
    for a in d.actions:
        f = a.features
        row = {dim: m.cells[a.id][dim].score for dim in m.dimensions}
        ordered = sorted(row, key=lambda k: -row[k])
        strengths, weaknesses = [], []
        for dim in m.dimensions:
            c = cells.get((a.id, dim))
            if c:
                strengths += [f"{DIMENSION_LABELS[dim]}: {x}" for x in c.strengths[:1]]
                weaknesses += [f"{DIMENSION_LABELS[dim]}: {x}" for x in c.weaknesses[:1]]
        imp = [i for i in impacts if i.action_id == a.id]
        risks = []
        if f.reversibility < 0.35:
            risks.append("Hard to reverse if the facts turn out to be different.")
        if f.prevents_harm < 0.4:
            risks.append("The threatened harm may continue or materialise.")
        if f.preserves_relationships < 0.35:
            risks.append("Likely damage to relationships and trust.")
        if f.courage > 0.75:
            risks.append("Personal risk to the decision-maker (retaliation, career or legal exposure).")
        if f.honesty < 0.35:
            risks.append("Involves concealment, which can compound harm if discovered.")
        spread = max(row.values()) - min(row.values())
        dv = ""
        if dharma:
            r = next((r for r in dharma.readings if r.action_id == a.id), None)
            if r:
                cites = sorted({e for c in r.contributions for e in c.entry_ids})
                dv = r.interpretation + (f" [sources: {', '.join(cites)}]" if cites else "")
        w = ws[a.id]
        out.append(ActionComparison(
            action_id=a.id, label=a.label,
            strengths=list(dict.fromkeys(strengths))[:5], weaknesses=list(dict.fromkeys(weaknesses))[:5],
            stakeholders_helped=[names.get(i.stakeholder_id, i.stakeholder_id) for i in imp if i.impact > 0.2],
            stakeholders_harmed=[names.get(i.stakeholder_id, i.stakeholder_id) for i in imp if i.impact < -0.2],
            short_term=("Acts quickly; immediate disruption likely." if f.timeliness > 0.7 and f.causes_harm > 0.4 else
                        "Acts quickly with limited immediate disruption." if f.timeliness > 0.7 else
                        "Little immediate change; the situation persists for now." if f.timeliness < 0.35 else
                        "Measured response; some time passes before effects."),
            long_term=("Builds trust through transparency; outcome less dependent on others' goodwill." if f.honesty > 0.7 and f.prevents_harm > 0.6 else
                       "Preserves options but long-term outcome depends on what is learned or how others respond." if f.reversibility > 0.7 else
                       "Long-term outcome uncertain; risk that underlying problem persists." if f.prevents_harm < 0.4 else
                       "Mixed long-term effects."),
            risks=risks,
            uncertainty=f"Weighted score {w.score:.2f} ± {w.uncertainty:.2f} (model-estimated confidence {w.confidence:.0%}).",
            framework_disagreement=(f"Dimension scores range {min(row.values()):.1f}–{max(row.values()):.1f} "
                                    f"(spread {spread:.1f}): " + ("frameworks disagree substantially." if spread >= 3 else
                                                                  "moderate disagreement." if spread >= 1.5 else "frameworks broadly agree.")),
            dharma_view=dv,
            best_dimensions=[DIMENSION_LABELS[x] for x in ordered[:2]],
            worst_dimensions=[DIMENSION_LABELS[x] for x in ordered[-2:]],
        ))
    return out
