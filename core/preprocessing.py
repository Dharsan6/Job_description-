"""Text normalization and NLP helpers."""

from __future__ import annotations

import re
import string
from functools import lru_cache

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

PUNCTUATION_TABLE = str.maketrans({char: " " for char in string.punctuation})


@lru_cache(maxsize=1)
def get_nlp():
    """Load spaCy English model with safe fallback download."""
    try:
        import spacy
        from spacy.cli import download as spacy_download

        try:
            return spacy.load("en_core_web_sm", disable=["ner", "textcat"])
        except OSError:
            spacy_download("en_core_web_sm")
            return spacy.load("en_core_web_sm", disable=["ner", "textcat"])
    except Exception:
        return None


def preprocess_text(text: str) -> str:
    """Lowercase, remove punctuation/stopwords, and lemmatize with spaCy."""
    if not text:
        return ""

    cleaned = re.sub(r"\s+", " ", str(text).lower().translate(PUNCTUATION_TABLE)).strip()
    if not cleaned:
        return ""

    nlp = get_nlp()
    if nlp is None:
        tokens = [tok for tok in cleaned.split() if tok not in ENGLISH_STOP_WORDS]
        return " ".join(tokens)

    doc = nlp(cleaned)
    lemmas = []
    for token in doc:
        if token.is_space or token.is_punct or token.is_stop:
            continue
        lemma = token.lemma_.strip().lower()
        if lemma and lemma != "-pron-":
            lemmas.append(lemma)
    return " ".join(lemmas)


def normalize_phrase(phrase: str) -> str:
    """Normalize a phrase for robust exact matching."""
    return re.sub(r"\s+", " ", preprocess_text(phrase)).strip()
