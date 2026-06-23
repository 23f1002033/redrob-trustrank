from __future__ import annotations


def _signals(active="2026-06-01", resp=0.8, otw=True, ic=0.9):
    return {
        "last_active_date": active,
        "recruiter_response_rate": resp,
        "open_to_work_flag": otw,
        "interview_completion_rate": ic,
        "github_activity_score": -1,
        "profile_completeness_score": 80,
    }


def _role(title, company, desc, start, end, months, current=False):
    return {
        "company": company, "title": title, "start_date": start, "end_date": end,
        "duration_months": months, "is_current": current,
        "industry": "Software", "company_size": "201-500", "description": desc,
    }


FIXTURES = [
    {  # BULLSEYE — ranking/recsys, shipped, product, 6y, active
        "candidate_id": "CAND_9000001",
        "profile": {"anonymized_name": "A", "headline": "x", "summary": "Applied ML engineer.",
                    "location": "Pune, Maharashtra", "country": "India",
                    "years_of_experience": 6.0, "current_title": "ML Engineer",
                    "current_company": "Hooli", "current_industry": "Software"},
        "career_history": [_role("ML Engineer", "Hooli",
            "Trained and shipped multiple ranking models for our product's discovery feed "
            "using xgboost and lightgbm. Designed features across content metadata, user "
            "behavior, and item engagement. Deployed to production serving real users.",
            "2021-01-01", None, 66, current=True)],
        "education": [], "skills": [], "redrob_signals": _signals(),
    },
    {  # STRONG B — applied ML, customer-facing, 6.8y
        "candidate_id": "CAND_9000002",
        "profile": {"anonymized_name": "B", "headline": "x", "summary": "Data scientist.",
                    "location": "Bangalore, Karnataka", "country": "India",
                    "years_of_experience": 6.8, "current_title": "Data Scientist",
                    "current_company": "Initech", "current_industry": "E-commerce"},
        "career_history": [_role("Data Scientist", "Initech",
            "Customer-facing predictive modeling for an e-commerce platform — churn prediction, "
            "conversion likelihood, lifetime value estimation. Used scikit-learn and xgboost in "
            "production.", "2020-01-01", None, 78, current=True)],
        "education": [], "skills": [], "redrob_signals": _signals(resp=0.6),
    },
    {  # CV-only — should be penalised (no NLP/IR)
        "candidate_id": "CAND_9000003",
        "profile": {"anonymized_name": "C", "headline": "x", "summary": "CV engineer.",
                    "location": "Chennai, Tamil Nadu", "country": "India",
                    "years_of_experience": 6.8, "current_title": "AI Specialist",
                    "current_company": "Acme", "current_industry": "Software"},
        "career_history": [_role("AI Specialist", "Acme",
            "Built computer vision models for our product's image moderation feature using "
            "pytorch — fine-tuned resnet variants on a labeled dataset of ~200k images.",
            "2020-01-01", None, 78, current=True)],
        "education": [], "skills": [], "redrob_signals": _signals(),
    },
    {  # DATA ENG — ML-adjacent, 6.9y
        "candidate_id": "CAND_9000004",
        "profile": {"anonymized_name": "D", "headline": "x", "summary": "Data engineer.",
                    "location": "Hyderabad, Telangana", "country": "India",
                    "years_of_experience": 6.9, "current_title": "Data Engineer",
                    "current_company": "Globex", "current_industry": "Software"},
        "career_history": [_role("Data Engineer", "Globex",
            "Built and maintained data pipelines on apache airflow processing ~500gb of daily "
            "transactional data. Worked extensively with spark (pyspark) and dbt.",
            "2020-01-01", None, 78, current=True)],
        "education": [], "skills": [], "redrob_signals": _signals(),
    },
    {  # SERVICES CAREER — strong-ish ML evidence but entirely at services firms
        "candidate_id": "CAND_9000005",
        "profile": {"anonymized_name": "E", "headline": "x", "summary": "ML at services.",
                    "location": "Noida, Uttar Pradesh", "country": "India",
                    "years_of_experience": 7.0, "current_title": "ML Engineer",
                    "current_company": "Infosys", "current_industry": "IT Services"},
        "career_history": [_role("ML Engineer", "Infosys",
            "Built recommendation features and ranking models for a client project.",
            "2019-01-01", None, 90, current=True)],
        "education": [], "skills": [], "redrob_signals": _signals(),
    },
    {  # HONEYPOT — role duration_months impossible vs dates & total experience
        "candidate_id": "CAND_9000099",
        "profile": {"anonymized_name": "H", "headline": "x",
                    "summary": "Software engineer ... built a small RAG side project ... "
                               "haven't done it in a professional capacity yet.",
                    "location": "Noida, Uttar Pradesh", "country": "India",
                    "years_of_experience": 9.9, "current_title": "Frontend Engineer",
                    "current_company": "Wayne Enterprises", "current_industry": "Conglomerate"},
        "career_history": [_role("Frontend Engineer", "Wayne Enterprises",
            "Frontend engineering at a media company. React, TypeScript.",
            "2023-09-10", None, 166, current=True)],
        "education": [], "skills": [], "redrob_signals": _signals(),
    },
]
