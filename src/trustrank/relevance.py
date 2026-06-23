from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from . import lexicon as lex
from .jd import JobSpec
from .schema import TODAY, Candidate

_FAMILY_LABEL = {
    "A_ranking_recsys": "A · ranking/recsys/retrieval",
    "B_applied_ml": "B · applied ML at product",
    "CV_ML": "CV/speech ML (adjacent)",
    "C_light_ml": "C · light/mixed ML",
    "D_data_eng": "D · data engineering",
    "D_generic_swe": "D · generic software",
    "E_non_tech": "E · non-technical",
}


@dataclass
class RelevanceResult:
    score: float                       # final 0-100ish relevance
    family: str                        # best evidence family key
    family_label: str
    base: float
    yoe_factor: float
    cv_penalty: float = 1.0
    services_penalty: float = 1.0
    decoy_penalty: float = 1.0
    availability: float = 1.0
    evidence: list[str] = field(default_factory=list)   # matched phrases
    flags: list[str] = field(default_factory=list)      # human-readable notes


def _classify_role(desc: str) -> tuple[str, list[str]]:
    if (h := lex._hits(desc, lex.TIER_A_RANKING_RECSYS)):
        return "A_ranking_recsys", h
    if (h := lex._hits(desc, lex.TIER_B_APPLIED_ML)):
        return "B_applied_ml", h
    if (h := lex._hits(desc, lex.CV_SPEECH_ROBOTICS)):
        return "CV_ML", h
    if (h := lex._hits(desc, lex.TIER_C_LIGHT_ML)):
        return "C_light_ml", h
    if (h := lex._hits(desc, lex.TIER_D_DATA_ENG)):
        return "D_data_eng", h
    if (h := lex._hits(desc, lex.TIER_D_GENERIC_SWE)):
        return "D_generic_swe", h
    return "E_non_tech", []


def _base_for(family: str, jd: JobSpec) -> float:
    if family == "CV_ML":
        return jd.base_scores["B_applied_ml"]   # ML work, but penalised below
    return jd.base_scores.get(family, jd.base_scores["E_non_tech"])


def _yoe_factor(yoe: float, jd: JobSpec) -> float:
    if jd.yoe_ideal_low <= yoe <= jd.yoe_ideal_high:
        return 1.0
    if jd.yoe_ok_low <= yoe <= jd.yoe_ok_high:
        return 0.92
    if yoe < jd.yoe_ok_low:                      # too junior - steep
        return max(0.30, 0.92 * (yoe / jd.yoe_ok_low))
    return max(0.70, 0.92 - 0.03 * (yoe - jd.yoe_ok_high))  # over-experienced


def _availability(signals: dict, jd: JobSpec) -> tuple[float, list[str]]:
    flags: list[str] = []
    comps: list[tuple[float, float]] = []

    la = signals.get("last_active_date")
    try:
        d = date.fromisoformat(str(la))
        months = (TODAY.year - d.year) * 12 + (TODAY.month - d.month)
        rec = max(0.0, min(1.0, 1.0 - months / 9.0))
        comps.append((rec, 0.35))
        if months >= 6:
            flags.append(f"inactive ~{months}mo")
    except (TypeError, ValueError):
        pass

    rr = signals.get("recruiter_response_rate")
    if isinstance(rr, (int, float)) and rr >= 0:
        comps.append((max(0.0, min(1.0, rr)), 0.30))
        if rr < 0.15:
            flags.append(f"low recruiter response ({rr:.0%})")

    otw = signals.get("open_to_work_flag")
    if isinstance(otw, bool):
        comps.append((1.0 if otw else 0.4, 0.20))

    ic = signals.get("interview_completion_rate")
    if isinstance(ic, (int, float)) and ic >= 0:
        comps.append((max(0.0, min(1.0, ic)), 0.15))

    if not comps:
        raw = 0.7
    else:
        raw = sum(v * w for v, w in comps) / sum(w for _, w in comps)
    mult = jd.availability_min + (jd.availability_max - jd.availability_min) * raw
    return mult, flags


def score(c: Candidate, jd: JobSpec) -> RelevanceResult:
    # 1. strongest evidence anywhere in the career
    best_family, best_phrases = "E_non_tech", []
    best_base = _base_for("E_non_tech", jd)
    for r in c.roles:
        fam, phrases = _classify_role(r.description.lower())
        b = _base_for(fam, jd)
        if b > best_base:
            best_family, best_phrases, best_base = fam, phrases, b

    res = RelevanceResult(
        score=0.0,
        family=best_family,
        family_label=_FAMILY_LABEL[best_family],
        base=best_base,
        yoe_factor=_yoe_factor(c.years_experience, jd),
        evidence=best_phrases,
    )

    alltext = c.all_description_text() + " " + c.summary.lower()

    # 2. CV/speech without NLP-IR rescue
    cv_present = bool(lex._hits(alltext, lex.CV_SPEECH_ROBOTICS))
    nlp_rescue = bool(lex._hits(alltext, lex.NLP_IR_RESCUE))
    if cv_present and not nlp_rescue:
        res.cv_penalty = jd.cv_speech_penalty
        res.flags.append("CV/speech focus, limited NLP/IR")

    # 3. entire career at services firms
    comps = [r.company.lower() for r in c.roles if r.company]
    if comps and all(any(s in cmp for s in lex.SERVICES_COMPANIES) for cmp in comps):
        res.services_penalty = jd.services_penalty
        res.flags.append("career entirely at services firms")

    # 4. "AI-curious, no professional ML" persona — only when there is no real
    if best_family not in ("A_ranking_recsys", "B_applied_ml"):
        if any(sig in c.summary.lower() for sig in lex.DECOY_SUMMARY_SIGNATURES):
            res.decoy_penalty = jd.decoy_summary_penalty
            res.flags.append("AI-curious summary but no professional ML evidence")

    # 5. availability
    res.availability, avail_flags = _availability(c.signals, jd)
    res.flags.extend(avail_flags)

    res.score = (
        res.base
        * res.yoe_factor
        * res.cv_penalty
        * res.services_penalty
        * res.decoy_penalty
        * res.availability
    )
    return res
