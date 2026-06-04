"""Flask API for the AI Resume Analyzer & Intelligence Platform."""

from __future__ import annotations
import sys
from io import BytesIO
from pathlib import Path
from typing import Any
from flask import Flask, jsonify, request, send_from_directory
from PyPDF2 import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.matching import (
    DEFAULT_RESUME_CSV,
    analyze_resume,
    rank_resumes,
    recommend_jobs,
    load_resume_dataset
)
from backend.queue_service import send_to_queue

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

GLOBAL_DATASET = []

# Global Jobs List as requested
jobs = [
    "Machine Learning Engineer",
    "AI Engineer",
    "NLP Engineer",
    "Computer Vision Engineer",
    "Python Backend Developer",
    "Cyber Security Analyst",
    "Ethical Hacker",
    "Frontend Developer",
    "Cloud Engineer",
    "Data Scientist",
    "Data Analyst"
]

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    extracted_pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            extracted_pages.append(text.strip())
    return "\n\n".join(extracted_pages).strip()

@app.get("/")
def home():
    return jsonify({"status": "API Running", "message": "Intelligence Engine Active"})

@app.get("/app")
def frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.post("/upload_resume")
def upload_resume():
    uploaded_files = request.files.getlist("resumes") or request.files.getlist("resume")
    if not uploaded_files:
        return jsonify({"error": "No PDFs provided."}), 400
    extracted = []
    for idx, f in enumerate(uploaded_files, start=1):
        if not f.filename.lower().endswith(".pdf"): continue
        try:
            text = extract_text_from_pdf(f.read())
            if text:
                extracted.append({"filename": f.filename, "resume_text": text})
                send_to_queue({"resume_id": idx, "filename": f.filename, "resume_text": text})
        except Exception as e:
            print(f"[PDF ERROR] {e}")
    return jsonify({"resumes": extracted})

@app.post("/match")
def match():
    payload = request.get_json(silent=True) or {}
    resumes = payload.get("resumes", [])
    job_description = str(payload.get("job_description") or "").strip()
    if not job_description or not resumes:
        return jsonify({"error": "Resumes and Job Description are required."}), 400
    try:
        results = rank_resumes(resumes, job_description)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommend_jobs', methods=['POST'])
def recommend_jobs_route():
    """Recommend jobs based on resume text or job description."""
    try:
        data = request.get_json()
        resume_text = data.get("resume_text", "")
        job_description = data.get("job_description", "")

        # Prioritize resume text for personalized recommendations
        input_text = resume_text if resume_text else job_description
        
        print("Received input for recommendation:", "Resume provided" if resume_text else job_description)

        if not input_text:
            return jsonify({
                "error": "Please provide a resume or job description for recommendations."
            }), 400

        result = recommend_jobs(input_text, jobs)
        
        print("Generated recommendations:", result)

        return jsonify({
            "recommendations": result
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.post("/rank")
def rank():
    payload = request.get_json(silent=True) or {}
    resume_text = str(payload.get("resume_text") or "").strip()
    if not resume_text:
        return jsonify({"error": "Dataset ranking requires valid resume text."}), 400
    dataset = GLOBAL_DATASET or load_resume_dataset()
    if not dataset:
        return jsonify({"error": "No dataset available."}), 400
    try:
        results = rank_resumes(dataset, resume_text)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/upload_csv")
def upload_csv():
    global GLOBAL_DATASET
    try:
        f = request.files.get("file") or request.files.get("dataset")
        if not f: return jsonify({"error": "No file."}), 400
        import pandas as pd
        df = pd.read_csv(f)
        col = "Resume_str" if "Resume_str" in df.columns else df.columns[0]
        GLOBAL_DATASET = df[col].dropna().astype(str).tolist()
        return jsonify({"message": "Loaded", "total": len(GLOBAL_DATASET)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)