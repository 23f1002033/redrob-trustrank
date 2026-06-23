from __future__ import annotations

import argparse
import resource
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from trustrank.jd import REDROB_SENIOR_AI_ENGINEER as JD   
from trustrank.ranker import rank_candidates               


def _peak_mem_mb() -> float:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss / (1024 * 1024) if sys.platform == "darwin" else rss / 1024


def main() -> None:
    ap = argparse.ArgumentParser(description="TrustRank candidate ranker")
    ap.add_argument("--candidates", required=True, help="path to candidates.jsonl")
    ap.add_argument("--out", default="submission.csv", help="output CSV path")
    ap.add_argument("--top", type=int, default=100, help="how many to shortlist")
    ap.add_argument("--limit", type=int, default=None, help="cap rows read (debug)")
    args = ap.parse_args()

    cards, stats = rank_candidates(args.candidates, JD, limit=args.limit)
    top = cards[: args.top]

    print(f"\n{'='*78}")
    print(f"  TrustRank — {JD.title}")
    print(f"{'='*78}")
    print(f"  candidates read      : {stats['total']:,}")
    print(f"  honeypots excluded   : {stats['honeypots_excluded']:,}")
    print(f"  scored & ranked      : {stats['scored']:,}")
    print(f"  ranking time         : {stats['seconds']}s")
    print(f"  peak memory          : {_peak_mem_mb():.0f} MB")

    fam = Counter(c.family_label for c in top)
    print(f"\n  top-{args.top} evidence-family mix:")
    for f, n in fam.most_common():
        print(f"    {n:3d}  {f}")

    print(f"\n  top 20:")
    print(f"  {'#':>2}  {'candidate_id':<14} {'score':>6}  {'family':<26} {'yoe':>4}")
    for i, c in enumerate(top[:20], 1):
        print(f"  {i:>2}  {c.candidate_id:<14} {c.score:6.1f}  {c.family_label:<26} "
              f"{c.years_experience:>4.1f}")

    print(f"\n  (CSV writing + reasoning column come in the next step)\n")


if __name__ == "__main__":
    main()