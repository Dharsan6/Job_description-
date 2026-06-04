#!/usr/bin/env python3
"""Example: Upload a CSV dataset to the Resume Analyzer API."""

import requests

API_URL = "http://127.0.0.1:5000"

def upload_dataset(csv_file_path: str):
    """Upload a CSV dataset file."""
    with open(csv_file_path, 'rb') as f:
        files = {'dataset': f}
        response = requests.post(f"{API_URL}/upload_dataset", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Dataset uploaded successfully!")
        print(f"   Resume count: {data['resume_count']}")
        print(f"   Backup created: {data['backup_created']}")
    else:
        print(f"❌ Upload failed: {response.json()}")

def get_dataset_info():
    """Get current dataset information."""
    response = requests.get(f"{API_URL}/dataset_info")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 Current Dataset Info:")
        print(f"   Path: {data['path']}")
        print(f"   Resume count: {data['resume_count']}")
        if data['sample_preview']:
            print(f"   Sample: {data['sample_preview']}...")
    else:
        print(f"❌ Error: {response.json()}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 upload_dataset_example.py <path_to_csv>")
        print("\nExample:")
        print("  python3 upload_dataset_example.py data/my_resumes.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    # Upload the dataset
    upload_dataset(csv_path)
    
    # Get updated info
    get_dataset_info()
