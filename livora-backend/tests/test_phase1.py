"""
Phase 1 API tests. Requires MongoDB running (see MONGODB_URI).

Run from livora-backend:
  pip install -r requirements.txt pytest httpx
  pytest tests/test_phase1.py -v
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
    return f"test_{uuid.uuid4().hex[:12]}@livora.test"


@pytest.fixture(scope="module", autouse=True)
def require_mongo():
    try:
        r = client.get("/")
        assert r.status_code == 200
    except Exception as exc:
        pytest.skip(f"API not available: {exc}")


def test_signup_only_creates_user_then_donor_profile_via_put():
    email = _unique_email()
    password = "testpass123"

    signup = client.post(
        "/api/auth/signup",
        json={
            "fullName": "Test Donor",
            "email": email,
            "password": password,
            "role": "donor",
        },
    )
    assert signup.status_code == 200, signup.text
    token = signup.json()["access_token"]
    user_id = signup.json()["userId"]
    assert signup.json()["role"] == "donor"
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["userId"] == user_id

    # GET creates empty donor profile
    donor = client.get("/api/donors/me", headers=headers)
    assert donor.status_code == 200
    assert donor.json()["bloodGroup"] is None

    updated = client.put(
        "/api/donors/me",
        headers=headers,
        json={
            "bloodGroup": "O+",
            "organs": ["kidney"],
            "phone": "555-0100",
            "address": "Delhi, India",
            "age": 28,
            "gender": "female",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["bloodGroup"] == "O+"
    assert updated.json()["status"] == "pending"
    assert "kidney" in updated.json()["organs"]
    assert updated.json()["age"] == 28
    assert updated.json()["profileCompletion"] > 0

    rejected = client.put(
        "/api/donors/me",
        headers=headers,
        json={"status": "active"},
    )
    assert rejected.status_code == 422

    logout = client.post("/api/auth/logout", headers=headers)
    assert logout.status_code == 200

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_signup_rejects_profile_fields():
    email = _unique_email()
    signup = client.post(
        "/api/auth/signup",
        json={
            "fullName": "Test",
            "email": email,
            "password": "testpass123",
            "role": "donor",
            "bloodGroup": "O+",
        },
    )
    assert signup.status_code == 422


def test_recipient_profile_via_put():
    email = _unique_email()
    signup = client.post(
        "/api/auth/signup",
        json={
            "fullName": "Test Recipient",
            "email": email,
            "password": "testpass123",
            "role": "recipient",
        },
    )
    assert signup.status_code == 200
    headers = {"Authorization": f"Bearer {signup.json()['access_token']}"}

    profile = client.put(
        "/api/recipients/me",
        headers=headers,
        json={
            "organNeeded": "kidney",
            "bloodGroup": "A+",
            "medicalHistory": "Waiting list",
            "address": "Mumbai",
        },
    )
    assert profile.status_code == 200
    assert profile.json()["organNeeded"] == "kidney"
    assert profile.json()["bloodGroup"] == "A+"
    assert profile.json()["status"] == "pending"

    rejected = client.put(
        "/api/recipients/me",
        headers=headers,
        json={"status": "active"},
    )
    assert rejected.status_code == 422


def test_protected_route_rejects_anonymous():
    r = client.get("/api/donors/me")
    assert r.status_code == 401


def test_hospital_can_update_donor_status():
    donor_email = _unique_email()
    donor_signup = client.post(
        "/api/auth/signup",
        json={
            "fullName": "Donor For Status",
            "email": donor_email,
            "password": "testpass123",
            "role": "donor",
        },
    )
    donor_id = donor_signup.json()["userId"]
    client.put(
        "/api/donors/me",
        headers={"Authorization": f"Bearer {donor_signup.json()['access_token']}"},
        json={"bloodGroup": "A+"},
    )

    hospital_email = _unique_email()
    hospital_signup = client.post(
        "/api/auth/signup",
        json={
            "fullName": "City Hospital",
            "email": hospital_email,
            "password": "testpass123",
            "role": "hospital",
        },
    )
    hospital_headers = {
        "Authorization": f"Bearer {hospital_signup.json()['access_token']}"
    }

    patched = client.patch(
        f"/api/donors/{donor_id}/status",
        headers=hospital_headers,
        json={"status": "verified"},
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "verified"

    donor_cannot = client.patch(
        f"/api/donors/{donor_id}/status",
        headers={"Authorization": f"Bearer {donor_signup.json()['access_token']}"},
        json={"status": "active"},
    )
    assert donor_cannot.status_code == 403


def test_role_mismatch_on_donor_route():
    email = _unique_email()
    signup = client.post(
        "/api/auth/signup",
        json={
            "fullName": "Hospital User",
            "email": email,
            "password": "testpass123",
            "role": "hospital",
        },
    )
    assert signup.status_code == 200
    headers = {"Authorization": f"Bearer {signup.json()['access_token']}"}
    r = client.get("/api/donors/me", headers=headers)
    assert r.status_code == 403
