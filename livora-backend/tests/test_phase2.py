"""
Phase 2 API tests. Requires MongoDB (see MONGODB_URI).

Run from livora-backend:
  pytest tests/test_phase2.py -v
"""

import os
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MONGODB_DB_NAME", "livora_test")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-pytest-only")

from main import app  # noqa: E402

client = TestClient(app)


def _unique_email() -> str:
    return f"phase2_{uuid.uuid4().hex[:12]}@example.com"


def _signup(role: str, name: str) -> tuple[str, str]:
    email = _unique_email()
    r = client.post(
        "/api/auth/signup",
        json={
            "fullName": name,
            "email": email,
            "password": "testpass123",
            "role": role,
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    return data["access_token"], data["userId"]


@pytest.fixture(scope="module", autouse=True)
def require_mongo():
    try:
        r = client.get("/")
        assert r.status_code == 200
    except Exception as exc:
        pytest.skip(f"API not available: {exc}")


def test_matching_recipient_and_notifications():
    recipient_token, recipient_id = _signup("recipient", "Phase2 Recipient")
    donor_token, donor_id = _signup("donor", "Phase2 Donor")
    hospital_token, _ = _signup("hospital", "Phase2 Hospital")

    recipient_headers = {"Authorization": f"Bearer {recipient_token}"}
    donor_headers = {"Authorization": f"Bearer {donor_token}"}
    hospital_headers = {"Authorization": f"Bearer {hospital_token}"}

    client.put(
        "/api/recipients/me",
        headers=recipient_headers,
        json={
            "organNeeded": "kidney",
            "bloodGroup": "O+",
            "address": "Delhi, India",
            "age": 45,
        },
    )
    client.put(
        "/api/donors/me",
        headers=donor_headers,
        json={
            "bloodGroup": "O+",
            "organs": ["kidney"],
            "address": "Delhi, India",
            "age": 30,
        },
    )

    client.patch(
        f"/api/donors/{donor_id}/status",
        headers=hospital_headers,
        json={"status": "verified"},
    )
    client.patch(
        f"/api/recipients/{recipient_id}/status",
        headers=hospital_headers,
        json={"status": "active"},
    )

    matches = client.get("/api/matching/recipient", headers=recipient_headers)
    assert matches.status_code == 200, matches.text
    body = matches.json()
    assert "matches" in body
    assert "stats" in body
    assert body["stats"]["totalMatches"] >= 1
    assert len(body["matches"]) >= 1
    match = body["matches"][0]
    assert match["bloodGroup"] == "O+"
    assert match["compatibility"] >= 50
    assert "distance" in match

    me = client.get("/api/matching/me", headers=recipient_headers)
    assert me.status_code == 200

    donor_matches = client.get("/api/matching/donor", headers=donor_headers)
    assert donor_matches.status_code == 200

    stats = client.get("/api/dashboard/stats", headers=recipient_headers)
    assert stats.status_code == 200
    assert stats.json()["totalMatches"] >= 1

    notifs = client.get("/api/notifications", headers=donor_headers)
    assert notifs.status_code == 200
    assert notifs.json()["unreadCount"] >= 1

    unread = client.get("/api/notifications/unread-count", headers=donor_headers)
    assert unread.status_code == 200
    assert unread.json()["count"] >= 1


def test_admin_pending_and_stats():
    admin_token, _ = _signup("admin", "Phase2 Admin")
    donor_token, donor_id = _signup("donor", "Pending Donor")
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_donor = {"Authorization": f"Bearer {donor_token}"}

    client.put(
        "/api/donors/me",
        headers=headers_donor,
        json={"bloodGroup": "A+", "organs": ["liver"]},
    )

    pending = client.get("/api/admin/pending", headers=headers_admin)
    assert pending.status_code == 200
    donor_ids = [d["userId"] for d in pending.json()["donors"]]
    assert donor_id in donor_ids

    stats = client.get("/api/admin/stats", headers=headers_admin)
    assert stats.status_code == 200
    assert stats.json()["totalUsers"] >= 3

    client.patch(
        f"/api/donors/{donor_id}/status",
        headers=headers_admin,
        json={"status": "verified"},
    )

    pending_after = client.get("/api/admin/pending?status=pending", headers=headers_admin)
    assert pending_after.status_code == 200
    assert donor_id not in [d["userId"] for d in pending_after.json()["donors"]]


def test_donor_cannot_self_approve():
    donor_token, donor_id = _signup("donor", "Self Approve Donor")
    headers = {"Authorization": f"Bearer {donor_token}"}
    client.get("/api/donors/me", headers=headers)

    r = client.patch(
        f"/api/donors/{donor_id}/status",
        headers=headers,
        json={"status": "verified"},
    )
    assert r.status_code == 403
