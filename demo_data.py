"""A small, curated demo dataset for the sandbox 'Load demo' button.

Hand-mixed from the real description templates so the live demo shows the whole
story end-to-end: deep ranking engineers rise, generic/decoy profiles sink, and
internally-impossible 'honeypot' profiles are caught and excluded. No real
candidate data — every row is reconstructed from public template patterns.
"""
from __future__ import annotations


def _sig(active="2026-06-10", resp=0.7, otw=True, ic=0.85, notice=45):
    return {"last_active_date": active, "recruiter_response_rate": resp,
            "open_to_work_flag": otw, "interview_completion_rate": ic,
            "github_activity_score": -1, "profile_completeness_score": 82,
            "notice_period_days": notice}


def _c(cid, title, yoe, desc, summary="Applied ML engineer.", loc="Pune, Maharashtra",
       company="Hooli", start="2020-02-01", end=None, months=70, current=True, sig=None):
    return {
        "candidate_id": cid,
        "profile": {"anonymized_name": "—", "headline": title, "summary": summary,
                    "location": loc, "country": "India", "years_of_experience": yoe,
                    "current_title": title, "current_company": company,
                    "current_industry": "Software"},
        "career_history": [{"company": company, "title": title, "start_date": start,
                            "end_date": end, "duration_months": months,
                            "is_current": current, "industry": "Software",
                            "company_size": "201-500", "description": desc}],
        "education": [], "skills": [], "redrob_signals": sig or _sig(),
    }


DECOY = ("Software engineer with {y} years across web, backend, and cloud. I've been keeping "
         "up with AI/ML at a self-learner level — taken some online courses, played with the "
         "OpenAI and Anthropic APIs, built a small RAG side project — but I haven't done it in "
         "a professional capacity yet.")

DEMO_CANDIDATES = [
    # --- deep ranking engineers (should top the list) ---
    _c("CAND_0000101", "Staff ML Engineer", 7.0,
       "Owned the end-to-end ranking pipeline at a recommendations-heavy consumer product: "
       "candidate sourcing → embedding generation (sentence-transformers) → FAISS vector search "
       "→ learning-to-rank with LightGBM. Served 50M+ queries/month, evaluated with NDCG and "
       "online A/B tests.", sig=_sig(resp=0.9, notice=30)),
    _c("CAND_0000102", "Search Engineer", 6.5,
       "Built a RAG-based ranking pipeline serving 30M+ queries per month for a recruiter-facing "
       "search product, with hybrid retrieval (BM25 + dense embeddings) and NDCG/MRR evaluation.",
       sig=_sig(resp=0.82, notice=30)),
    _c("CAND_0000103", "Senior ML Engineer", 8.0,
       "Trained and shipped multiple ranking models for our product's discovery feed using "
       "XGBoost and LightGBM; designed features across content, user-behavior and engagement, "
       "with offline-to-online evaluation.", sig=_sig(resp=0.75, notice=60)),
    _c("CAND_0000104", "Recommendation Systems Engineer", 7.0,
       "Owned the ranking layer for an e-commerce search product, evolving it from a hand-tuned "
       "scoring function to a learning-to-rank model over 9 months, measured by conversion A/B "
       "tests at scale.", sig=_sig(resp=0.6, notice=90)),
    # --- applied ML at product (B) ---
    _c("CAND_0000110", "Data Scientist", 6.8,
       "Customer-facing predictive modeling for an e-commerce platform — churn prediction, "
       "conversion likelihood, lifetime value — using scikit-learn and XGBoost in production.",
       summary="Product data scientist."),
    _c("CAND_0000111", "AI Engineer", 5.5,
       "Built NLP pipelines for sentiment analysis and document classification; moved from "
       "sklearn bag-of-words to fine-tuned transformers for an internal analytics dashboard."),
    # --- CV-only (adjacent, penalised) ---
    _c("CAND_0000120", "AI Specialist", 6.8,
       "Built computer vision models for our product's image moderation feature using PyTorch — "
       "fine-tuned ResNet variants on a labeled dataset of ~200k images.", summary="CV engineer."),
    # --- data engineering (D) ---
    _c("CAND_0000130", "Data Engineer", 6.9,
       "Built and maintained data pipelines on Apache Airflow processing ~500GB of daily "
       "transactional data; Spark (PySpark) and dbt for transformations.", summary="Data engineer."),
    _c("CAND_0000131", "Analytics Engineer", 6.4,
       "Designed and maintained the analytical data warehouse on Snowflake supporting the BI team.",
       summary="Analytics engineer."),
    # --- generic SWE (D) ---
    _c("CAND_0000140", "Backend Engineer", 7.3,
       "Java backend development at a large enterprise — Spring Boot microservices and REST APIs.",
       summary="Backend engineer."),
    _c("CAND_0000141", "Frontend Engineer", 5.0,
       "Frontend engineering at a media company. React, TypeScript, design systems.",
       summary="Frontend engineer."),
    # --- services-career ranking (penalised) ---
    _c("CAND_0000150", "ML Engineer", 7.0,
       "Built recommendation features and ranking models for a client project.",
       company="Infosys", loc="Noida, Uttar Pradesh", summary="ML at services firm."),
    # --- non-tech decoys with AI-curious summaries (E, sink) ---
    _c("CAND_0000160", "Content Writer", 8.0,
       "Content writing and SEO strategy for a tech-focused publication.",
       summary=DECOY.format(y=8)),
    _c("CAND_0000161", "Operations Manager", 9.0,
       "Operations management role at a logistics company. Owned warehouse throughput.",
       summary=DECOY.format(y=9)),
    _c("CAND_0000162", "Accountant", 10.0,
       "Senior accounting role — month-end close, statutory compliance, GL ownership.",
       summary=DECOY.format(y=10)),
    _c("CAND_0000163", "Sales Executive", 6.0,
       "Enterprise sales of cloud software solutions into the mid-market.",
       summary=DECOY.format(y=6)),
    # --- honeypots (impossible internal facts -> excluded) ---
    _c("CAND_0000190", "Frontend Engineer", 9.9,
       "Frontend engineering at a media company. React, TypeScript.",
       start="2023-09-10", end=None, months=166, summary=DECOY.format(y=10)),
    _c("CAND_0000191", ".NET Developer", 8.0,
       "Test automation and QA engineering for a fintech product.",
       start="2024-11-03", end=None, months=144, company="Mphasis", summary=DECOY.format(y=8)),
]
