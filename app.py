from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from trustrank.honeypot import detect as detect_honeypot   
from trustrank.jd import REDROB_SENIOR_AI_ENGINEER as JD    
from trustrank.reasoning import reason_for                 
from trustrank.ranker import Ranked, _best_role_snippet    
from trustrank.relevance import score as score_relevance   
from trustrank.schema import Candidate                     

st.set_page_config(page_title="TrustRank", page_icon="🎯", layout="wide")


def _parse(text: str) -> list[dict]:
    """Accept either JSONL (one object per line) or a JSON array."""
    text = text.strip()
    if not text:
        return []
    if text[0] == "[":                      # JSON array
        return json.loads(text)
    out = []                                # JSONL
    for line in StringIO(text):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def _rank(raws: list[dict]):
    cards, honeypots = [], []
    for raw in raws:
        c = Candidate.from_raw(raw)
        is_hp, reasons = detect_honeypot(c)
        if is_hp:
            honeypots.append((c.candidate_id, reasons[0] if reasons else ""))
            continue
        r = score_relevance(c, JD)
        sig = c.signals or {}
        cards.append(Ranked(
            candidate_id=c.candidate_id, score=r.score, family_label=r.family_label,
            years_experience=c.years_experience, current_title=c.current_title,
            evidence=r.evidence, flags=r.flags, snippet=_best_role_snippet(c),
            location=c.location, notice_days=sig.get("notice_period_days"),
            response_rate=sig.get("recruiter_response_rate"),
            open_to_work=sig.get("open_to_work_flag"),
        ))
    cards.sort(key=lambda x: (-x.score, x.candidate_id))
    return cards, honeypots


st.title("🎯 TrustRank")
st.caption("Evidence-based candidate ranking — ranks corroborated evidence, not keywords.")

with st.expander("How it works", expanded=False):
    st.markdown(
        "- Reads the **career-history descriptions** (the one truthful block) - "
        "ignores title/skills bait.\n"
        "- Scores against the JD rubric: ranking/recsys ▸ applied-ML ▸ light-ML ▸ "
        "data-eng/SWE ▸ non-tech.\n"
        "- Applies JD penalties (CV-only, pure-services, AI-curious-no-ML) and an "
        "availability multiplier.\n"
        "- Drops **honeypots** (internally-impossible profiles).\n"
        "- Pure-Python, CPU-only, no network."
    )

up = st.file_uploader("Upload candidates (.jsonl or .json, ≤100)", type=["jsonl", "json"])
top_n = st.slider("Show top N", 5, 100, 20)

if up is not None:
    try:
        raws = _parse(up.read().decode("utf-8"))
    except Exception as e:
        st.error(f"Could not parse file: {e}")
        st.stop()

    st.success(f"Loaded {len(raws)} candidates.")
    cards, honeypots = _rank(raws)

    c1, c2, c3 = st.columns(3)
    c1.metric("Scored & ranked", len(cards))
    c2.metric("Honeypots excluded", len(honeypots))
    c3.metric("Top family", cards[0].family_label.split("·")[0].strip() if cards else "-")

    st.subheader(f"Top {min(top_n, len(cards))}")
    st.dataframe(
        [{"rank": i + 1, "candidate_id": c.candidate_id,
          "score": round(c.score, 1), "family": c.family_label,
          "yoe": c.years_experience, "reasoning": reason_for(c)}
         for i, c in enumerate(cards[:top_n])],
        use_container_width=True, hide_index=True,
    )

    if honeypots:
        with st.expander(f"🍯 Honeypots excluded ({len(honeypots)})"):
            for cid, why in honeypots:
                st.write(f"**{cid}** - {why}")
else:
    st.info("Upload a sample to see the ranking. Try `data/sample_candidates.json` "
            "or `data/first20.jsonl`.")