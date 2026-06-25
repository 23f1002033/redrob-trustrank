"""TrustRank — sandbox / live demo.

An evidence-ledger view of the ranking system: reviewers upload a sample (or
load the bundled demo) and watch each candidate get judged on corroborated
evidence — green chips for the JD-specific depth that lifted them, amber for
honest concerns. Same code path as rank.py. Designed for samples; the full
100k run is `python rank.py --candidates candidates.jsonl --out submission.csv`.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from io import StringIO
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from trustrank.honeypot import detect as detect_honeypot   # noqa: E402
from trustrank.jd import REDROB_SENIOR_AI_ENGINEER as JD    # noqa: E402
from trustrank.ranker import Ranked, _clean_snippet         # noqa: E402
from trustrank.reasoning import reason_for                  # noqa: E402
from trustrank.relevance import score as score_relevance    # noqa: E402
from trustrank.schema import Candidate                      # noqa: E402

st.set_page_config(page_title="TrustRank", page_icon="🎯", layout="wide")

# ---------------- styling ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, .stDataFrame { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.tr-wordmark { font-family:'Fraunces',serif; font-weight:700; font-size:42px; color:#16243A; letter-spacing:-0.02em; line-height:1; }
.tr-tag { color:#5A6477; font-size:15px; margin-top:2px; }
.tr-eyebrow { font-size:11px; letter-spacing:0.14em; text-transform:uppercase; color:#128A5B; font-weight:600; }
.tr-rule { height:3px; width:54px; background:#128A5B; border-radius:2px; margin:14px 0 4px; }
.tr-chip { display:inline-block; font-size:11.5px; padding:3px 10px; border-radius:20px; margin:3px 5px 0 0; font-weight:500; }
.tr-chip-ev { background:#E3F3EC; color:#0E6A47; }
.tr-chip-warn { background:#FBEEDA; color:#8A5A12; }
.tr-section { font-family:'Fraunces',serif; font-weight:600; font-size:22px; color:#16243A; margin:6px 0 2px; }
</style>
""", unsafe_allow_html=True)


def _parse(text: str) -> list[dict]:
    text = text.strip()
    if not text:
        return []
    if text[0] == "[":
        return json.loads(text)
    return [json.loads(ln) for ln in StringIO(text) if ln.strip()]


def _to_card(c: Candidate) -> Ranked:
    r = score_relevance(c, JD)
    sig = c.signals or {}
    return Ranked(
        candidate_id=c.candidate_id, score=r.score, family_label=r.family_label,
        years_experience=c.years_experience, current_title=c.current_title,
        evidence=r.evidence, flags=r.flags, snippet=_clean_snippet(r.best_role_desc),
        depth_hits=r.depth_hits, location=c.location,
        notice_days=sig.get("notice_period_days"),
        response_rate=sig.get("recruiter_response_rate"),
        open_to_work=sig.get("open_to_work_flag"),
    )


def _rank(raws):
    cards, honeypots = [], []
    for raw in raws:
        c = Candidate.from_raw(raw)
        is_hp, reasons = detect_honeypot(c)
        if is_hp:
            honeypots.append((c.candidate_id, reasons[0] if reasons else ""))
            continue
        cards.append(_to_card(c))
    cards.sort(key=lambda x: (-x.score, x.candidate_id))
    return cards, honeypots


_ACCENT = {"A": "#128A5B", "B": "#2A7D8C", "C": "#6B7488",
           "CV": "#A8742C", "D": "#6B7488", "E": "#B0392C"}


def _accent(label: str) -> str:
    key = label.split("·")[0].strip().split(" ")[0]
    return _ACCENT.get(key, "#6B7488")


def _card_html(rank: int, c: Ranked, score100: float) -> str:
    accent = _accent(c.family_label)
    chips = "".join(
        f"<span class='tr-chip tr-chip-ev'>✓ {h}</span>" for h in c.depth_hits[:4])
    concern = None
    if c.flags:
        concern = c.flags[0]
    elif isinstance(c.notice_days, (int, float)) and c.notice_days >= 60:
        concern = f"{int(c.notice_days)}-day notice"
    if concern:
        chips += f"<span class='tr-chip tr-chip-warn'>▲ {concern}</span>"
    snippet = (c.snippet or "—").replace("<", "&lt;")
    return f"""
<div style="border:1px solid #E7EAF0; border-left:4px solid {accent}; border-radius:12px;
     padding:15px 18px; margin-bottom:11px; background:#fff;">
  <div style="display:flex; justify-content:space-between; align-items:baseline;">
    <div>
      <span style="font-family:Fraunces,serif; font-size:14px; color:#9AA2B2;">#{rank}</span>
      <span style="font-weight:600; color:#16243A; margin-left:8px;">{c.current_title or 'Candidate'}</span>
      <span style="color:#9AA2B2; font-size:12.5px; margin-left:8px;">{c.candidate_id} · {c.years_experience:.0f}y · {c.family_label}</span>
    </div>
    <div style="text-align:right; min-width:70px;">
      <div style="font-family:Fraunces,serif; font-size:26px; color:{accent}; line-height:1;">{score100:.0f}</div>
      <div style="font-size:9.5px; letter-spacing:0.08em; text-transform:uppercase; color:#9AA2B2;">TrustRank</div>
    </div>
  </div>
  <div style="margin:9px 0 8px; padding:9px 12px; background:#F7F8FA; border-radius:8px;
       font-size:13.5px; color:#3A4458; font-style:italic;">"{snippet}"</div>
  <div>{chips}</div>
</div>"""


# ---------------- header ----------------
st.markdown("<div class='tr-eyebrow'>AIM Nexus · Redrob Data & AI Challenge</div>",
            unsafe_allow_html=True)
st.markdown("<div class='tr-wordmark'>TrustRank</div>", unsafe_allow_html=True)
st.markdown("<div class='tr-tag'>Ranks candidates by corroborated evidence — "
            "the work they can prove, not the keywords they list.</div>",
            unsafe_allow_html=True)
st.markdown("<div class='tr-rule'></div>", unsafe_allow_html=True)

with st.expander("How it works"):
    st.markdown(
        "- **Reads the career-history descriptions** — the one block that stays truthful "
        "when titles, skills and degrees are independently-sampled bait.\n"
        "- **Scores against the JD rubric:** ranking/recsys ▸ applied-ML ▸ light-ML ▸ "
        "data-eng/SWE ▸ non-tech, taking the strongest evidence anywhere in the career.\n"
        "- **Rewards JD depth** (green chips): embeddings, vector search, production scale, "
        "evaluation rigor, learning-to-rank — this is what sharpens the top-10.\n"
        "- **Penalises** CV/speech-only, pure-services careers, AI-curious-but-no-ML, and "
        "down-weights inactive candidates.\n"
        "- **Excludes honeypots** — internally-impossible profiles caught by contradiction, "
        "not keywords.\n"
        "- Pure-Python, CPU-only, no network. The full 100k run is `python rank.py`."
    )

# ---------------- input ----------------
if "raws" not in st.session_state:
    st.session_state.raws = None

col_a, col_b = st.columns([3, 1])
with col_a:
    up = st.file_uploader("Upload candidates (.jsonl or .json)", type=["jsonl", "json"],
                          label_visibility="collapsed")
with col_b:
    if st.button("⚡ Load demo dataset", use_container_width=True):
        try:
            import demo_data
            st.session_state.raws = demo_data.DEMO_CANDIDATES
        except Exception as e:
            st.error(f"Demo unavailable: {e}")

if up is not None:
    try:
        st.session_state.raws = _parse(up.read().decode("utf-8"))
    except Exception as e:
        st.error(f"Couldn't read that file — expecting JSONL or a JSON array. ({e})")
        st.session_state.raws = None

raws = st.session_state.raws

if not raws:
    st.info("Upload a candidate sample, or hit **Load demo dataset** to see the "
            "ranking on a curated mix of strong, weak, and honeypot profiles.")
    st.stop()

cards, honeypots = _rank(raws)
if not cards:
    st.warning("Every profile in this sample was flagged as a honeypot.")
    st.stop()

hi = cards[0].score or 1.0
yoes = [c.years_experience for c in cards]

# ---------------- metrics ----------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Scored & ranked", len(cards))
m2.metric("Honeypots excluded", len(honeypots))
m3.metric("Top family", cards[0].family_label.split("·")[0].strip())
m4.metric("Median experience", f"{sorted(yoes)[len(yoes)//2]:.0f}y")

# ---------------- signature: top-3 evidence cards ----------------
st.markdown("<div class='tr-section'>Top shortlist</div>", unsafe_allow_html=True)
st.caption("The strongest matches, with the evidence that earned the score.")
for i, c in enumerate(cards[:3], 1):
    st.markdown(_card_html(i, c, 100 * c.score / hi), unsafe_allow_html=True)

# ---------------- family distribution (custom HTML bars; no Altair dep) ------
fam_counts = Counter(c.family_label for c in cards)
if len(fam_counts) > 1:
    st.markdown("<div class='tr-section'>Evidence-family mix</div>", unsafe_allow_html=True)
    mx = max(fam_counts.values())
    bars = ""
    for label, n in sorted(fam_counts.items(), key=lambda kv: -kv[1]):
        pct = 100 * n / mx
        bars += (
            f"<div style='display:flex; align-items:center; margin:5px 0;'>"
            f"<div style='width:210px; font-size:13px; color:#3A4458;'>{label}</div>"
            f"<div style='flex:1; background:#EEF1F5; border-radius:6px; height:20px;'>"
            f"<div style='width:{pct:.1f}%; background:{_accent(label)}; height:100%; "
            f"border-radius:6px;'></div></div>"
            f"<div style='width:34px; text-align:right; font-weight:600; "
            f"color:#16243A; font-size:13px;'>{n}</div></div>")
    st.markdown(bars, unsafe_allow_html=True)

# ---------------- full ranked table ----------------
st.markdown("<div class='tr-section'>Full ranking</div>", unsafe_allow_html=True)
top_n = st.slider("Rows to show", 5, min(100, len(cards)), min(20, len(cards)))
table = [{"rank": i + 1, "candidate_id": c.candidate_id,
          "score": round(c.score / hi, 3), "family": c.family_label,
          "yoe": c.years_experience, "reasoning": reason_for(c)}
         for i, c in enumerate(cards[:top_n])]
st.dataframe(
    table, use_container_width=True, hide_index=True,
    column_config={
        "score": st.column_config.ProgressColumn(
            "TrustRank", min_value=0.0, max_value=1.0, format="%.2f"),
        "reasoning": st.column_config.TextColumn("reasoning", width="large"),
    },
)

# ---------------- honeypots ----------------
if honeypots:
    with st.expander(f"🍯 Honeypots excluded ({len(honeypots)}) — caught by contradiction"):
        for cid, why in honeypots:
            st.markdown(f"**{cid}** — {why}")

st.markdown(
    "<div style='margin-top:24px; padding-top:12px; border-top:1px solid #E7EAF0; "
    "color:#9AA2B2; font-size:12.5px;'>Pure-Python · CPU-only · no network · "
    "100k candidates in ~15s / ~110MB &nbsp;·&nbsp; "
    "<a href='https://github.com/23f1002033/redrob-trustrank' style='color:#128A5B;'>"
    "GitHub repo</a></div>", unsafe_allow_html=True)