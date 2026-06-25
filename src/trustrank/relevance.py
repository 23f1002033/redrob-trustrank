"""Relevance scoring: evidence -> base tier -> JD penalties -> depth -> recency."""
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
    score: float
    family: str
    family_label: str
    base: float
    yoe_factor: float
    cv_penalty: float = 1.0
    services_penalty: float = 1.0
    decoy_penalty: float = 1.0
    availability: float = 1.0
    depth: float = 0.0
    recency: float = 1.0
    evidence: list[str] = field(default_factory=list)
    depth_hits: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    best_role_desc: str = ""


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
        return jd.base_scores["B_applied_ml"]
    return jd.base_scores.get(family, jd.base_scores["E_non_tech"])


def _yoe_factor(yoe: float, jd: JobSpec) -> float:
    if jd.yoe_ideal_low <= yoe <= jd.yoe_ideal_high:
        return 1.0
    if jd.yoe_ok_low <= yoe <= jd.yoe_ok_high:
        return 0.92
    if yoe < jd.yoe_ok_low:
        return max(0.30, 0.92 * (yoe / jd.yoe_ok_low))
    return max(0.70, 0.92 - 0.03 * (yoe - jd.yoe_ok_high))


def _depth(text: str) -> tuple[float, list[str]]:
    """Fraction of JD depth-signal categories present (0..1), plus their names."""
    hits = [name for name, bank in lex.DEPTH_SIGNALS.items() if lex._hits(text, bank)]
    return len(hits) / len(lex.DEPTH_SIGNALS), hits


def _recency(best_role, jd: JobSpec) -> float:
    if best_role is None or best_role.is_current:
        return 1.0
    try:
        e = date.fromisoformat(str(best_role.end_date))
    except (TypeError, ValueError):
        return 1.0
    years = (TODAY - e).days / 365.0
    if years < 1.5:
        return 1.0
    if years < 3:
        return 0.95
    if years < 6:
        return 0.90
    return jd.recency_floor


def _availability(signals: dict, jd: JobSpec) -> tuple[float, list[str]]:
    flags: list[str] = []
    comps: list[tuple[float, float]] = []
    la = signals.get("last_active_date")
    try:
        d = date.fromisoformat(str(la))
        months = (TODAY.year - d.year) * 12 + (TODAY.month - d.month)
        comps.append((max(0.0, min(1.0, 1.0 - months / 9.0)), 0.35))
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
    raw = 0.7 if not comps else sum(v * w for v, w in comps) / sum(w for _, w in comps)
    return jd.availability_min + (jd.availability_max - jd.availability_min) * raw, flags


def score(c: Candidate, jd: JobSpec) -> RelevanceResult:
    best_family, best_phrases, best_role = "E_non_tech", [], None
    best_base = _base_for("E_non_tech", jd)
    for r in c.roles:
        fam, phrases = _classify_role(r.description.lower())
        b = _base_for(fam, jd)
        if b > best_base:
            best_family, best_phrases, best_base, best_role = fam, phrases, b, r
    best_desc = best_role.description if best_role else (
        c.current_role().description if c.current_role() else "")

    depth, depth_hits = _depth(c.all_description_text())

    res = RelevanceResult(
        score=0.0, family=best_family, family_label=_FAMILY_LABEL[best_family],
        base=best_base, yoe_factor=_yoe_factor(c.years_experience, jd),
        evidence=best_phrases, best_role_desc=best_desc,
        depth=depth, depth_hits=depth_hits, recency=_recency(best_role, jd),
    )

    alltext = c.all_description_text() + " " + c.summary.lower()
    cv_present = bool(lex._hits(alltext, lex.CV_SPEECH_ROBOTICS))
    nlp_rescue = bool(lex._hits(alltext, lex.NLP_IR_RESCUE))
    if cv_present and not nlp_rescue:
        res.cv_penalty = jd.cv_speech_penalty
        res.flags.append("CV/speech focus, limited NLP/IR")

    comps = [r.company.lower() for r in c.roles if r.company]
    if comps and all(any(s in cmp for s in lex.SERVICES_COMPANIES) for cmp in comps):
        res.services_penalty = jd.services_penalty
        res.flags.append("career entirely at services firms")

    if best_family not in ("A_ranking_recsys", "B_applied_ml"):
        if any(sig in c.summary.lower() for sig in lex.DECOY_SUMMARY_SIGNATURES):
            res.decoy_penalty = jd.decoy_summary_penalty
            res.flags.append("AI-curious summary but no professional ML evidence")

    res.availability, avail_flags = _availability(c.signals, jd)
    res.flags.extend(avail_flags)
    if res.recency < 1.0:
        res.flags.append("strongest ML work is not recent")

    res.score = (
        res.base * res.yoe_factor * res.cv_penalty * res.services_penalty
        * res.decoy_penalty * res.availability
        * (1 + jd.depth_weight * res.depth) * res.recency
    )
    return res
