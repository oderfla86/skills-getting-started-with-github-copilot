import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic check: known activity exists
    assert "Chess Club" in data


def test_signup_and_duplicate_and_unregister():
    activity = "Chess Club"
    email = "teststudent@example.com"

    # Ensure the test email is not present initially (clean up if necessary)
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json().get(activity, {}).get("participants", [])
    if email in participants:
        # remove first to have a clean state
        del_resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert del_resp.status_code == 200

    # Sign up the user
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant appears
    resp = client.get("/activities")
    participants = resp.json().get(activity, {}).get("participants", [])
    assert email in participants

    # Try signing up again -> should fail with 400
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200

    # Verify removed
    resp = client.get("/activities")
    participants = resp.json().get(activity, {}).get("participants", [])
    assert email not in participants
