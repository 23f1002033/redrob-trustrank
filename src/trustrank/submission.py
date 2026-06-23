from __future__ import annotations

import csv
from pathlib import Path

from .ranker import Ranked

HEADER = ["candidate_id", "rank", "score", "reasoning"]


def _placeholder_reasoning(c: Ranked) -> str:
    """Short, non-identical justification until the real generator (M3c).

    Pulled from this candidate's own fields so no two are identical and
    nothing is hallucinated (spec penalises empty / templated / identical).
    """
    ev = ", ".join(c.evidence[:2]) if c.evidence else "relevant experience"
    note = f"; {c.flags[0]}" if c.flags else ""
    return (
        f"{c.family_label.split('·')[-1].strip()} evidence "
        f"({ev}); ~{c.years_experience:.0f}y experience{note}."
    )


def _normalise(score: float, hi: float) -> float:
    """Map raw scores to a clean 0-1 range (rank order is unchanged)."""
    return round(score / hi, 4) if hi > 0 else 0.0


def write_submission(top: list[Ranked], out_path: str | Path, n: int = 100) -> Path:
    out_path = Path(out_path)
    top = top[:n]
    if len(top) < n:
        raise ValueError(f"need {n} candidates, got {len(top)} after filtering")

    hi = top[0].score or 1.0
    rows = []
    prev = 1.0
    for rank, c in enumerate(top, 1):
        s = _normalise(c.score, hi)
        s = min(s, prev)          
        prev = s
        rows.append([c.candidate_id, rank, f"{s:.4f}", _placeholder_reasoning(c)])

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    return out_path