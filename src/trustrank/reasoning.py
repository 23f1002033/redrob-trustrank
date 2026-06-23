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
    "CV/speech ML (adjacent)": [
        "is real ML depth, but in CV/speech the JD treats as adjacent",
    ],
    "C · light/mixed ML": [
        "is partial ML exposure, short of the JD's applied-ML bar",
    ],
    "D · data engineering": [
        "is data-engineering work adjacent to the JD's ranking focus",
    ],
    "D · generic software": [
        "is solid software work but thin on ML evidence for this role",
    ],
    "E · non-technical": [
        "shows no ML evidence for this AI-engineering role",
    ],
}


def _pick(options: list[str], cid: str) -> str:
    """Deterministic per-candidate choice — stable across runs, varied across rows."""
    h = sum(ord(ch) for ch in cid)
    return options[h % len(options)]


def _yoe_clause(yoe: float) -> str:
    if 6 <= yoe <= 8:
        return f"{yoe:.0f}y experience, squarely in the JD's 6-8y band"
    if 5 <= yoe <= 9:
        return f"{yoe:.0f}y experience, inside the 5-9y range"
    if yoe < 5:
        return f"only {yoe:.0f}y, below the JD's band"
    return f"{yoe:.0f}y, a bit above the JD's stated band"


def _concern(c: Ranked) -> str | None:
    """Surface one honest, concrete concern from real signals/flags."""
    if c.flags:
        return c.flags[0]
    if isinstance(c.notice_days, (int, float)) and c.notice_days >= 60:
        return f"{int(c.notice_days)}-day notice period"
    if isinstance(c.response_rate, (int, float)) and 0 <= c.response_rate < 0.3:
        return f"low recruiter response ({c.response_rate:.0%})"
    return None


def _positive_signal(c: Ranked) -> str | None:
    """A concrete availability positive, when present."""
    bits = []
    if c.open_to_work is True:
        bits.append("open to work")
    if isinstance(c.notice_days, (int, float)) and c.notice_days <= 30:
        bits.append(f"{int(c.notice_days)}-day notice")
    if isinstance(c.response_rate, (int, float)) and c.response_rate >= 0.5:
        bits.append(f"responsive to recruiters ({c.response_rate:.0%})")
    return ", ".join(bits) if bits else None


def reason_for(c: Ranked) -> str:
    """One to two sentences, fully grounded in this candidate's own fields."""
    jd_link = _pick(_FAMILY_JD.get(c.family_label, ["relevant background"]), c.candidate_id)

    # lead: prefer a real description snippet over bare lexicon tokens
    title = c.current_title or "Candidate"
    if c.snippet:
        lead = f"{title}: \"{c.snippet}\" — {jd_link}."
    elif c.evidence:
        lead = f"{title} with {', '.join(c.evidence[:2])} experience — {jd_link}."
    else:
        lead = f"{title} — {jd_link}."

    tail = _yoe_clause(c.years_experience).capitalize()

    pos = _positive_signal(c)
    con = _concern(c)
    if con:
        tail += f"; concern: {con}"
    elif pos:
        tail += f"; {pos}"

    return f"{lead} {tail}."[:320].strip()