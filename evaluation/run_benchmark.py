"""DharmaNet benchmark runner (Phases 8-9).

Usage (from repo root):
    backend/.venv/Scripts/python evaluation/run_benchmark.py            # Windows
    backend/.venv/bin/python evaluation/run_benchmark.py                # Linux/macOS

Conditions:
  B1 plain_llm            "Analyze this ethical dilemma."             (needs an LLM provider)
  B2 single_framework_llm LLM + consequentialism only                 (needs an LLM provider)
  B3 multi_framework_llm  LLM + multiple frameworks, free text        (needs an LLM provider)
  B4 dharmanet_no_dharma  structured pipeline without the Dharma layer
  B5 dharmanet_full       full structured pipeline

Without an LLM provider configured, B1-B3 are reported as NOT YET EVALUATED and B4/B5 run on the
offline heuristic engine. Nothing in the report is estimated or invented: every number comes from
this run, and human-study metrics are always NOT YET EVALUATED until a study is conducted.

Writes evaluation/results.json, evaluation/results.csv, evaluation/report.md.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.core.versions import version_record  # noqa: E402
from app.llm.base import make_provider  # noqa: E402
from app.rag.knowledge import load_kb  # noqa: E402
from app.schemas.dilemma import DilemmaContext  # noqa: E402
from app.services.evaluation.metrics import consistency, structured_metrics, text_metrics  # noqa: E402
from app.services.llm_backend import free_text_baseline  # noqa: E402
from app.services.pipeline import AnalysisPipeline  # noqa: E402

NYE = "NOT YET EVALUATED"
OUT = ROOT / "evaluation"
LLM_CONDITIONS = {"plain_llm": "baseline_plain", "single_framework_llm": "baseline_single_framework",
                  "multi_framework_llm": "baseline_multi_framework"}
METRICS = ["stakeholder_coverage", "conflict_coverage", "dimension_coverage", "explanation_completeness"]

IRRELEVANT = [
    ("name_alex", "My name is Alex. "), ("name_priya", "My name is Priya. "),
    ("name_kwame", "My name is Kwame. "), ("name_mei", "My name is Mei. "),
]
NOISE = " It was a rainy Tuesday afternoon when I started thinking about this."
CONTRADICTION = " Later I heard from someone else that the problem might not be real after all."


def mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(statistics.fmean(xs), 3) if xs else None


def main() -> None:
    s = get_settings()
    s.sensitivity_samples = 1000
    kb = load_kb(s.knowledge_path)
    provider = make_provider(s)
    pipe = AnalysisPipeline(s, kb, provider)
    cases = json.loads((OUT / "benchmark" / "dilemmas.json").read_text(encoding="utf-8"))["cases"]
    paraphrases = json.loads((OUT / "benchmark" / "paraphrases.json").read_text(encoding="utf-8"))["paraphrases"]
    engine = pipe.provider_info()
    t0 = time.time()

    rows: list[dict] = []
    robustness: list[dict] = []
    ablation: list[dict] = []
    for case in cases:
        ctx = DilemmaContext(**case.get("context", {}))
        full = pipe.run(case["dilemma"], ctx, include_dharma=True)
        nod = pipe.run(case["dilemma"], ctx, include_dharma=False)
        for cond, r in (("dharmanet_full", full), ("dharmanet_no_dharma", nod)):
            rows.append({"case_id": case["id"], "category": case["category"], "difficulty": case["difficulty"],
                         "condition": cond, "status": "evaluated", **structured_metrics(r, case)})
        ablation.append({"case_id": case["id"], "full_top": structured_metrics(full, case)["top_action_label"],
                         "no_dharma_top": structured_metrics(nod, case)["top_action_label"]})
        for cond, prompt in LLM_CONDITIONS.items():
            if provider is None:
                rows.append({"case_id": case["id"], "category": case["category"], "difficulty": case["difficulty"],
                             "condition": cond, "status": NYE + " (no LLM provider configured)"})
                continue
            try:
                text = free_text_baseline(provider, prompt, case["dilemma"])
                rows.append({"case_id": case["id"], "category": case["category"], "difficulty": case["difficulty"],
                             "condition": cond, "status": "evaluated", **text_metrics(text, case)})
            except Exception as e:  # recorded, never silently dropped
                rows.append({"case_id": case["id"], "category": case["category"], "difficulty": case["difficulty"],
                             "condition": cond, "status": f"error: {type(e).__name__}"})

        # ---- Phase 9 robustness (full DharmaNet) ----
        variants = {
            "irrelevant_name": [pipe.run(p + case["dilemma"], ctx) for _, p in IRRELEVANT],
            "irrelevant_context": [pipe.run(case["dilemma"] + NOISE, ctx)],
            "contradictory_info": [pipe.run(case["dilemma"] + CONTRADICTION, ctx)],
            "missing_info": [pipe.run(case["dilemma"].split(". ")[0] + ".", ctx)],
        }
        if case["id"] in paraphrases:
            variants["paraphrase"] = [pipe.run(paraphrases[case["id"]], ctx)]
        for kind, outs in variants.items():
            robustness.append({"case_id": case["id"], "perturbation": kind, **consistency(full, outs)})

    by_cond: dict[str, dict] = {}
    for cond in ["plain_llm", "single_framework_llm", "multi_framework_llm", "dharmanet_no_dharma", "dharmanet_full"]:
        rs = [r for r in rows if r["condition"] == cond and r["status"] == "evaluated"]
        by_cond[cond] = ({m: mean([r[m] for r in rs]) for m in METRICS} | {"n": len(rs)}) if rs else {"status": NYE}
    full_rows = [r for r in rows if r["condition"] == "dharmanet_full"]
    stab = {lab: sum(1 for r in full_rows if r["stability_label"] == lab) for lab in
            ("Stable", "Moderately Sensitive", "Highly Sensitive")}
    rob: dict[str, dict] = {}
    for kind in ("irrelevant_name", "irrelevant_context", "contradictory_info", "missing_info", "paraphrase"):
        rr = [x for x in robustness if x["perturbation"] == kind]
        rob[kind] = {"n_cases": len(rr), "top_agreement": mean([x["top_agreement"] for x in rr]),
                     "mean_abs_score_diff": mean([x["mean_abs_score_diff"] for x in rr])}
    changed = sum(1 for a in ablation if a["full_top"] != a["no_dharma_top"])

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "runtime_s": round(time.time() - t0, 1),
        "engine": engine.model_dump(), "versions": version_record(kb.version), "n_cases": len(cases),
        "conditions": by_cond, "stability_distribution_full": stab,
        "robustness_full": rob, "model_change_robustness": NYE + " (requires runs with ≥2 LLM providers)",
        "dharma_ablation": {"cases_where_top_action_changes": changed, "n": len(ablation), "detail": ablation},
        "human_evaluation": NYE, "rows": rows, "robustness_rows": robustness,
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    keys = sorted({k for r in rows for k in r})
    with open(OUT / "results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    (OUT / "report.md").write_text(report(results), encoding="utf-8")
    print(f"Wrote results for {len(cases)} cases in {results['runtime_s']}s -> evaluation/report.md")


def fmt(v):
    return "—" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))


def report(R: dict) -> str:
    e = R["engine"]
    L = [
        "# DharmaNet — Evaluation Report",
        "",
        f"Generated {R['generated_at']} · {R['n_cases']} benchmark cases · runtime {R['runtime_s']} s",
        "",
        f"**Engine:** `{e['provider']}` / `{e['model']}` — {e['note']}",
        "",
        "> **Read this first.** These are automatic, structure-level metrics computed against *author-written* "
        "annotations (not expert annotations). They measure coverage and consistency, **not** moral correctness. "
        + ("Because the engine is the offline heuristic engine, high consistency partly reflects its deterministic, "
           "keyword-based design rather than robust understanding. " if not e["is_llm"] else "")
        + "No result here supports a claim of superiority over LLM baselines unless those baselines were actually run.",
        "",
        "## Baseline comparison (mean over cases)",
        "",
        "| Condition | Stakeholder cov. | Conflict cov. | Dimension cov. | Explanation compl. | n |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    names = {"plain_llm": "B1 Plain LLM", "single_framework_llm": "B2 LLM + single framework",
             "multi_framework_llm": "B3 LLM + multiple frameworks", "dharmanet_no_dharma": "B4 DharmaNet w/o Dharma",
             "dharmanet_full": "B5 Full DharmaNet"}
    for k, label in names.items():
        c = R["conditions"][k]
        if "status" in c:
            L.append(f"| {label} | {NYE} | | | | 0 |")
        else:
            L.append(f"| {label} | {fmt(c['stakeholder_coverage'])} | {fmt(c['conflict_coverage'])} | "
                     f"{fmt(c['dimension_coverage'])} | {fmt(c['explanation_completeness'])} | {c['n']} |")
    L += ["", "Dimension coverage is 1.0 by construction for B4/B5 (every framework is always evaluated); it is "
          "informative only for free-text baselines. Free-text baselines are scored with keyword proxies (see docs/evaluation.md).",
          "", "## Recommendation stability (full DharmaNet, default weights)", "",
          "| Stable | Moderately Sensitive | Highly Sensitive |", "|---:|---:|---:|",
          "| {Stable} | {Moderately Sensitive} | {Highly Sensitive} |".format(**R["stability_distribution_full"]),
          "", "## Robustness (full DharmaNet)", "",
          "Top-action agreement compares the leading action *type* between the original and perturbed input; score "
          "difference is the change in that action's weighted score (0-10).", "",
          "| Perturbation | Cases | Top-action agreement | Mean abs. score diff |", "|---|---:|---:|---:|"]
    for k, v in R["robustness_full"].items():
        L.append(f"| {k.replace('_', ' ')} | {v['n_cases']} | {fmt(v['top_agreement'])} | {fmt(v['mean_abs_score_diff'])} |")
    L += ["", "Irrelevant-name and irrelevant-context perturbations *should* not change results; contradictory or "
          "missing information *may* legitimately change them (reported for transparency, not as errors).", "",
          f"Model-change robustness: {R['model_change_robustness']}.", "",
          "## Dharma-layer ablation", "",
          f"Adding the Dharma-inspired dimension changed the top-ranked action in "
          f"{R['dharma_ablation']['cases_where_top_action_changes']} of {R['dharma_ablation']['n']} cases at default weights "
          "(Dharma weight 10%).", "",
          "## Human evaluation", "", f"{NYE}. Protocol: evaluation/user_study/protocol.md.", "",
          "## Versions", "", "```json", json.dumps(R["versions"], indent=2), "```", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
