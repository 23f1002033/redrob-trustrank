"""Ranking core: stream -> honeypot filter -> relevance score -> sorted order.

Single pass over candidates.jsonl. Honeypots are dropped (not ranked).
Everyone else gets a relevance score; we sort once, descending, breaking ties
by candidate_id ascending (the submission spec's required deterministic
tie-break). Memory stays modest (~tens of MB for 100k).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .honeypot import detect as detect_honeypot
from .io_jsonl import stream_candidates
from .jd import REDROB_SENIOR_AI_ENGINEER, JobSpec
from .relevance import score as score_relevance


def _clean_snippet(text: str, limit: int = 130) -> str:
    """First sentence of a role description, cleaned for use in reasoning."""
    if not text:
        return ""
    s = text.strip().split(". ")[0].strip()
    return (s[:limit] + "…") if len(s) > limit else s


@dataclass
class Ranked:
    candidate_id: str
    score: float
    family_label: str
    years_experience: float
    current_title: str
    evidence: list = field(default_factory=list)
    flags: list = field(default_factory=list)
    # extra facts for grounded reasoning (no hallucination — read from profile)
    snippet: str = ""              # phrase from the role that EARNED the score
    location: str = ""
    notice_days: float | None = None
    response_rate: float | None = None
    open_to_work: bool | None = None


def rank_candidates(
    path: str,
    jd: JobSpec = REDROB_SENIOR_AI_ENGINEER,
    limit: int | None = None,
) -> tuple[list[Ranked], dict]:
    t0 = time.time()
    cards: list[Ranked] = []
    n = n_hp = 0

    for c in stream_candidates(path, limit=limit):
        n += 1
        is_hp, _ = detect_honeypot(c)
        if is_hp:
            n_hp += 1
            continue
        r = score_relevance(c, jd)
        sig = c.signals or {}
        cards.append(
            Ranked(
                candidate_id=c.candidate_id,
                score=r.score,
                family_label=r.family_label,
                years_experience=c.years_experience,
                current_title=c.current_title,
                evidence=r.evidence,
                flags=r.flags,
                snippet=_clean_snippet(r.best_role_desc),   # role that set the family
                location=c.location,
                notice_days=sig.get("notice_period_days"),
                response_rate=sig.get("recruiter_response_rate"),
                open_to_work=sig.get("open_to_work_flag"),
            )
        )

    cards.sort(key=lambda x: (-x.score, x.candidate_id))

    stats = {
        "total": n,
        "honeypots_excluded": n_hp,
        "scored": len(cards),
        "seconds": round(time.time() - t0, 2),
    }
    return cards, stats