"""Generate grounded, per-candidate reasoning for the submission."""
from __future__ import annotations

from .ranker import Ranked

_FAMILY_JD = {
    "A · ranking/recsys/retrieval": [
        "maps straight onto the JD's mandate to own ranking and retrieval",
        "is exactly the ranking/recsys ownership the role is built around",
        "hits the core ask: ranking, retrieval and matching systems",
    ],
    "B · applied ML at product": [
        "is applied ML shipped at a product company, the JD's central ask",
        "shows production ML at a product, which the JD weights heavily",
    ],
    "CV/speech ML (adjacent)": ["is real ML depth, but in CV/speech the JD treats as adjacent"],
    "C · light/mixed ML": ["is partial ML exposure, short of the JD's applied-ML bar"],
    "D · data engineering": ["is data-engineering work adjacent to the JD's ranking focus"],
    "D · generic software": ["is solid software work but thin on ML evidence for this role"],
    "E · non-technical": ["shows no ML evidence for this AI-engineering role"],
}


def _pick(options, cid):
    return options[sum(ord(ch) for ch in cid) % len(options)]


def _yoe_clause(yoe):
    if 6 <= yoe <= 8:
        return f"{yoe:.0f}y experience, squarely in the JD's 6–8y band"
    if 5 <= yoe <= 9:
        return f"{yoe:.0f}y experience, inside the 5–9y range"
    if yoe < 5:
        return f"only {yoe:.0f}y, below the JD's 6–8y band"
    return f"{yoe:.0f}y, a touch above the JD's 6–8y band"


def _concern(c):
    if c.flags:
        return c.flags[0]
    if isinstance(c.notice_days, (int, float)) and c.notice_days >= 60:
        return f"{int(c.notice_days)}-day notice period"
    if isinstance(c.response_rate, (int, float)) and 0 <= c.response_rate < 0.3:
        return f"low recruiter response ({c.response_rate:.0%})"
    return None


def _positive(c):
    bits = []
    if c.open_to_work is True:
        bits.append("open to work")
    if isinstance(c.notice_days, (int, float)) and c.notice_days <= 30:
        bits.append(f"{int(c.notice_days)}-day notice")
    if isinstance(c.response_rate, (int, float)) and c.response_rate >= 0.5:
        bits.append(f"responsive ({c.response_rate:.0%})")
    return ", ".join(bits) if bits else None


def reason_for(c: Ranked) -> str:
    jd_link = _pick(_FAMILY_JD.get(c.family_label, ["relevant background"]), c.candidate_id)
    title = c.current_title or "Candidate"
    if c.snippet:
        lead = f"{title}: \"{c.snippet}\" — {jd_link}."
    elif c.evidence:
        lead = f"{title} with {', '.join(c.evidence[:2])} experience — {jd_link}."
    else:
        lead = f"{title} — {jd_link}."

    tail = _yoe_clause(c.years_experience)
    tail = tail[0].upper() + tail[1:]

    # surface the JD-specific depth that lifted this candidate (top-10 colour)
    if c.depth_hits:
        tail += f"; depth: {', '.join(c.depth_hits[:3])}"

    con = _concern(c)
    pos = _positive(c)
    if con:
        tail += f"; concern: {con}"
    elif pos:
        tail += f"; {pos}"
    return f"{lead} {tail}."[:340].strip()
