"""Unit tests for matching_engine normalization (no MongoDB required)."""

import pytest

from utils.matching_engine import (
    blood_compatible,
    collect_donor_organs,
    collect_recipient_organs,
    compute_compatibility_score,
    explain_match_rejection,
    is_matchable_donor_status,
    normalize_blood_group,
    normalize_organ,
    normalize_profile_status,
    organs_overlap,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("B+", "B+"),
        ("b+", "B+"),
        ("B+ve", "B+"),
        ("B +ve", "B+"),
        ("B positive", "B+"),
        ("B POSITIVE", "B+"),
        ("B-", "B-"),
        ("B negative", "B-"),
        ("B-ve", "B-"),
        ("O+", "O+"),
        ("o positive", "O+"),
        ("0+", "O+"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("AB negative", "AB-"),
        ("A Rh+", "A+"),
        ("a rh negative", "A-"),
    ],
)
def test_normalize_blood_group(raw: str, expected: str):
    assert normalize_blood_group(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["unknown", "X+", "", "   "],
)
def test_normalize_blood_group_invalid(raw: str):
    assert normalize_blood_group(raw) is None


@pytest.mark.parametrize(
    "donor,recipient,compatible",
    [
        ("B+", "B+", True),
        ("B+ve", "B positive", True),
        ("O+", "B+", True),
        ("B+", "O+", False),
        ("B+", "AB+", True),
    ],
)
def test_blood_compatible(donor: str, recipient: str, compatible: bool):
    assert blood_compatible(donor, recipient) is compatible


@pytest.mark.parametrize(
    "status,matchable",
    [
        ("verified", True),
        ("Verified", True),
        ("active", True),
        ("approved", True),
        ("pending", False),
        ("inactive", False),
    ],
)
def test_donor_status_matchable(status: str, matchable: bool):
    assert is_matchable_donor_status(status) is matchable


def test_normalize_profile_status_aliases():
    assert normalize_profile_status("Approved") == "verified"
    assert normalize_profile_status("VERIFIED") == "verified"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Heart", "heart"),
        ("KIDNEY", "kidney"),
        ("kidneys", "kidney"),
        ("Lungs", "lung"),
        (" liver ", "liver"),
        ("heart transplant", "heart"),
        ("liver transplant", "liver"),
        ("Kidney Transplant", "kidney"),
    ],
)
def test_normalize_organ(raw: str, expected: str):
    assert normalize_organ(raw) == expected


def test_organs_overlap_case_and_plural():
    assert organs_overlap(["Heart"], ["heart"])
    assert organs_overlap(["kidney"], ["Kidneys"])
    assert organs_overlap(["heart"], ["heart transplant"])
    assert not organs_overlap(["liver"], ["kidney"])


def test_collect_recipient_organs_from_organ_needed_only():
    recipient = {"organs": [], "organNeeded": "Heart"}
    assert collect_recipient_organs(recipient) == ["heart"]


def test_collect_recipient_organ_needed_transplant_phrase():
    recipient = {"organs": [], "organNeeded": "liver transplant"}
    donor = {"organs": ["liver"], "status": "verified", "bloodGroup": "O+"}
    recipient_full = {
        **recipient,
        "status": "active",
        "bloodGroup": "O+",
    }
    assert explain_match_rejection(donor=donor, recipient=recipient_full) is None


def test_compute_compatibility_score_full_match():
    donor = {
        "status": "verified",
        "bloodGroup": "B+ve",
        "organs": ["Heart"],
        "address": "Delhi, India",
    }
    recipient = {
        "status": "active",
        "bloodGroup": "B positive",
        "organNeeded": "heart",
        "organs": [],
        "address": "Delhi",
    }
    score = compute_compatibility_score(donor=donor, recipient=recipient)
    assert score is not None
    assert score >= 70


def test_compute_compatibility_approved_donor_alias():
    donor = {
        "status": "approved",
        "bloodGroup": "O+",
        "organs": ["kidney"],
        "address": "Mumbai",
    }
    recipient = {
        "status": "verified",
        "bloodGroup": "O+",
        "organs": ["kidney"],
        "address": "Mumbai",
    }
    assert compute_compatibility_score(donor=donor, recipient=recipient) is not None


def test_compute_compatibility_rejects_pending_donor():
    donor = {
        "status": "pending",
        "bloodGroup": "O+",
        "organs": ["kidney"],
    }
    recipient = {
        "status": "active",
        "bloodGroup": "O+",
        "organs": ["kidney"],
    }
    assert compute_compatibility_score(donor=donor, recipient=recipient) is None


def test_coerce_comma_separated_organs():
    donor = {"organs": "heart, kidney", "status": "verified", "bloodGroup": "A+"}
    recipient = {
        "organNeeded": "kidney",
        "status": "active",
        "bloodGroup": "A+",
    }
    assert explain_match_rejection(donor=donor, recipient=recipient) is None
