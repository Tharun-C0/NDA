# NDA Analysis & Risk Assessment Framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.0+-61dafb.svg)](https://react.dev/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-Transformers-yellow.svg)](https://huggingface.co/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI-Powered Non-Disclosure Agreement (NDA) Analysis & Legal Risk Assessment System**

This repository contains an end-to-end legal tech intelligence platform designed to parse, segment, classify, and risk-assess Non-Disclosure Agreements (NDAs). It features a multi-label clause classification pipeline across 14 legal categories, trained on genuine benchmark splits and augmented with a 5,000-clause dataset (`nda_clause_dataset_5000.csv`), backed by a FastAPI REST API, SQLite analysis persistence, automated PDF report generation, and a classical legal editorial React web application.

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Project Architecture](#-project-architecture)
- [14 Approved NDA Legal Categories](#-14-approved-nda-legal-categories)
- [Classical ORM Risk Index Model](#-classical-orm-risk-index-model)
- [Experimental Matrix & Scorecard](#-experimental-matrix--scorecard)
- [Quick Start & Installation](#-quick-start--installation)
  - [1. Backend Setup (FastAPI)](#1-backend-setup-fastapi)
  - [2. Frontend Setup (React + Vite)](#2-frontend-setup-react--vite)
- [Usage Guide](#-usage-guide)
  - [1. Automated Risk Assessment CLI & Parity Mode](#1-automated-risk-assessment-cli--parity-mode)
  - [2. Model Benchmark Training](#2-model-benchmark-training)
  - [3. Running Backend Tests](#3-running-backend-tests)
- [Web Application Architecture](#-web-application-architecture)
- [Citation & License](#-citation--license)

---

## ✨ Key Features

- **Classical Legal Editorial UI**: Responsive React 19 web application inspired by parchment paper, dark walnut, roasted coffee, and antique brass styling.
- **FastAPI REST Service**: Production-grade async backend serving `/api/v1/documents/analyze`, history tracking, and downloadable PDF reports.
- **SQLite Document Analysis History**: Persists all document analysis results, clause predictions, model choices, and scores to `storage/db/nda_history.db`.
- **Classical ORM Risk Scoring**: Normalized Operational Risk Model blending Category Exposure Breadth (60%) and Clause Risk Density (40%) to yield continuous, realistic risk indices.
- **14-Category Multi-Label Transformer Classification**: Fine-tuned sequence classifiers (`Legal-RoBERTa`, `Legal-BERT`, `DeBERTa-v3`) trained on 5,344 augmented NDA clauses.
- **Terminal & API Parity**: CLI tool `scripts/verify_nda_risk.py` supports both legacy `EXP-03` evaluation and full `--parity` execution mode matching FastAPI services.
- **Automated PDF Report Generator**: Produces executive PDF risk briefs via PyMuPDF.

---

## 📁 Project Architecture

```text
NDA/
├── backend/                    # FastAPI Backend Application
│   ├── app/
│   │   ├── api/routes/         # API endpoints (document analyze, history, PDF reports, health)
│   │   ├── core/               # Configuration settings & CORS
│   │   ├── db/                 # SQLite database persistence adapter
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── services/           # PDF text extractor, segmenter, transformer inference, risk engine & report generator
│   └── tests/                  # Pytest unit & integration test suites
├── frontend/                   # Classical Legal Editorial React 19 Web App
│   ├── src/
│   │   ├── components/         # Header, BottomNav, LegalSeal, RiskMeter, ClauseCard, CategoryAccordion, HistoryModal
│   │   ├── pages/              # UploadNDA, ProcessingScreen, ContractAudit, ClauseAnalysis, CategoriesOverview, ExportReport
│   │   ├── services/           # Centralized API fetch client (api.js)
│   │   └── index.css           # Parchment design tokens & print stylesheets
│   ├── public/                 # Static web assets & sample NDA contracts
│   └── package.json            # Node.js dependencies (Vite, React 19, Lucide React)
├── data/                       # Benchmark datasets, Splits & Module 18 Checkpoints
├── experiments/                # Fine-tuned model checkpoints (Legal-RoBERTa, Legal-BERT, DeBERTa-v3)
├── models/                     # Base transformer weights & tokenizers
├── preprocessing/              # Clause segmenter v3, text parsers & dataset loaders
├── reports/                    # Benchmark metrics & research scorecards
├── scripts/                    # Training runners & terminal verification tools
│   ├── verify_nda_risk.py      # Terminal Risk Assessment CLI with --parity mode
│   └── train_exp12_model_comparison.py
├── storage/                    # SQLite database persistence (storage/db/nda_history.db)
├── nda_clause_dataset_5000.csv # 5,000 NDA clause dataset
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🏷️ 14 Approved NDA Legal Categories

Every clause in the NDA corpus is mapped across 14 legal classes:

1. **Party Identification** — Identifies contracting entities (Disclosing & Receiving parties).
2. **Purpose** — Defines permissible scope/purpose of information sharing.
3. **NDA Type** — Classifies agreement as Mutual or Unilateral.
4. **Definition of Confidential Information** — Scope of proprietary materials covered.
5. **Confidentiality Obligations** — Duty of care, non-use, and non-disclosure standards.
6. **Authorized Disclosure** — Permitted disclosures (representatives, legal processes).
7. **Non-Confidential Information** — Exclusions (public domain, prior knowledge, independent creation).
8. **Liability for Damages** — Indemnification, remedies, and liability caps.
9. **Competition Rights** — Non-compete, non-solicit, and non-circumvention terms.
10. **Term and Termination** — Agreement duration, survival periods, and termination notice.
11. **Intellectual Property** — Ownership reservation and IP grant exclusions.
12. **Employee Obligations** — Employee obligations, solicitation restrictions, and coverage.
13. **Governing Law & Jurisdiction** — Choice of law, venue, and dispute resolution.
14. **Additional Information** — Miscellaneous provisions (severability, entire agreement, notices).

---

## ⚖️ Classical ORM Risk Index Model

The system evaluates overall contract risk using a normalized Operational Risk Model (ORM) combining two balanced factors:

1. **Category Exposure Ratio ($S_{\text{cat}}$)** *(Weight: 60%)*:
   Sums the weights of all distinct detected risk categories normalized across maximum category points ($175$):
   $$S_{\text{cat}} = \left(\frac{\sum_{\text{detected}} W_{\text{cat}}}{175}\right) \times 100$$

2. **Clause Risk Density Ratio ($D_{\text{clause}}$)** *(Weight: 40%)*:
   Measures the density of high and medium risk clauses relative to total document length:
   $$D_{\text{clause}} = \min\left(100.0,\ \frac{100 \times (N_{\text{high}} + 0.5 \times N_{\text{med}})}{N_{\text{total}}}\right)$$

3. **Composite Risk Index**:
   $$\text{Risk Index} = \left(0.60 \times S_{\text{cat}}\right) + \left(0.40 \times D_{\text{clause}}\right)$$

---

## 🚀 Quick Start & Installation

### 1. Backend Setup (FastAPI)

```bash
# Clone repository
git clone https://github.com/Tharun-C0/NDA.git
cd NDA

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Windows

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
$env:PYTHONPATH="."
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend
```
- API Documentation: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`

### 2. Frontend Setup (React + Vite)

Open a new terminal in the `frontend/` directory:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 💻 Usage Guide

### 1. Automated Risk Assessment CLI & Parity Mode

To run terminal verification in **Legacy EXP-03 mode**:
```bash
python scripts/verify_nda_risk.py --pdf "25f2299_1.pdf"
```

To run terminal verification in **Full Backend Parity mode** (re-using FastAPI services with `legal_roberta`):
```bash
python scripts/verify_nda_risk.py --pdf "25f2299_1.pdf" --model_choice legal_roberta --parity
```

### 2. Model Benchmark Training

Run the multi-model comparison training pipeline (EXP-12):
```bash
python scripts/train_exp12_model_comparison.py
```

### 3. Running Backend Tests

Run the full pytest suite (24 tests):
```bash
.\venv\Scripts\python.exe -m pytest backend/tests/
```

---

## 🖥️ Web Application Architecture

The frontend consists of 6 interactive screens:

1. **Document Deposit (`UploadNDA.jsx`)**: Drag-and-drop parchment file dropzone with PDF validation, model picker (`Legal-RoBERTa`, `Legal-BERT`, `DeBERTa-v3`), threshold slider (`0.10`–`0.90`), and sample document loader.
2. **Processing Pipeline (`ProcessingScreen.jsx`)**: 3-stage visual progress stepper tracking real API request lifecycle.
3. **Executive Risk Dashboard (`ContractAudit.jsx`)**: Circular parchment risk index meter, clause triage cards, document structural profile, and priority category cards.
4. **Interactive Legal Workbench (`ClauseAnalysis.jsx`)**: 2-pane workspace with text search, risk level filters, category dropdowns, verbatim clause display, and copy excerpt functionality.
5. **14-Category Analysis (`CategoriesOverview.jsx`)**: Expandable Roman numeral taxonomy accordions (I..XIV) showing confidence scores and detected clause lists.
6. **Executive Brief & Export (`ExportReport.jsx`)**: Direct download for PyMuPDF PDF reports, JSON metadata exporter, browser print engine with optional `CONFIDENTIAL` watermark toggle, and legal disclaimer notice.

---

## 📜 Citation & License

If you use this repository or dataset in your research, please cite:

```bibtex
@misc{nda_analysis_2026,
  author = {Tharun-C0},
  title = {A Two-Stage Architecture for NDA Analysis: LLM-based Segmentation and Transformer-based Clause Classification},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub Repository},
  howpublished = {\url{https://github.com/Tharun-C0/NDA.git}}
}
```

Distributed under the **MIT License**. See `LICENSE` for details.
