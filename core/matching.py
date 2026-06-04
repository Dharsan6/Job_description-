"""
AI Resume Intelligence Platform - Core Matching & Scoring Engine.
Optimized for semantic relevance, technical skill extraction, and career intelligence.
"""

from __future__ import annotations
import re
import numpy as np
from pathlib import Path
from typing import Any
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

# --- Configuration & Constants ---
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_CACHE_DIR = BASE_DIR / ".model_cache"

# Large technical skills database
TECHNICAL_SKILLS = [
    "python", "java", "c++", "machine learning", "deep learning", "nlp",
    "computer vision", "opencv", "mediapipe", "mongodb", "mysql", "sql",
    "react", "javascript", "html", "css", "fastapi", "flask", "docker",
    "aws", "cloud", "cyber security", "penetration testing", "network security",
    "data analysis", "pandas", "matplotlib", "seaborn", "git", "github",
    "rest api", "api", "telegram bot", "rag", "llm", "chroma", "vector database"
]

# Career Path Mapping
CAREER_MAP = {
    "machine learning": ["Machine Learning Engineer", "AI Engineer"],
    "deep learning": ["AI Research Engineer"],
    "nlp": ["NLP Engineer"],
    "opencv": ["Computer Vision Engineer"],
    "cyber security": ["Security Analyst", "Ethical Hacker"],
    "react": ["Frontend Developer"],
    "mongodb": ["Backend Developer"],
    "fastapi": ["Python Backend Developer"],
    "rag": ["Generative AI Engineer"],
    "llm": ["LLM Engineer"]
}

# Global realistic jobs list
REALISTIC_ROLES = [
    "Machine Learning Engineer", "AI Engineer", "NLP Engineer",
    "Computer Vision Engineer", "Python Backend Developer",
    "Cyber Security Analyst", "Ethical Hacker", "Frontend Developer",
    "Cloud Engineer", "Data Scientist", "Data Analyst"
]

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load the embedding model once."""
    MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return SentenceTransformer(MODEL_NAME, cache_folder=str(MODEL_CACHE_DIR))

def clean_text(text: str) -> str:
    """Regex-based text cleaning for token matching."""
    if not text: return ""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def extract_skills(text: str) -> list[str]:
    """Robust skill extraction supporting multi-word and partial matches."""
    norm = f" {clean_text(text)} "
    found = []
    for skill in TECHNICAL_SKILLS:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, norm):
            found.append(skill)
    return sorted(list(set(found)))

def get_experience_info(text: str) -> dict[str, Any]:
    """Detect projects, certifications, and coding profiles."""
    norm = text.lower()
    projects = len(re.findall(r"\bproject\b|developed|implemented|built", norm))
    certs = len(re.findall(r"\bcertified\b|\bcertification\b|\bcertificate\b", norm))
    profiles = len(re.findall(r"github\.com|leetcode\.com|hackerrank\.com|linkedin\.com", norm))
    skills_count = len(extract_skills(text))
    has_internship = bool(re.search(r"\binternship\b|\bintern\b", norm))
    has_cloud_devops = any(s in norm for s in ["aws", "cloud", "docker", "kubernetes", "gcp", "azure"])
    return {
        "projects": projects, "certs": certs, "profiles": profiles,
        "skills_count": skills_count, "has_internship": has_internship,
        "has_cloud_devops": has_cloud_devops
    }

def infer_experience_level(text: str) -> str:
    """Heuristic logic for experience level detection."""
    info = get_experience_info(text)
    if info["has_internship"] and info["skills_count"] >= 8 and info["has_cloud_devops"]:
        return "Advanced"
    if info["projects"] >= 3 or (info["certs"] >= 2 and info["skills_count"] >= 5) or info["profiles"] >= 1:
        return "Intermediate"
    return "Beginner"

def predict_career_paths(resume_text: str) -> list[str]:
    """Generate career paths ONLY from detected resume skills."""
    skills = extract_skills(resume_text)
    paths = []
    for skill in skills:
        if skill in CAREER_MAP:
            paths.extend(CAREER_MAP[skill])
    unique_paths = list(dict.fromkeys(paths))
    return unique_paths[:5]

def get_resume_quality_score(resume_text: str) -> float:
    """Quality factors for resume assessment."""
    info = get_experience_info(resume_text)
    norm = clean_text(resume_text)
    project_score = min(25.0, info["projects"] * 5.0)
    skill_score = min(25.0, info["skills_count"] * 2.5)
    cert_score = min(15.0, info["certs"] * 7.5)
    profile_score = min(10.0, info["profiles"] * 10.0)
    length_score = min(15.0, len(norm.split()) / 40.0)
    achievement_bonus = 10.0 if re.search(r"award|won|achievement|top|first|gold", norm) else 0.0
    total = project_score + skill_score + cert_score + profile_score + length_score + achievement_bonus
    return round(max(10.0, min(100.0, total)), 2)

def analyze_resume(resume_text: str, job_description: str) -> dict[str, Any]:
    """Analyze resume against job description."""
    model = get_model()
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(job_description)
    emb = model.encode([resume_clean, jd_clean])
    semantic_sim = float(cosine_similarity([emb[0]], [emb[1]])[0][0])
    semantic_score = round(max(0.0, semantic_sim) * 100, 2)
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    if not job_skills: job_skills = ["python"]
    matched_skills = sorted(list(set(resume_skills) & set(job_skills)))
    missing_skills = sorted(list(set(job_skills) - set(resume_skills)))
    skill_match_pct = round((len(matched_skills) / len(job_skills)) * 100, 2) if job_skills else 0
    quality_score = get_resume_quality_score(resume_text)
    final_score = round((0.45 * semantic_score) + (0.35 * skill_match_pct) + (0.20 * quality_score), 2)
    exp_level = infer_experience_level(resume_text)
    career_paths = predict_career_paths(resume_text)
    feedback = []
    if "aws" in missing_skills or "cloud" in missing_skills: feedback.append("Add AWS/cloud deployment experience")
    if "docker" in missing_skills: feedback.append("Add containerization skills using Docker")
    if not re.search(r"\b\d+%\b|\bincreased\b|\breduced\b", resume_clean): feedback.append("Add measurable project impact and metrics")
    if not feedback: feedback.append("Strong profile.")
    return {
        "final_score": final_score, "semantic_score": semantic_score, "skill_score": skill_match_pct,
        "resume_quality": quality_score, "experience_level": exp_level, "matched_skills": matched_skills,
        "missing_skills": missing_skills, "career_paths": career_paths, "feedback": feedback[:3],
        "label": "Excellent" if final_score >= 80 else "Good" if final_score >= 60 else "Low"
    }

def recommend_jobs(job_text, jobs):
    """Specific implementation requested by user for job recommendations."""
    if not job_text:
        return []
    
    # Use existing infrastructure
    model = get_model()
    job_text = clean_text(job_text)
    
    embeddings = model.encode([job_text] + jobs)
    main_vec = embeddings[0]
    job_vecs = embeddings[1:]
    
    scores = cosine_similarity(job_vecs, [main_vec])
    results = []
    
    for i, s in enumerate(scores):
        results.append({
            "job": jobs[i],
            "score": round(float(s[0]) * 100, 2)
        })
    
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:5]

def rank_resumes(dataset: list[str], job_description: str) -> list[dict[str, Any]]:
    """Rank multiple resumes against one job description."""
    ranked = []
    for idx, resume_text in enumerate(dataset):
        analysis = analyze_resume(resume_text, job_description)
        rank_val = (0.5 * analysis["semantic_score"]) + (0.3 * analysis["resume_quality"]) + (0.2 * analysis["skill_score"])
        ranked.append({
            "resume_id": idx + 1, "score": round(rank_val, 2), "final_score": analysis["final_score"],
            "label": analysis["label"], "experience_level": analysis["experience_level"],
            "matched_skills": analysis["matched_skills"], "missing_skills": analysis["missing_skills"],
            "semantic_score": analysis["semantic_score"], "skill_score": analysis["skill_score"],
            "resume_quality_score": analysis["resume_quality"], "feedback": analysis["feedback"],
            "career_paths": analysis["career_paths"]
        })
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:10]

# Backward compatibility
def match_resume_to_job(resume_text: str, job_description: str) -> dict[str, Any]:
    return analyze_resume(resume_text, job_description)

DEFAULT_RESUME_CSV = BASE_DIR / "data" / "resumes.csv"
RESUME_COLUMN = "Resume_str"

def load_resume_dataset(csv_path: str | Path = DEFAULT_RESUME_CSV) -> list[str]:
    import pandas as pd
    try:
        df = pd.read_csv(csv_path)
        return df[RESUME_COLUMN].dropna().astype(str).tolist()
    except Exception:
        return []
