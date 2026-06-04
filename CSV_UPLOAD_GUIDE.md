# CSV Dataset Upload Feature

## 🎯 Overview

You can now upload your own CSV resume datasets to the AI Resume Analyzer!

---

## 🌐 Upload Methods

### Method 1: Web Interface (Easiest)

1. Start the Flask app:
   ```bash
   python3 backend/app.py
   ```

2. Open in browser:
   ```
   http://127.0.0.1:5000/upload_dataset_page
   ```

3. Drag & drop or click to select your CSV file

4. Click "Upload Dataset"

---

### Method 2: cURL Command

```bash
curl -X POST http://127.0.0.1:5000/upload_dataset \
  -F "dataset=@/path/to/your/resumes.csv"
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/upload_dataset \
  -F "dataset=@data/my_resumes.csv"
```

---

### Method 3: Python Script

```python
import requests

with open('data/my_resumes.csv', 'rb') as f:
    files = {'dataset': f}
    response = requests.post('http://127.0.0.1:5000/upload_dataset', files=files)
    print(response.json())
```

Or use the provided script:
```bash
python3 upload_dataset_example.py data/my_resumes.csv
```

---

## 📋 CSV Format Requirements

Your CSV file must have this structure:

```csv
Resume_str
"Data scientist with 5 years of experience in Python, machine learning, NLP..."
"Full-stack developer proficient in React, Node.js, PostgreSQL, and AWS..."
"DevOps engineer with expertise in Docker, Kubernetes, CI/CD pipelines..."
```

**Requirements:**
- ✅ Must be a `.csv` file
- ✅ Must have a column named `Resume_str`
- ✅ Each row contains one resume text
- ✅ Empty rows are automatically skipped
- ✅ Maximum file size: 8MB

---

## 🔄 API Endpoints

### 1. Upload Dataset

**Endpoint:** `POST /upload_dataset`

**Request:**
```bash
curl -X POST http://127.0.0.1:5000/upload_dataset \
  -F "dataset=@resumes.csv"
```

**Response (Success):**
```json
{
  "message": "Dataset uploaded successfully",
  "resume_count": 150,
  "backup_created": true
}
```

**Response (Error):**
```json
{
  "error": "CSV must contain a 'Resume_str' column."
}
```

---

### 2. Get Dataset Info

**Endpoint:** `GET /dataset_info`

**Request:**
```bash
curl http://127.0.0.1:5000/dataset_info
```

**Response:**
```json
{
  "path": "/Users/dharsans/Job_description/data/resumes.csv",
  "resume_count": 150,
  "sample_preview": "Data scientist with 5 years of experience in Python..."
}
```

---

## 🛡️ Safety Features

### Automatic Backup
- Before uploading a new dataset, the system automatically creates a backup
- Backup location: `data/resumes_backup.csv`
- If upload fails, the original dataset is restored

### Validation
- ✅ File type validation (CSV only)
- ✅ Column validation (`Resume_str` required)
- ✅ Empty value filtering
- ✅ Error handling with rollback

---

## 📊 Example Datasets

### Small Dataset (5 resumes)
```csv
Resume_str
"Data scientist with Python, ML, NLP, TensorFlow, SQL"
"Frontend developer with React, JavaScript, TypeScript, CSS"
"Backend engineer with Java, Spring Boot, PostgreSQL, Docker"
"DevOps engineer with AWS, Kubernetes, CI/CD, Terraform"
"Full-stack developer with Node.js, React, MongoDB, GraphQL"
```

### Large Dataset (1000+ resumes)
For production use, you can upload datasets with hundreds or thousands of resumes. The system will:
- Cache embeddings for performance
- Use batch processing
- Return top K results efficiently

---

## 🚀 Complete Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. User uploads CSV via web interface or API           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. System validates file format and column             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. Creates backup of existing dataset                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. Saves new dataset to data/resumes.csv               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  5. Loads and validates dataset with pandas             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  6. Returns success with resume count                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  7. New dataset immediately available for matching      │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

### Test the upload feature:

```bash
# Start the app
python3 backend/app.py

# In another terminal, test upload
curl -X POST http://127.0.0.1:5000/upload_dataset \
  -F "dataset=@data/resumes.csv"

# Check dataset info
curl http://127.0.0.1:5000/dataset_info

# Test matching with new dataset
curl -X POST http://127.0.0.1:5000/match \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Python developer with ML experience"}'
```

---

## 📝 Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "No dataset file provided" | Missing file in request | Use field name 'dataset' |
| "Only CSV files are supported" | Wrong file type | Upload .csv file only |
| "CSV must contain 'Resume_str' column" | Missing required column | Add Resume_str column |
| "No valid resumes found" | All rows empty | Add resume text data |
| "Could not process dataset file" | Corrupted file | Check CSV format |

---

## 🎉 Summary

You can now:

✅ Upload CSV datasets via web interface  
✅ Upload via API (cURL, Python, etc.)  
✅ Automatic backup before upload  
✅ Validation and error handling  
✅ View current dataset info  
✅ Immediate availability for matching  

**Access the upload page:**
```
http://127.0.0.1:5000/upload_dataset_page
```
