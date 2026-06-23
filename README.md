# TrustRank — Redrob Intelligent Candidate Discovery & Ranking

Ranks candidates for a job description by **corroborated evidence, not keyword
overlap**. Built for the INDIA RUNS "Data & AI Challenge" (Track 1).

## The core idea

This dataset is *block-composed*: a profile's title, headline, summary, skills
and education are sampled largely independently, so they routinely contradict
each other (a "Content Writer" whose role descriptions are warehouse-ops,
brand-design, and marketing). The one block that stays truthful for a genuine
candidate is the **career-history description**. TrustRank reads evidence from
there and ignores the bait.

The released JD (Senior AI Engineer) is effectively the scoring rubric: it
states what it wants (ranking / retrieval / recommendation systems shipped at a
product company) and what it explicitly does **not** want (CV/speech-only,
pure-services careers, "AI-curious but no professional ML", title-chasers). We
encode that rubric directly.

## Pipeline

1. **Honeypot filter** (`honeypot.py`) — drop internally-impossible profiles
   (e.g. a role tagged 166 months that started 33 months ago). Caught by
   contradiction, not keywords — so we don't trip the ">10% honeypots = DQ" rule.
2. **Evidence relevance** (`relevance.py`, `lexicon.py`) — classify each role
   description into a JD-aligned family (ranking/recsys ▸ applied-ML ▸ light-ML
   ▸ data-eng/SWE ▸ non-tech); strongest evidence wins.
3. **JD penalties** — CV/speech-without-NLP, entire-career-at-services,
   AI-curious-no-ML.
4. **Availability multiplier** — recency, recruiter response, open-to-work,
   interview completion. A perfect-on-paper candidate who's been inactive for
   months is down-weighted (the JD asks for this explicitly).

Why not embeddings? On this dataset, naive embeddings rank the keyword-decoys
and honeypots *near the top* (their summaries are full of AI words), which is
exactly the failure mode the organizers penalize. We verified this and chose a
rules-first, fully-explainable design. (Details in the deck.)

## Reproduce

```bash
pip install -r requirements.txt
python rank.py --candidates ./candidates.jsonl --out ./submission.csv   # (added in M3)
```

Pure-Python, CPU-only, no network — the ranking step fits the 5-min / 16 GB
budget.

## Status (milestones)

- [x] M0 scaffold · M1 io + honeypot · M2 JD rubric + relevance scorer
- [ ] M3 full ranker → top-100 CSV  ·  M4 grounded reasoning  ·  M5 validator + sandbox + deck

## Demo

```bash
python demo_piece1.py /path/to/first20.jsonl   # ranks fixtures + a real sample
pytest -q                                       # 7 tests
```
