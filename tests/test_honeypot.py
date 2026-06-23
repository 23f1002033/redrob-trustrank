"""Honeypot detector tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trustrank import honeypot           
from trustrank.schema import Candidate   
from tests.fixtures import FIXTURES      

BY_ID = {f["candidate_id"]: f for f in FIXTURES}


def test_date_impossible_role_is_honeypot():
    c = Candidate.from_raw(BY_ID["CAND_9000099"])  # 166 months, spans ~33
    is_hp, reasons = honeypot.detect(c)
    assert is_hp
    assert "166 months" in reasons[0]


def test_genuine_profile_is_not_honeypot():
    c = Candidate.from_raw(BY_ID["CAND_9000001"])  # clean bullseye
    is_hp, _ = honeypot.detect(c)
    assert not is_hp


def test_expert_skill_zero_months_flags():
    raw = {
        "candidate_id": "CAND_9000100",
        "profile": {"years_of_experience": 5},
        "career_history": [],
        "skills": [
            {"name": s, "proficiency": "expert", "endorsements": 0, "duration_months": 0}
            for s in ("a", "b", "c", "d")
        ],
        "redrob_signals": {},
    }
    is_hp, reasons = honeypot.detect(Candidate.from_raw(raw))
    assert is_hp
    assert any("0 months" in r for r in reasons)
