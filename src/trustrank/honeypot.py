from __future__ import annotations

from .schema import Candidate

_CAL_SLACK = 6      
_YOE_SLACK = 12    
CURRENT_YEAR = 2026


def detect(c: Candidate) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    yoe_months = c.years_experience * 12 if c.years_experience else None

    for r in c.roles:
        cal = r.calendar_months()
        if r.duration_months and cal and r.duration_months > cal + _CAL_SLACK:
            reasons.append(
                f"role '{r.title}' claims {r.duration_months} months but its "
                f"dates span only ~{cal} months"
            )
        if (
            yoe_months is not None
            and r.duration_months
            and r.duration_months > yoe_months + _YOE_SLACK
        ):
            reasons.append(
                f"role '{r.title}' claims {r.duration_months} months "
                f"(> {c.years_experience}y total experience)"
            )

    expert_zero = [
        s.name
        for s in c.skills
        if s.proficiency in ("expert", "advanced") and s.duration_months == 0
    ]
    if len(expert_zero) >= 3:
        reasons.append(
            f"{len(expert_zero)} skills claimed expert/advanced with 0 months used"
        )

    for e in c.education:
        sy, ey = e.start_year, e.end_year
        if isinstance(sy, (int, float)) and isinstance(ey, (int, float)):
            if sy > ey or ey > CURRENT_YEAR + 4:
                reasons.append(f"education years impossible ({e.degree}: {sy}-{ey})")

    return (len(reasons) > 0, reasons)
