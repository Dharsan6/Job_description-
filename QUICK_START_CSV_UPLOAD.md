# 🚀 Quick Start: CSV Upload Feature

## ✅ What's New

You can now upload your own CSV resume datasets!

---

## 🌐 Easiest Way: Web Interface

1. **Start the app:**
   ```bash
   python3 backend/app.py
   ```

2. **Open in browser:**
   ```
   http://127.0.0.1:5000/upload_dataset_page
   ```

3. **Upload your CSV:**
   - Drag & drop or click to browse
   - Click "Upload Dataset"
   - Done! ✅

---

## 📋 CSV Format

Your CSV must have a `Resume_str` column:

```csv
Resume_str
"Python developer with 5 years ML experience..."
"React frontend engineer with TypeScript..."
"DevOps engineer with AWS and Kubernetes..."
```

---

## 🔧 API Endpoints Added

### 1. Upload Dataset
```bash
POST /upload_dataset
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/upload_dataset \
  -F "dataset=@my_resumes.csv"
```

### 2. Get Dataset Info
```bash
GET /dataset_info
```

**Example:**
```bash
curl http://127.0.0.1:5000/dataset_info
```

### 3. Upload Page
```bash
GET /upload_dataset_page
```

**Browser:** `http://127.0.0.1:5000/upload_dataset_page`

---

## 🛡️ Safety Features

✅ **Automatic backup** before upload  
✅ **Validation** (CSV format, required columns)  
✅ **Rollback** if upload fails  
✅ **Error messages** for debugging  

---

## 📊 Complete Workflow

```
Upload CSV → Validate → Backup old → Save new → Load → Ready!
```

Your new dataset is immediately available for:
- `/match` endpoint
- `/recommend_jobs` endpoint
- Worker processing

---

## 🧪 Test It

```bash
# Start app
python3 backend/app.py

# Upload dataset
curl -X POST http://127.0.0.1:5000/upload_dataset \
  -F "dataset=@data/resumes.csv"

# Check info
curl http://127.0.0.1:5000/dataset_info

# Test matching
curl -X POST http://127.0.0.1:5000/match \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Python ML engineer"}'
```

---

## 📁 Files Created

- `backend/app.py` — Added 3 new endpoints
- `frontend/upload_dataset.html` — Beautiful upload interface
- `upload_dataset_example.py` — Python upload script
- `CSV_UPLOAD_GUIDE.md` — Full documentation

---

## 🎉 You're Ready!

Visit: **http://127.0.0.1:5000/upload_dataset_page**
