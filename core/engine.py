"""Main recruitment intelligence engine."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from core.config import (
    DEFAULT_RESUME_CSV,
    IMPORTANT_SKILLS,
    KEYWORD_BOOST_FACTOR,
    MODEL_CACHE_DIR,
    SAMPLE_JOBS,
    SEMANTIC_MODEL_NAME,
    SEMANTIC_WEIGHT,
    TFIDF_MAX_FEATURES,
    TFIDF_WEIGHT,
    TOP_K_DEFAULT,
)
from core.data_loader import load_resumes
from core.preprocessing import get_nlp, normalize_phrase, preprocess_text


def _clamp01(score: float) -> float:
    return max(0.0, min(1.0, score))


def _normalize_scores_to_percent(scores: list[float]) -> list[float]:
    """Min-max normalize scores into a 0-100 percentage range."""
    if not scores:
        return []
    clamped = [max(0.0, min(1.0, s)) for s in scores]
    min_score = min(clamped)
    max_score = max(clamped)
    if max_score == min_score:
        return [round(s * 100.0, 2) for s in clamped]
    return [round(((s - min_score) / (max_score - min_score)) * 100.0, 2) for s in clamped]


@lru_cache(maxsize=1)
def get_semantic_model():
    """Load and cache sentence-transformers model from project-local cache."""
    from sentence_transformers import SentenceTransformer

    MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        # Prefer local cache for demo environments with restricted network.
        return SentenceTransformer(
            SEMANTIC_MODEL_NAME,
            cache_folder=str(MODEL_CACHE_DIR),
            local_files_only=True,
        )
    except Exception:
        try:
            # Fallback to downloading if network allows.
            return SentenceTransformer(
                SEMANTIC_MODEL_NAME,
                cache_folder=str(MODEL_CACHE_DIR),
                local_files_only=False,
            )
        except Exception:
            return None


class RecruitmentEngine:
    """Production-like intelligent recruitment engine."""

    def __init__(self, csv_path: Path | str = DEFAULT_RESUME_CSV):
        self.csv_path = Path(csv_path)
        self.uploaded_resumes: list[str] = []
        self.reload_dataset()

    def reload_dataset(self) -> None:
        self.dataset_resumes = load_resumes(self.csv_path)

    def _all_resumes(self) -> list[str]:
        return self.dataset_resumes + self.uploaded_resumes

    @staticmethod
    def extract_skills(text: str) -> set[str]:
        """
        Extract skills from text using:
        1) predefined skill list matching (robust normalized substring match)
        2) optional spaCy noun-chunk extraction as a backoff when list matching is empty
        """
        cleaned = str(text or "")
        if not cleaned.strip():
            return set()

        normalized_text = f" {normalize_phrase(cleaned)} "
        found: set[str] = set()

        # Fast path: direct match against curated skill list.
        for skill in IMPORTANT_SKILLS:
            if f" {normalize_phrase(skill)} " in normalized_text:
                found.add(skill)
        if found:
            return found

        # Backoff: use spaCy noun chunks and map them back to known skills.
        nlp = get_nlp()
        if nlp is None:
            return found

        try:
            doc = nlp(cleaned)
            noun_phrases = [
                normalize_phrase(chunk.text)
                for chunk in doc.noun_chunks
                if chunk.text and chunk.text.strip()
            ]
        except Exception:
            return found

        for skill in IMPORTANT_SKILLS:
            norm_skill = normalize_phrase(skill)
            if not norm_skill:
                continue
            # If either direction contains the other, we treat it as a match.
            for phrase in noun_phrases:
                if phrase and (norm_skill in phrase or phrase in norm_skill):
                    found.add(skill)
                    break

        return found

    @staticmethod
    def match_label(score_percent: float) -> str:
        if score_percent >= 75:
            return "High"
        if score_percent >= 45:
            return "Medium"
        return "Low"

    @staticmethod
    def _keyword_boost(job_skills: set[str], resume_skills: set[str]) -> float:
        if not job_skills:
            return 0.0
        overlap = len(job_skills & resume_skills) / len(job_skills)
        return overlap * KEYWORD_BOOST_FACTOR

    @staticmethod
    def _score_to_percent(score: float) -> float:
        return round(_clamp01(score) * 100.0, 2)

    def add_uploaded_resume(self, resume_text: str) -> int:
        clean = resume_text.strip()
        if not clean:
            raise ValueError("Uploaded resume text is empty.")
        self.uploaded_resumes.append(clean)
        return len(self._all_resumes())

    def _tfidf_scores(self, resumes: list[str], job_description: str) -> list[float]:
        normalized_resumes = [preprocess_text(text) for text in resumes]
        normalized_job = preprocess_text(job_description)
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=TFIDF_MAX_FEATURES,
            sublinear_tf=True,
            min_df=1,
        )
        matrix = vectorizer.fit_transform(normalized_resumes + [normalized_job])
        sims = cosine_similarity(matrix[:-1], matrix[-1])
        return [_clamp01(float(item[0])) for item in sims]

    def _semantic_scores(self, resumes: list[str], job_description: str) -> list[float]:
        raise NotImplementedError("Use _semantic_scores_with_fallback().")

    def _semantic_scores_with_fallback(
        self,
        resumes: list[str],
        job_description: str,
        fallback_scores: list[float] | None = None,
    ) -> list[float]:
        """
        Semantic similarity in [0,1].
        If BERT can't load, fall back to `fallback_scores` (typically TF-IDF).
        """
        model = get_semantic_model()
        if model is None:
            return fallback_scores if fallback_scores is not None else [0.0 for _ in resumes]

        resume_embeddings = model.encode(resumes, convert_to_numpy=True, normalize_embeddings=True)
        job_embedding = model.encode([job_description], convert_to_numpy=True, normalize_embeddings=True)[0]
        cosine = np.dot(resume_embeddings, job_embedding)  # in [-1, 1]
        bert01 = (cosine + 1.0) / 2.0
        return [_clamp01(float(value)) for value in bert01]

    def match_resumes(
        self,
        job_description: str,
        top_k: int | None = TOP_K_DEFAULT,
        min_score: float = 0.0,
        max_score: float = 100.0,
        required_skills: list[str] | None = None,
    ) -> list[dict[str, object]]:
        text = (job_description or "").strip()
        if not text:
            raise ValueError("Job description is required.")

        resumes = self._all_resumes()
        if not resumes:
            return []

        tfidf_scores = self._tfidf_scores(resumes, text)
        semantic_scores = self._semantic_scores_with_fallback(
            resumes=resumes,
            job_description=text,
            fallback_scores=tfidf_scores,
        )
        jd_skills = self.extract_skills(text)
        normalized_required_skills = {normalize_phrase(skill) for skill in (required_skills or []) if skill.strip()}

        fused_scores = [
            (SEMANTIC_WEIGHT * semantic_scores[i]) + (TFIDF_WEIGHT * tfidf_scores[i])
            for i in range(len(resumes))
        ]
        match_percents = _normalize_scores_to_percent(fused_scores)

        ranked: list[dict[str, object]] = []
        for idx, resume in enumerate(resumes):
            resume_skills = self.extract_skills(resume)
            percent = match_percents[idx]

            matched = sorted(jd_skills & resume_skills)
            missing = sorted(jd_skills - resume_skills)

            if normalized_required_skills:
                resume_norm_skills = {normalize_phrase(skill) for skill in resume_skills}
                if not normalized_required_skills.issubset(resume_norm_skills):
                    continue

            if percent < min_score or percent > max_score:
                continue

            ranked.append(
                {
                    "resume_id": idx + 1,
                    "match_score": percent,
                    "label": self.match_label(percent),
                    "matched_skills": matched,
                    "missing_skills": missing,
                }
            )

        ranked.sort(key=lambda item: float(item["match_score"]), reverse=True)
        return ranked[:top_k] if top_k else ranked

    def recommend_jobs(self, resume_text: str, top_k: int = 3) -> list[dict[str, object]]:
        clean_resume = (resume_text or "").strip()
        if not clean_resume:
            raise ValueError("Resume text is required for job recommendations.")

        model = get_semantic_model()
        job_descriptions = [job["description"] for job in SAMPLE_JOBS]

        # TF-IDF always computed for hybrid scoring.
        tfidf_scores = self._tfidf_scores(job_descriptions, clean_resume)

        if model is None:
            # Fallback when BERT can't load.
            semantic_sims = np.array(tfidf_scores, dtype=float)
        else:
            resume_embedding = model.encode([clean_resume], convert_to_numpy=True, normalize_embeddings=True)[0]
            job_embeddings = model.encode(job_descriptions, convert_to_numpy=True, normalize_embeddings=True)
            cosine = np.dot(job_embeddings, resume_embedding)  # [-1, 1]
            semantic_sims = (cosine + 1.0) / 2.0

        recommendations = []
        resume_skills = self.extract_skills(clean_resume)
        for index, job in enumerate(SAMPLE_JOBS):
            job_skills = self.extract_skills(job["description"])
            fused = (SEMANTIC_WEIGHT * float(semantic_sims[index])) + (TFIDF_WEIGHT * tfidf_scores[index])
            score = self._score_to_percent(fused)
            recommendations.append(
                {
                    "job_id": job["job_id"],
                    "title": job["title"],
                    "score": score,
                    "matched_skills": sorted(job_skills & resume_skills),
                    "missing_skills": sorted(job_skills - resume_skills),
                }
            )
        recommendations.sort(key=lambda item: float(item["score"]), reverse=True)
        return recommendations[:top_k]
