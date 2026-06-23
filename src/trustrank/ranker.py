from __future__ import annotations

import time
from dataclasses import dataclass, field

from .honeypot import detect as detect_honeypot
from .io_jsonl import stream_candidates
from .jd import REDROB_SENIOR_AI_ENGINEER, JobSpec
from .relevance import score as score_relevance


@dataclass
class Ranked:
    candidate_id: str
    score: float
    family_label: str
    years_experience: float
    current_title: str
    evidence: list = field(default_factory=list)
    flags: list = field(default_factory=list)


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
        cards.append(
            Ranked(
                candidate_id=c.candidate_id,
                score=r.score,
                family_label=r.family_label,
                years_experience=c.years_experience,
                current_title=c.current_title,
                evidence=r.evidence,
                flags=r.flags,
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