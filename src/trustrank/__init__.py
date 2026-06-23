"""TrustRank - evidence-based candidate ranking for the Redrob challenge.

The dataset is block-composed: a profile's title, headline, summary, skills,
and education are sampled largely independently, so they routinely contradict
each other. The ONE block that stays truthful for a genuine candidate is the
career-history *description* text. TrustRank reads evidence from there, maps it
to a JD-aligned relevance rubric, penalises the gaps the JD explicitly calls
out, scales by how *available* the candidate actually is, and discards
internally-impossible "honeypot" profiles.

Pure-Python, CPU-only, no network — the ranking step fits the 5-minute budget.
"""

__version__ = "0.1.0"
