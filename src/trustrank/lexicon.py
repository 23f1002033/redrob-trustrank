from __future__ import annotations

TIER_A_RANKING_RECSYS = (
    "ranking model", "ranking models", "learning to rank", "recommendation",
    "recommender", "recommendation-style", "collaborative filtering",
    "matrix factorization", "discovery feed", "search relevance",
    "retrieval", "personalization", "recsys",
)

TIER_B_APPLIED_ML = (
    "churn prediction", "conversion likelihood", "lifetime value",
    "predictive modeling", "fraud detection", "fraud-detection",
    "nlp pipeline", "nlp pipelines", "sentiment analysis",
    "document classification", "named-entity", "transformer", "transformers",
    "anomaly detection", "forecasting model", "gradient-boosted",
)

TIER_C_LIGHT_ML = (
    "lightweight ml", "clustering", "classification model", "scikit-learn",
    "sklearn", "xgboost", "lightgbm", "data science", "analytics-engineering",
    "feature engineering",
)

TIER_D_DATA_ENG = (
    "data pipeline", "data pipelines", "apache airflow", "pyspark", "spark",
    "dbt", "etl", "data warehouse", "kafka", "snowflake", "schema-registry",
)

TIER_D_GENERIC_SWE = (
    "frontend engineering", "full-stack web", "backend development",
    "android mobile development", "mobile development", "devops",
    "test automation", "qa engineering", "spring boot", "microservices",
    "cloud infrastructure",
)

CV_SPEECH_ROBOTICS = (
    "computer vision", "image classification", "image moderation",
    "object detection", "resnet", "segmentation", "ocr",
    "speech recognition", "asr", "tts", "robotics", "slam",
)

NLP_IR_RESCUE = (
    "nlp", "information retrieval", "retrieval", "ranking", "recommendation",
    "search", "embedding", "language model",
)

PRODUCT_CONTEXT = (
    "product company", "customer-facing", "shipped", "in production",
    "production", "at scale", "real users", "paying customers",
    "e-commerce platform", "our product",
)

SERVICES_COMPANIES = (
    "tcs", "tata consultancy", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "tech mahindra", "hcl", "mindtree", "ltimindtree", "mphasis",
)

DECOY_SUMMARY_SIGNATURES = (
    "haven't done it in a professional capacity",
    "self-learner level",
    "played with the openai and anthropic apis",
    "built a small rag side project",
    "experimented with chatgpt",
    "curious about how ai tools could augment",
    "apply my domain expertise alongside emerging ai",
)

PREFERRED_LOCATIONS = (
    "noida", "pune", "delhi", "ncr", "gurugram", "gurgaon", "hyderabad",
    "mumbai", "bangalore", "bengaluru",
)


def _hits(text: str, bank: tuple[str, ...]) -> list[str]:
    return [p for p in bank if p in text]
