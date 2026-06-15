import re
from typing import List, Dict

SKILL_PATTERNS = [
    # Languages
    "python", "sql", "java", "scala", "r", "bash", "javascript", "typescript",
    "c++", "c#", "rust", "go", "swift", "kotlin",
    # ML / DL
    "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn", "xgboost",
    "lightgbm", "huggingface", "transformers", "spacy", "nltk",
    # Data
    "pandas", "numpy", "spark", "pyspark", "airflow", "dbt", "kafka",
    "flink", "prefect", "luigi",
    # AI / LLM
    "langchain", "openai", "llm", "rag", "vector search", "embeddings",
    "chromadb", "faiss", "pinecone", "llamaindex",
    # Cloud
    "aws", "gcp", "azure", "ec2", "s3", "lambda", "ecs", "fargate",
    "sagemaker", "bigquery", "dataflow", "ecr",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "snowflake", "databricks", "redshift",
    # DevOps
    "docker", "kubernetes", "terraform", "ci/cd", "github actions",
    "jenkins", "fastapi", "flask", "django", "nginx", "streamlit",
    # Methodologies
    "agile", "scrum", "mlops", "etl", "rest api", "graphql",
]

YOUR_SKILLS = [
    "python", "sql", "javascript", "pandas", "numpy", "pytorch",
    "keras", "tensorflow", "fastapi", "flask", "django", "langchain",
    "chromadb", "docker", "aws", "s3", "ec2", "ecr", "ecs",
    "github actions", "nginx", "rag", "embeddings", "postgresql",
    "redis", "pyspark", "etl", "rest api", "agile", "scrum",
    "spacy", "nlp",
]


def extract_skills(text: str) -> List[str]:
    """Extract tech skills from any text."""
    text_lower = text.lower()
    found = set()
    for skill in SKILL_PATTERNS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return sorted(found)


def analyse_gap(jd_text: str) -> Dict:
    """
    Compare JD requirements against your skills.
    Returns matched, missing, coverage percentage.
    """
    jd_skills = extract_skills(jd_text)
    your_set = set(YOUR_SKILLS)
    jd_set = set(jd_skills)

    matched = sorted(your_set & jd_set)
    missing = sorted(jd_set - your_set)
    coverage = round(len(matched) / len(jd_set) * 100, 1) if jd_set else 100.0

    return {
        "jd_skills": jd_skills,
        "matched": matched,
        "missing": missing,
        "coverage_pct": coverage,
        "total_required": len(jd_skills),
        "total_matched": len(matched),
        "total_missing": len(missing),
    }