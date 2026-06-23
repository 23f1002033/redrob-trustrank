import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from trustrank import honeypot                      
from trustrank.jd import REDROB_SENIOR_AI_ENGINEER as JD   
from trustrank.relevance import score               
from trustrank.schema import Candidate              
from tests.fixtures import FIXTURES                 


def load(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main():
    raws = list(FIXTURES)
    if len(sys.argv) > 1:
        raws += load(sys.argv[1])

    rows = []
    for raw in raws:
        c = Candidate.from_raw(raw)
        is_hp, hp_reasons = honeypot.detect(c)
        r = score(c, JD)
        rows.append((c, r, is_hp, hp_reasons))

    # honeypots excluded from ranking, listed separately
    ranked = sorted(
        [x for x in rows if not x[2]],
        key=lambda x: (-x[1].score, x[0].candidate_id),
    )
    honeypots = [x for x in rows if x[2]]

    print(f"\n{'='*92}\nRANKED  ({len(ranked)} candidates, honeypots removed)\n{'='*92}")
    print(f"{'#':>2}  {'candidate_id':<14} {'score':>6}  {'family':<26} {'yoe':>4}  flags")
    for i, (c, r, _, _) in enumerate(ranked, 1):
        flags = "; ".join(r.flags) if r.flags else "-"
        print(f"{i:>2}  {c.candidate_id:<14} {r.score:6.1f}  {r.family_label:<26} "
              f"{c.years_experience:>4.1f}  {flags[:46]}")

    print(f"\n{'='*92}\nHONEYPOTS EXCLUDED ({len(honeypots)})\n{'='*92}")
    for c, r, _, reasons in honeypots:
        print(f"  {c.candidate_id}: {reasons[0] if reasons else ''}")

    # show evidence for the top 3
    print(f"\n{'='*92}\nTOP-3 EVIDENCE (what the score is actually reading)\n{'='*92}")
    for c, r, _, _ in ranked[:3]:
        cur = c.current_role()
        print(f"\n  {c.candidate_id}  [{r.family_label}]  score={r.score:.1f}")
        print(f"    base={r.base:.0f} × yoe={r.yoe_factor:.2f} × cv={r.cv_penalty:.2f} "
              f"× svc={r.services_penalty:.2f} × decoy={r.decoy_penalty:.2f} "
              f"× avail={r.availability:.2f}")
        print(f"    matched evidence: {r.evidence or '—'}")
        if cur:
            print(f"    current role desc: {cur.description[:110]}...")


if __name__ == "__main__":
    main()
