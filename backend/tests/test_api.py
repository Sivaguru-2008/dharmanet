import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import WHISTLE


@pytest.fixture
def client(settings):
    return TestClient(create_app(settings))


def test_health_and_meta(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    m = client.get("/api/meta").json()
    assert m["provider"]["provider"] == "heuristic" and len(m["frameworks"]) == 6
    assert "dharma_kb_version" in m["versions"]


def test_full_lifecycle(client):
    r = client.post("/api/analyses", json={"dilemma": WHISTLE, "context": {"role": "engineer"}})
    assert r.status_code == 200, r.text
    a = r.json()
    rid = a["id"]
    assert client.get(f"/api/analyses/{rid}").json()["id"] == rid
    assert client.get("/api/analyses").json()[0]["id"] == rid

    w = {"consequences": 0, "duty": 1, "fairness": 0, "virtue": 0, "care": 0, "stakeholder_impact": 0, "dharma": 0}
    rs = client.post(f"/api/analyses/{rid}/rescore", json={"weights": {"values": w}}).json()
    assert rs["matrix"]["weights"]["duty"] == pytest.approx(1.0)
    assert client.get(f"/api/analyses/{rid}").json()["matrix"]["weights"]["duty"] == pytest.approx(1.0)

    acts = a["structured"]["actions"] + [{"id": "u1", "label": "Talk to a lawyer", "kind": "gather_info"}]
    rv = client.post(f"/api/analyses/{rid}/revise", json={"actions": acts}).json()
    assert rv["parent_id"] == rid and "u1" in rv["matrix"]["actions"]

    d = client.post(f"/api/analyses/{rid}/decision", json={"choice": "alternative", "action_id": "a3", "note": "n"})
    assert d.status_code == 200 and "does not execute" in d.json()["statement"]
    assert client.post(f"/api/analyses/{rid}/decision", json={"choice": "alternative", "action_id": "zz"}).status_code == 422
    assert client.post(f"/api/analyses/{rid}/feedback", json={"useful": True, "ratings": {"transparency": 5}}).status_code == 200
    assert client.post(f"/api/analyses/{rid}/feedback", json={"ratings": {"x": 9}}).status_code == 422

    ex = client.get(f"/api/analyses/{rid}/export").json()
    for key in ("analysis_id", "framework_scores", "dharma_analysis", "weights", "recommendation", "sensitivity",
                "versions", "model", "timestamp", "decision", "feedback"):
        assert key in ex
    assert ex["decision"]["choice"] == "alternative" and len(ex["feedback"]) == 2

    assert client.delete(f"/api/analyses/{rid}").status_code == 200
    assert client.get(f"/api/analyses/{rid}").status_code == 404


def test_input_validation(client):
    assert client.post("/api/analyses", json={"dilemma": "too short"}).status_code == 422
    assert client.post("/api/analyses", json={"dilemma": WHISTLE, "weights": {"values": {"duty": -1}}}).status_code == 422


def test_knowledge_endpoint(client):
    assert len(client.get("/api/knowledge").json()) >= 25
    hits = client.get("/api/knowledge", params={"q": "should I stay silent or speak up to my boss"}).json()
    assert hits and all("citation" in h for h in hits)


def test_auth_token_required_when_configured(settings):
    settings.api_token = "s3cret"
    c = TestClient(create_app(settings))
    assert c.get("/api/health").status_code == 200
    assert c.get("/api/analyses").status_code == 401
    assert c.get("/api/analyses", headers={"Authorization": "Bearer s3cret"}).status_code == 200


def test_rate_limit(settings):
    settings.rate_limit_per_minute = 3
    c = TestClient(create_app(settings))
    codes = [c.get("/api/meta").status_code for _ in range(5)]
    assert codes[:3] == [200, 200, 200] and codes[-1] == 429


def test_text_not_stored_when_disabled(settings):
    settings.store_dilemma_text = False
    c = TestClient(create_app(settings))
    rid = c.post("/api/analyses", json={"dilemma": WHISTLE}).json()["id"]
    assert c.get(f"/api/analyses/{rid}").json()["structured"]["dilemma_text"] == "[not stored]"
