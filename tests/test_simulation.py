from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def payload():
    return {
        "initial_state": {"energy": 50, "strain": 20, "momentum": 10},
        "paths": {
            "balanced": [
                {"demand": 5, "recovery": 3, "opportunity": 4},
                {"demand": 2, "recovery": 6, "opportunity": 1},
            ],
            "rest": [],
        },
    }


def test_health_and_docs(client):
    assert client.get("/health").json() == {"status": "healthy"}
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_simulation_returns_trajectory_and_independent_paths(client, payload):
    original = deepcopy(payload)
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200
    assert response.json() == {
        "results": {
            "balanced": {
                "trajectory": [
                    {"energy": 50, "strain": 20, "momentum": 10},
                    {"energy": 48, "strain": 22, "momentum": 12},
                    {"energy": 52, "strain": 18, "momentum": 12},
                ],
                "final_state": {"energy": 52, "strain": 18, "momentum": 12},
            },
            "rest": {
                "trajectory": [{"energy": 50, "strain": 20, "momentum": 10}],
                "final_state": {"energy": 50, "strain": 20, "momentum": 10},
            },
        }
    }
    assert payload == original
    assert client.post("/simulate", json=payload).json() == response.json()


@pytest.mark.parametrize(
    "state, step, expected",
    [
        ((0, 100, 0), (10, 0, 0), (0, 100, 0)),
        ((100, 0, 100), (0, 10, 10), (100, 0, 100)),
    ],
)
def test_state_values_are_clamped(client, state, step, expected):
    response = client.post("/simulate", json={
        "initial_state": dict(zip(("energy", "strain", "momentum"), state)),
        "paths": {"boundary": [dict(zip(("demand", "recovery", "opportunity"), step))]},
    })
    assert response.status_code == 200
    assert response.json()["results"]["boundary"]["final_state"] == dict(
        zip(("energy", "strain", "momentum"), expected)
    )


@pytest.mark.parametrize("field", ["energy", "strain", "momentum"])
@pytest.mark.parametrize("value", [-1, 101])
def test_rejects_out_of_range_states(client, payload, field, value):
    payload["initial_state"][field] = value
    assert client.post("/simulate", json=payload).status_code == 422


@pytest.mark.parametrize("field", ["demand", "recovery", "opportunity"])
@pytest.mark.parametrize("value", [-1, 11])
def test_rejects_out_of_range_environment(client, payload, field, value):
    payload["paths"]["balanced"][0][field] = value
    assert client.post("/simulate", json=payload).status_code == 422


def test_rejects_missing_fields_and_empty_paths(client, payload):
    assert client.post("/simulate", json={}).status_code == 422
    payload["paths"] = {}
    assert client.post("/simulate", json=payload).status_code == 422
