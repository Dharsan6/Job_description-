"""Shared configuration for the intelligent recruitment platform."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_CACHE_DIR = BASE_DIR / ".model_cache"
DEFAULT_RESUME_CSV = DATA_DIR / "resumes.csv"
RESUME_COLUMN = "Resume_str"

SEMANTIC_MODEL_NAME = "all-MiniLM-L6-v2"
TFIDF_WEIGHT = 0.4
SEMANTIC_WEIGHT = 0.6
KEYWORD_BOOST_FACTOR = 0.08
TFIDF_MAX_FEATURES = 12000
TOP_K_DEFAULT = 25

IMPORTANT_SKILLS = {
    "python",
    "flask",
    "django",
    "fastapi",
    "machine learning",
    "deep learning",
    "nlp",
    "sql",
    "pandas",
    "numpy",
    "scikit learn",
    "sklearn",
    "tensorflow",
    "pytorch",
    "javascript",
    "typescript",
    "react",
    "html",
    "css",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "rest api",
    "microservices",
    "postgresql",
    "mysql",
    "git",
    "linux",
    "spark",
    "hadoop",
}

SAMPLE_JOBS = [
    {
        "job_id": "J101",
        "title": "AI Engineer",
        "description": "Build NLP and ML products using Python, PyTorch, APIs, and cloud deployment.",
    },
    {
        "job_id": "J102",
        "title": "Backend Python Developer",
        "description": "Develop Flask APIs, SQL databases, testing pipelines, and Dockerized services.",
    },
    {
        "job_id": "J103",
        "title": "Data Scientist",
        "description": "Create machine learning models, data pipelines, analytics, and model evaluation.",
    },
    {
        "job_id": "J104",
        "title": "Frontend Engineer",
        "description": "Build React interfaces with JavaScript, responsive CSS, and API integrations.",
    },
    {
        "job_id": "J105",
        "title": "Cloud Engineer",
        "description": "Design scalable cloud systems with AWS, Kubernetes, Docker, and CI/CD automation.",
    },
]
