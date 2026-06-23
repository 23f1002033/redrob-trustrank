"""Relevance scorer ordering tests — locks the JD-aligned ordering."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trustrank.jd import REDROB_SENIOR_AI_ENGINEER as JD   
from trustrank.relevance import score                      
from trustrank.schema import Candidate                     
from tests.fixtures import FIXTURES                         

BY_ID = {f["candidate_id"]: f for f in FIXTURES}


def s(cid):
    return score(Candidate.from_raw(BY_ID[cid]), JD).score


def test_ranking_recsys_beats_applied_ml():
    assert s("CAND_9000001") > s("CAND_9000002")


def test_applied_ml_beats_cv_and_data_eng():
    assert s("CAND_9000002") > s("CAND_9000003")   # vs CV
    assert s("CAND_9000002") > s("CAND_9000004")   # vs data-eng


def test_services_penalty_applies():
    # same ranking evidence, but entirely at a services firm -> lower
    assert s("CAND_9000005") < s("CAND_9000001")


def test_cv_is_penalised_relative_to_its_base():
    r = score(Candidate.from_raw(BY_ID["CAND_9000003"]), JD)
    assert r.cv_penalty < 1.0
    assert "CV/speech" in " ".join(r.flags)
