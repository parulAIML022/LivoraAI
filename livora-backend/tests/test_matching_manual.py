"""Unit tests for manual matching_service (no MongoDB)."""

from services.matching_service import _donor_matches_recipient


def test_manual_match_same_blood_and_organ():
    donor = {
        "status": "verified",
        "bloodGroup": "O+",
        "organs": ["kidney"],
    }
    recipient = {
        "bloodGroup": "O+",
        "organNeeded": "kidney",
    }
    assert _donor_matches_recipient(donor, recipient) == "kidney"


def test_manual_match_rejects_pending_donor():
    donor = {
        "status": "pending",
        "bloodGroup": "O+",
        "organs": ["kidney"],
    }
    recipient = {"bloodGroup": "O+", "organNeeded": "kidney"}
    assert _donor_matches_recipient(donor, recipient) is None


def test_manual_match_rejects_blood_mismatch():
    donor = {
        "status": "verified",
        "bloodGroup": "A+",
        "organs": ["kidney"],
    }
    recipient = {"bloodGroup": "O+", "organNeeded": "kidney"}
    assert _donor_matches_recipient(donor, recipient) is None


def test_manual_match_case_insensitive():
    donor = {
        "status": "Verified",
        "bloodGroup": "B+",
        "organs": ["Heart"],
    }
    recipient = {"bloodGroup": "b+", "organNeeded": "heart"}
    assert _donor_matches_recipient(donor, recipient) == "heart"
