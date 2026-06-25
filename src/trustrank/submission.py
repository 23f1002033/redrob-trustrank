"""Write the top-100 ranking to the exact submission CSV format.

The submission spec checks two ordering rules on the *rounded* score in the
CSV: scores must be non-increasing by rank, and ties (equal rounded score)
must break by candidate_id ascending. So we round first, then sort by
(-rounded_score, candidate_id) — guaranteeing both rules hold even when two
different raw scores round to the same 4-decimal value.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .ranker import Ranked
from .reasoning import reason_for

HEADER = ["candidate_id", "rank", "score", "reasoning"]


def _normalise(score: float, hi: float) -> float:
    return round(score / hi, 4) if hi > 0 else 0.0


def write_submission(top: list[Ranked], out_path, n: int = 100) -> Path:
    out_path = Path(out_path)
    top = top[:n]
    if len(top) < n:
        raise ValueError(f"need {n} candidates, got {len(top)}")

    hi = max(c.score for c in top) or 1.0
    scored = [(min(_normalise(c.score, hi), 1.0), c) for c in top]
    # final CSV order: rounded score desc, then candidate_id asc (spec tie-break)
    scored.sort(key=lambda t: (-t[0], t[1].candidate_id))

    rows, prev = [], 1.0
    for rank, (s, c) in enumerate(scored, 1):
        s = min(s, prev)          # non-increasing (defensive; already sorted)
        prev = s
        rows.append([c.candidate_id, rank, f"{s:.4f}", reason_for(c)])

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    return out_path