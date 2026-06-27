# TrustRank

**Ranking candidates by corroborated evidence, not keywords.**

TrustRank is an evidence-based candidate ranking system built for the
**Data & AI Challenge: Intelligent Candidate Discovery** (India.RUNS, Redrob x
Hack2skill). It ranks 100,000 candidate profiles against a Senior AI Engineer
job description by reading the one part of each profile that stays truthful, then
proving fit before trusting it.

- **Live demo:** https://redrob-trustrank-aim-nexus.streamlit.app
- **Team:** AIM Nexus (Ishank Gupta, Muskan Jadon)

---

## The problem

The dataset is adversarial by design. For each profile, the **title, skills, and
degree are independently sampled** from the actual work history, so they
routinely contradict it: a profile titled "Content Writer" whose real career is
warehouse operations and brand design, listing Kubernetes and Terraform as
skills. Keyword and naive semantic search reward whichever profile *says* the
right words, which floats these decoys, and ~80 internally-impossible
"honeypot" profiles, straight to the top. Landing too many honeypots in the
shortlist is an automatic disqualification.

## The approach

TrustRank ranks **proof of work**, not claims:

1. **Read the truthful block.** Only the career-history *descriptions* are used
   for evidence; title / skills / degree are treated as unreliable.
2. **Corroborate against the JD.** A claim only counts when the description shows
   the work, in the right JD context. Curated phrase-banks classify the strongest
   evidence into a JD family: `ranking/recsys > applied-ML > light-ML >
   data-eng/SWE > non-tech`.
3. **Score and adjust.**
   `score = family_base x years_fit x JD_penalties x depth_bonus x recency x availability`
   where penalties down-weight the JD's explicit rejects (CV/speech-only,
   pure-services careers, "AI-curious" with no professional ML, title-chasers).
4. **Exclude honeypots** by contradiction (e.g. a role tagged 166 months that
   began only 33 months ago), before ranking.
5. **Rank, cut to top-100, and explain** every row with a grounded reason built
   only from that candidate's own fields.

### Why rules-first, not embeddings

We tested an embedding / semantic-search baseline. On this data it ranks the
keyword-stuffed decoys and honeypots near the top, which is exactly the failure
the challenge penalises. A rules-plus-evidence design is a **deliberate choice**
here: it gives zero hallucination, full explainability, and honeypot safety by
logical contradiction, and it fits the hard limits (CPU-only, no network, well
under 5 min and 16 GB).

---

## Quick start

Requires **Python 3.10+**. The ranker uses only the standard library.

```bash
git clone https://github.com/23f1002033/redrob-trustrank
cd redrob-trustrank

# place the challenge dataset at data/candidates.jsonl
# (gitignored: ~480 MB, not committed)

# rank -> writes the submission CSV
python rank.py --candidates data/candidates.jsonl --out submission.csv

# validate the CSV against the official rules
python docs/validate_submission.py submission.csv
```

`rank.py` prints run stats, the top-100 family mix, a honeypot audit, and the
top-20 preview, then writes `submission.csv`.

### Run the demo locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload a sample or click **Load demo dataset** to see the ranking on a curated
mix of strong, weak, and honeypot profiles.

---

## Results

| Metric | Value |
|---|---|
| Candidates ranked | 100,000 -> top-100 |
| Runtime | ~15-22 s (budget: 5 min) |
| Peak memory | ~110 MB (budget: 16 GB) |
| Honeypots detected / in top-100 | 41 / **0** |
| Top-100 family | 100% ranking/recsys (target family) |
| Validator | Passes (format, ordering, tie-break) |

After depth scoring, the top-10 are deep ranking engineers showing the JD's
stack: embeddings, vector search, production scale, and NDCG / A-B evaluation.
The scoring metric weights `NDCG@10` at 0.50, so the top-10 order is roughly half
the score, and depth scoring is tuned to sharpen exactly that.

---

## Project structure

```
redrob-trustrank/
  rank.py                  # single-command entry point
  app.py                   # Streamlit sandbox / demo
  demo_data.py             # curated demo dataset for the app
  src/trustrank/
    schema.py              # dataclasses + date helpers
    io_jsonl.py            # streaming JSONL reader (single pass, low memory)
    honeypot.py            # contradiction-based honeypot detection
    lexicon.py             # evidence phrase-banks + depth signals
    jd.py                  # the JD encoded as a scoring rubric
    relevance.py           # evidence -> family -> score
    ranker.py              # ranking + stats
    reasoning.py           # grounded, non-hallucinating explanations
    submission.py          # exact submission CSV writer
  tests/                   # pytest unit tests
  docs/validate_submission.py
  requirements.txt
  submission_metadata.yaml
```

## How it stays honest

- **Explainable:** every ranked candidate ships a reasoning line built only from
  its own fields, naming the role that earned the score and any concern.
- **No hallucination:** reasons are templated from real data, never generated
  free-form.
- **Honeypot-safe:** impossible profiles are caught by internal contradiction,
  not text, and excluded before ranking.
- **Tested:** `pytest` covers honeypot detection, relevance scoring, and the
  submission format.

## Tech stack

Python 3 standard library (ranking), Streamlit (demo), pytest (tests), Git /
GitHub. No ML or embedding libraries by design.

**AI tools declared:** Claude (pair-programming and design support).

---

## Team

**AIM Nexus** - Ishank Gupta (team lead), Muskan Jadon.