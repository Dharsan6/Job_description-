"""Worker process: polls SQS (or local queue) and processes resume messages."""

from __future__ import annotations

import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.queue_service import receive_from_queue
from core.matching import DEFAULT_RESUME_CSV, rank_resumes


def process_message(message: dict) -> None:
    resume_text = message.get("resume_text", "").strip()
    job_description = message.get("job_description", "").strip()
    filename = message.get("filename", "unknown")

    if not resume_text:
        print(f"[WORKER] Skipping empty resume_text for {filename}", flush=True)
        return

    if job_description:
        results = rank_resumes([resume_text], job_description, top_k=1)
    else:
        from core.matching import rank_dataset_resumes
        results = rank_dataset_resumes(resume_text, DEFAULT_RESUME_CSV, top_k=5)

    print(f"[WORKER] Processed '{filename}': {results}", flush=True)


def run():
    print("[WORKER] Starting — waiting for messages...", flush=True)
    while True:
        message = receive_from_queue(wait_seconds=5)
        if message:
            try:
                process_message(message)
            except Exception as e:
                print(f"[WORKER ERROR] {type(e).__name__}: {e}", flush=True)
        else:
            time.sleep(1)


if __name__ == "__main__":
    run()
