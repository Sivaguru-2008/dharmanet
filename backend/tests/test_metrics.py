from app.services.evaluation.metrics import consistency, structured_metrics, text_metrics
from tests.conftest import BENCHMARK, WHISTLE

CASE = next(c for c in BENCHMARK if c["id"] == "wp-1")


def test_structured_metrics(pipeline):
    m = structured_metrics(pipeline.run(WHISTLE), CASE)
    assert m["stakeholder_coverage"] == 1.0
    assert m["explanation_completeness"] == 1.0 and m["has_uncertainty"]
    assert 0 <= m["conflict_coverage"] <= 1 and m["n_actions"] == 7


def test_text_metrics_keyword_proxy():
    t = ("Because employees could lose their jobs, you should weigh the duty to customers' safety against loyalty to "
         "the company. However, this depends on assumptions about the harm.")
    m = text_metrics(t, CASE)
    assert m["stakeholder_coverage"] == 1.0
    assert m["explanation_completeness"] > 0.5
    assert text_metrics("Do it.", CASE)["stakeholder_coverage"] == 0.0


def test_consistency_identical_runs(pipeline):
    r = pipeline.run(WHISTLE)
    c = consistency(r, [pipeline.run(WHISTLE)])
    assert c["top_agreement"] == 1.0 and c["mean_abs_score_diff"] == 0.0
