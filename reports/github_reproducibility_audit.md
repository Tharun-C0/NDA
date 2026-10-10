# GitHub Reproducibility & Deployment Audit Report

**Date**: October 9, 2026  
**Project**: NDA Multi-Label Clause Classification & Risk Assessment Architecture  
**Repository**: `https://github.com/Tharun-C0/NDA.git`  
**Current Branch**: `main` (Up to date with `origin/main`)  
**Target Deployment Platform**: Amazon EC2 / Fresh Host Machine  

---

## 1. Executive Summary

This audit evaluates the GitHub repository reproducibility of the NDA Analysis project. The goal is to ensure that a fresh computer or Amazon EC2 instance can clone the repository, install dependencies, fetch the fine-tuned **Legal-RoBERTa** model directly from Hugging Face Hub (`THARUNC0/legal-roberta-nda-clause-classifier`), and run full multi-label clause inference without local retraining or local model checkpoints.

---

## 2. Git Repository & Tracking Status

### Repository Metadata
- **Remote Origin**: `https://github.com/Tharun-C0/NDA.git`
- **Active Branch**: `main`
- **Git Status**: Clean baseline with untracked export/audit artifacts (`artifacts/`, `reports/*.md`).

### Tracked vs Untracked Asset Breakdown

| Asset Category | Location | Tracking Status | Notes / Recommendation |
| :--- | :--- | :---: | :--- |
| **Backend API Source** | `backend/app/` | **Tracked** | Fully committed to Git. |
| **Frontend App Source** | `frontend/` & `app/` | **Tracked** | Fully committed to Git. |
| **Pipeline Scripts** | `scripts/` | **Tracked** | All training and dataset generation scripts tracked. |
| **Benchmark Datasets** | `data/classification/module16_benchmark/` | **Tracked** | Train, val, and test splits (CSV) are tracked. |
| **Synthetic Dataset** | `nda_clause_dataset_5000.csv` | **Tracked** | 5,000 synthetic training clauses tracked in Git root. |
| **Project Configs** | `configs/` | **Tracked** | `config.yaml` & `experiments_config.json` tracked. |
| **Dependencies** | `requirements.txt` & `backend/requirements.txt` | **Tracked** | Root and backend requirements tracked. |
| **Environment File** | `.env` | **Ignored (`.gitignore`)** | Local secrets excluded safely from Git. |
| **Local Checkpoints** | `experiments/.../best_checkpoint/` | **Ignored (`*.safetensors`)** | Heavy model weights excluded from Git. |
| **Local Model Export** | `artifacts/legal_roberta_nda/` | **Untracked** | Portable HF export folder on local disk. |
| **Audit Reports** | `reports/` | **Partially Tracked** | New HF audit reports are untracked. |

---

## 3. `.gitignore` Audit & Rule Verification

The existing `.gitignore` contains the following active rules:

```gitignore
# Environment files
.env
*.env

# Python cache & artifacts
__pycache__/
*.pyc
.pytest_cache/

# Virtual environment
venv/
env/
ENV/

# Large model weights and checkpoints
*.safetensors
*.bin
*.pt
*.pth

# Logs and OS files
*.log
.DS_Store

# Application runtime storage and database
/storage/
*.db
*.sqlite
```

### `.gitignore` Evaluation
- **Correctly Excluded**: Heavy model weights (`*.safetensors`, `*.bin`, `*.pt`), local environment files (`.env`), Python bytecode (`__pycache__/`), and runtime database files (`/storage/`, `*.db`).
- **Files Incorrectly Excluded**: None. All core code, configurations, and evaluation benchmarks are tracked.
- **Security Check**: `.env` and tokens are strictly excluded from Git commits.

---

## 4. Codebase Path Portability Audit

### Absolute Path Findings
1. **Source Code (`backend/app/`, `scripts/`)**:
   - Uses relative path resolution via `Path(__file__).resolve().parents[...]`.
   - **Status**: **Portable across OS platforms and cloud instances**.
2. **Generated Scratch Logs & Artifact Metadata**:
   - Some local test outputs (`validation_summary.json`) contain local Windows paths (`F:\NDA\...`).
   - **Fix Recommendation**: Ensure runtime services write dynamic logs using relative paths or environment variables (`PROJECT_ROOT`).

---

## 5. Model Loading & Hugging Face Integration Audit

### Current Model Service Loading (`backend/app/services/model_service.py`)

Currently, `model_service.py` is configured with local filesystem fallbacks:

```python
CHECKPOINT_MAP = {
    "legal_roberta": ROOT / "experiments" / "EXP-12_model_comparison" / "legal_roberta" / "best_checkpoint",
    ...
}
```

### Required Modification for Fresh Computer / EC2 Deployment

To enable instant inference on a fresh EC2 instance without downloading local checkpoint files, update `model_service.py` to fetch from Hugging Face Hub when `HF_MODEL_ID` is set or local path is absent:

```python
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

HF_MODEL_ID = os.environ.get("HF_MODEL_ID", "THARUNC0/legal-roberta-nda-clause-classifier")
HF_TOKEN = os.environ.get("HF_TOKEN", None)

def load_model_and_tokenizer(model_key: str = "legal_roberta"):
    local_path = CHECKPOINT_MAP.get(model_key)
    
    # Check if local checkpoint exists; if not, pull from Hugging Face Hub
    if local_path and local_path.exists():
        model_source = local_path
    else:
        model_source = HF_MODEL_ID
        
    tokenizer = AutoTokenizer.from_pretrained(model_source, token=HF_TOKEN)
    model = AutoModelForSequenceClassification.from_pretrained(model_source, token=HF_TOKEN)
    ...
```

---

## 6. Required Environment Variables

For deployment on a fresh computer or Amazon EC2, the application requires the following environment variables (stored in `.env` or system environment):

| Environment Variable | Recommended Value | Purpose |
| :--- | :--- | :--- |
| `HF_TOKEN` | `hf_...` (User Read Token) | Authenticates with private HF repository `THARUNC0/legal-roberta-nda-clause-classifier` |
| `HF_MODEL_ID` | `THARUNC0/legal-roberta-nda-clause-classifier` | Specifies Hugging Face model repository ID |
| `PORT` | `8000` | FastAPI server listening port |
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` | Allowed frontend origins |
| `DEBUG` | `False` (for production EC2) | Disables debug mode in production |

---

## 7. Dependency Declarations Audit

The root `requirements.txt` specifies all required libraries:

- **Core ML & Inference**: `torch>=2.0.0`, `transformers>=4.30.0`, `scikit-learn>=1.3.0`, `numpy>=1.24.0`
- **FastAPI Web Service**: `fastapi>=0.100.0`, `uvicorn>=0.22.0`, `pydantic>=2.0.0`, `pydantic-settings>=2.0.0`, `httpx>=0.24.0`
- **Hugging Face Integration**: `huggingface_hub>=0.16.0`
- **Data & PDF Extraction**: `pandas>=2.0.0`, `PyMuPDF>=1.23.0`

---

## 8. Step-by-Step Deployment Protocol for Fresh Computer / Amazon EC2

To deploy and run the application on a fresh Linux/Ubuntu EC2 instance or new computer:

### Step 1: Clone Repository
```bash
git clone https://github.com/Tharun-C0/NDA.git
cd NDA
```

### Step 2: Create Python Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the project root or set environment variables:
```bash
cat << 'EOF' > .env
HF_TOKEN=your_huggingface_read_token_here
HF_MODEL_ID=THARUNC0/legal-roberta-nda-clause-classifier
APP_NAME=NDA Analyst API
DEBUG=False
PORT=8000
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF
```

### Step 4: Run FastAPI Backend Server
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Step 5: Test Multi-Label Clause Classification Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/classify" \
     -H "Content-Type: application/json" \
     -d '{"clauses": ["This Agreement shall be governed by the laws of Delaware."]}'
```

---

## 9. Reproducibility Audit Checklist

- [x] Current repository (`https://github.com/Tharun-C0/NDA.git`) and branch (`main`) verified.
- [x] `.gitignore` inspected; confirms model weights (`*.safetensors`) and `.env` are safely excluded.
- [x] Tracked vs untracked assets analyzed; all core code and datasets are committed.
- [x] Codebase path portability verified (uses `Path(__file__).resolve()`).
- [x] Required environment variables identified (`HF_TOKEN`, `HF_MODEL_ID`).
- [x] Hugging Face remote model loading mechanism designed for `model_service.py`.
- [x] End-to-end EC2 / fresh machine setup instructions documented.

---
*End of Reproducibility Audit Report.*
