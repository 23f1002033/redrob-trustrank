"""Evidence phrase banks, derived from the real description templates."""
from __future__ import annotations

TIER_A_RANKING_RECSYS = (
    "ranking", "ranking model", "ranking models", "ranking pipeline",
    "ranking system", "ranking layer", "learning to rank", "learning-to-rank",
    "recommendation", "recommender", "recommendation-style", "recommendation system",
    "collaborative filtering", "matrix factorization", "discovery feed",
    "search relevance", "search ranking", "semantic search", "vector search",
    "retrieval", "two-tower", "personalization", "recsys",
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

# --- DEPTH signals (the JD's specific must-haves / nice-to-haves) ----------
# Used to differentiate WITHIN the top family for NDCG@10: a candidate whose
# ranking work shows the JD's exact stack (embeddings, vector search, scale,
# evaluation, learning-to-rank) outranks a generic recsys mention.
DEPTH_SIGNALS = {
    "retrieval/embeddings": (
        "embedding", "embeddings", "sentence-transformer", "semantic search",
        "dense retrieval", "two-tower", "bi-encoder", "cross-encoder", "bert",
        "bge", " e5 ", "rag",
    ),
    "vector search": (
        "vector database", "vector db", "pinecone", "weaviate", "qdrant",
        "milvus", "faiss", "elasticsearch", "opensearch", "hybrid search",
        "bm25",
    ),
    "production scale": (
        "at scale", "million", "m+", "10m", "50m", "100m", "billion", "qps",
        "queries per", "requests per", "real-time", "low latency", "latency",
        "high throughput", "serving",
    ),
    "evaluation rigor": (
        "ndcg", "mrr", "recall@", "precision@", "a/b test", "ab test",
        "offline evaluation", "online evaluation", "ranking metric",
        "click-through", "ctr", "regression test",
    ),
    "learning-to-rank": (
        "learning to rank", "learning-to-rank", "lambdamart", "neural ranking",
        "gradient-boosted ranking", "xgboost", "lightgbm",
    ),
    "llm fine-tuning": (
        "lora", "qlora", "peft", "fine-tune", "fine-tuned", "fine-tuning",
        "rlhf", "instruction-tun",
    ),
    "end-to-end ownership": (
        "owned", "end-to-end", "from scratch", "built and shipped",
        "designed and built", "led the",
    ),
}


def _hits(text: str, bank: tuple[str, ...]) -> list[str]:
    return [p for p in bank if p in text]
