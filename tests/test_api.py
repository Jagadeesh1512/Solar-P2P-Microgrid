import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_api_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Decentralized Solar Microgrid" in data["system"]

def test_get_state(client):
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "summary" in data
    assert "nodes" in data
    assert "community_battery" in data
    assert "tariff_rates" in data
    assert "house_alpha" in data["nodes"]

def test_get_trades(client):
    response = client.get("/api/trades?limit=10")
    assert response.status_code == 200
    trades = response.json()
    assert isinstance(trades, list)

def test_scenario_switching(client):
    # Valid scenario
    res = client.post("/api/scenario", json={"scenario": "cloudy_afternoon"})
    assert res.status_code == 200
    assert "cloudy_afternoon" in res.json()["message"]

    # Invalid scenario
    res_invalid = client.post("/api/scenario", json={"scenario": "tornado_disaster"})
    assert res_invalid.status_code == 400

def test_speed_update(client):
    res = client.post("/api/speed", json={"multiplier": 10.0})
    assert res.status_code == 200
    assert "10.0x" in res.json()["message"]

def test_blackout_toggle(client):
    res = client.post("/api/blackout?active=true")
    assert res.status_code == 200
    assert "True" in res.json()["message"]

    res_off = client.post("/api/blackout?active=false")
    assert res_off.status_code == 200
    assert "False" in res_off.json()["message"]

def test_relay_control(client):
    # Valid node
    res = client.post("/api/relay", json={"node_id": "house_alpha", "relay_active": False})
    assert res.status_code == 200
    assert res.json()["status"] == "ISLANDED"
    assert res.json()["grid_relay_active"] is False

    # Reconnect
    res_reconnect = client.post("/api/relay", json={"node_id": "house_alpha", "relay_active": True})
    assert res_reconnect.status_code == 200
    assert res_reconnect.json()["status"] == "CONNECTED"

    # Nonexistent node
    res_404 = client.post("/api/relay", json={"node_id": "house_nonexistent", "relay_active": True})
    assert res_404.status_code == 404

def test_mqtt_status(client):
    res = client.get("/api/mqtt/status")
    assert res.status_code == 200
    data = res.json()
    assert "enabled" in data
    assert "broker" in data
