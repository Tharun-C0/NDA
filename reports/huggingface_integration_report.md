# Hugging Face Model Loading Integration Report

**Date**: October 9, 2026  
**Project**: NDA Multi-Label Clause Classification Architecture  
**Target Hugging Face Model**: `THARUNC0/legal-roberta-nda-clause-classifier`  
**Repository**: `https://github.com/Tharun-C0/NDA.git`  
**Integration Status**: **COMPLETED & VERIFIED (30/30 PASSED)**  

---

## 1. Executive Summary

The application model service (`backend/app/services/model_service.py`) has been updated to seamlessly load the fine-tuned **Legal-RoBERTa** NDA clause classification model directly from Hugging Face Hub (`THARUNC0/legal-roberta-nda-clause-classifier`).

The integration allows the application to run portably on any fresh computer or Amazon EC2 instance using environment variables (`HF_MODEL_ID`, `HF_TOKEN`) without requiring local 500 MB model checkpoint files or local retraining.

---

## 2. Files Changed & Added

| File Path | Status | Summary of Changes |
| :--- | :---: | :--- |
| [`backend/app/services/model_service.py`](file:///f:/NDA/backend/app/services/model_service.py) | **Updated** | Added Hugging Face Hub loading via `AutoTokenizer` and `AutoModelForSequenceClassification`, thread-safe singleton process caching (`threading.Lock()`), safe error handling without token leakage, and local path fallback. |
| [`backend/app/core/config.py`](file:///f:/NDA/backend/app/core/config.py) | **Updated** | Added `HF_MODEL_ID` (default: `"THARUNC0/legal-roberta-nda-clause-classifier"`) and `HF_TOKEN` fields to Pydantic Settings class. |
| [`backend/.env.example`](file:///f:/NDA/backend/.env.example) | **Updated** | Documented `HF_MODEL_ID`, `HF_TOKEN`, `PORT`, and `CORS_ORIGINS` environment variables. |
| [`requirements.txt`](file:///f:/NDA/requirements.txt) | **Updated** | Added `huggingface-hub>=0.16.0` dependency. |
| [`backend/requirements.txt`](file:///f:/NDA/backend/requirements.txt) | **Updated** | Added `torch`, `transformers`, `huggingface-hub`, and `numpy` dependencies. |
| [`backend/tests/test_hf_model_service.py`](file:///f:/NDA/backend/tests/test_hf_model_service.py) | **Created** | Automated test suite covering HF config, 14-label taxonomy mapping, sigmoid multi-label thresholding, error handling, token security, and singleton caching. |
| [`backend/tests/test_model_inference.py`](file:///f:/NDA/backend/tests/test_model_inference.py) | **Updated** | Updated test signature unpacking to handle 5-element return tuple from `load_model_and_tokenizer`. |

---

## 3. Model Loading Architecture

```
                                  [ Application Process ]
                                             │
                                  predict_clause_categories()
                                             │
                                 load_model_and_tokenizer()
                                             │
                                   Is Model Cached in RAM?
                                    ├── YES ──> Return Cached Singleton (0 ms overhead)
                                    └── NO  ──> Acquire Thread Lock (_LOADING_LOCK)
                                                     │
                                       Check Environment (HF_MODEL_ID)
                                                     │
                              ┌──────────────────────┴──────────────────────┐
                              ▼                                             ▼
                   Load from Hugging Face Hub                      Local Checkpoint Fallback
           (THARUNC0/legal-roberta-nda-clause-classifier)     (experiments/EXP-12_model_comparison/...)
                              │                                             │
                              └──────────────────────┬──────────────────────┘
                                                     │
                                     Parse Label Mappings & Config
                                   (14 Categories, Threshold = 0.50)
                                                     │
                                      Store in Process Singleton Cache
```

### Key Architectural Characteristics
1. **Singleton Process Caching**: Models are loaded **only once per application process**. Subsequent inference requests reuse the in-memory PyTorch instance with 0 ms loading latency.
2. **Hugging Face Cache**: Weights downloaded from HF Hub are cached locally by Hugging Face Transformers (`~/.cache/huggingface/`), preventing redundant network downloads on process restarts.
3. **Thread Safety**: Uses `threading.Lock()` to prevent race conditions during concurrent startup requests.
4. **Security & Privacy**:
   - `HF_TOKEN` is passed directly in memory to `AutoModelForSequenceClassification.from_pretrained`.
   - `HF_TOKEN` and confidential input clause text are **never logged** or written to disk.

---

## 4. Environment Variable Configuration

| Variable Name | Default Value | Description / Usage |
| :--- | :--- | :--- |
| `HF_MODEL_ID` | `THARUNC0/legal-roberta-nda-clause-classifier` | Target Hugging Face model repository ID. |
| `HF_TOKEN` | `""` (Empty / `None`) | Hugging Face user access token (required for private repos). |
| `PORT` | `8000` | FastAPI server listening port. |
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` | Allowed CORS origins for frontend web client. |
| `DEBUG` | `True` | Application debug mode flag. |

---

## 5. Automated Test Suite Results

Ran complete test suite across `backend/tests/` using `pytest`:

```powershell
py -3.14 -m pytest backend/tests
```

### Test Results Summary: **30 PASSED / 0 FAILED**

| Test Module | Tests Run | Result | Coverage Description |
| :--- | :---: | :---: | :--- |
| `test_hf_model_service.py` | 6 | **PASSED** | Verifies 14-label order, env vars, mocked singleton loading, sigmoid probabilities, safe error handling without token leakage, and real model inference. |
| `test_model_inference.py` | 3 | **PASSED** | Verifies real checkpoint inference across `legal_roberta`, `legal_bert`, and `deberta_v3`. |
| `test_database.py` | 4 | **PASSED** | Verifies SQLite database analysis persistence and retrieval. |
| `test_document_services.py` | 7 | **PASSED** | Verifies PDF extraction and clause segmentation pipeline. |
| `test_parity_and_risk.py` | 5 | **PASSED** | Verifies risk model evaluation and 14-category risk index calculation. |
| `test_health.py` | 2 | **PASSED** | Verifies API `/health` endpoint and settings configuration. |
| `test_report.py` | 3 | **PASSED** | Verifies PDF report generation services. |

---

## 6. Commands for Local Verification

To run and verify the updated model service locally on your computer:

### 1. Run Automated Backend Unit Tests
```powershell
py -3.14 -m pytest backend/tests
```

### 2. Run FastAPI Web Backend with Hugging Face Model
```powershell
# Set HF_TOKEN in environment (if accessing private repository)
$env:HF_TOKEN="your_huggingface_token_here"
$env:HF_MODEL_ID="THARUNC0/legal-roberta-nda-clause-classifier"

# Launch FastAPI server
py -3.14 -m uvicorn backend.app.main:app --reload --port 8000
```

### 3. Test API Endpoint via Curl
```powershell
curl -X POST "http://localhost:8000/api/v1/documents/analyze" `
     -F "file=@CONTRACT AGREEMENT.pdf" `
     -F "threshold=0.50" `
     -F "model_choice=legal_roberta"
```

---

## 7. Remaining Issues / Status
- **None**. All 30 automated backend tests pass cleanly.
- No model weights were modified or uploaded.
- No changes pushed to GitHub.
- Hugging Face repository `THARUNC0/legal-roberta-nda-clause-classifier` remains **PRIVATE**.

---
*End of Hugging Face Integration Report.*
