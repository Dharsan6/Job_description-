# Intelligent Recruitment Platform

Production-style upgrade of the Job Description Matching System with hybrid semantic scoring, explainable skill matching, resume upload support, dashboard charts, filtering, and job recommendations.

## Folder Structure

```text
Job_description/
├── backend/
│   └── app.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── engine.py
│   ├── file_parser.py
│   ├── matching.py
│   └── preprocessing.py
├── data/
│   └── resumes.csv
├── frontend/
│   └── index.html
├── README.md
└── requirements.txt
```

## Key Features

- Advanced preprocessing with spaCy lemmatization
- Hybrid matching score:
  - `0.6 * BERT semantic similarity`
  - `0.4 * TF-IDF similarity`
  - keyword skill boost
- Explainable output:
  - `resume_id`, `match_score`, `label`, `matched_skills`, `missing_skills`
- Resume upload endpoint for PDF/DOC/DOCX/TXT
- Candidate filtering by score range and required skills
- Dashboard with:
  - top candidates chart
  - score distribution chart
- Job recommendation system from resume text
- Health endpoint and API error handling

## API Endpoints

- `GET /health`
- `POST /match`
- `POST /upload_resume`
- `POST /recommend_jobs`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
python3 backend/app.py
```

App URL: `http://127.0.0.1:5000`

## `/match` Request Example

```json
{
  "job_description": "Looking for a Python NLP engineer with Flask and SQL experience.",
  "min_score": 30,
  "max_score": 100,
  "skills": "python,flask",
  "top_k": 10
}
```

## `/match` Response Example

```json
{
  "count": 2,
  "results": [
    {
      "resume_id": 4,
      "match_score": 87.52,
      "label": "High",
      "matched_skills": ["flask", "nlp", "python", "sql"],
      "missing_skills": [],
      "source": "dataset"
    }
  ]
}
```
