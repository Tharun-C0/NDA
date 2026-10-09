# NDA Analysis & Risk Assessment Framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-Transformers-yellow.svg)](https://huggingface.co/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A Two-Stage Architecture for Non-Disclosure Agreement (NDA) Analysis: LLM-based Clause Segmentation and Multi-Label Transformer Classification**

This repository contains a full legal contract intelligence framework designed to process, segment, classify, and risk-assess Non-Disclosure Agreements (NDAs). It features a multi-label clause classification pipeline across 14 legal categories, trained on genuine benchmark splits and augmented with a 5,000-clause dataset (`nda_clause_dataset_5000.csv`).

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Project Architecture](#-project-architecture)
- [14 Approved NDA Legal Categories](#-14-approved-nda-legal-categories)
- [Implementation Roadmap & Module Status](#-implementation-roadmap--module-status)
- [Experimental Matrix (EXP-01 to EXP-12)](#-experimental-matrix-exp-01-to-exp-12)
- [Empirical Results & Benchmark Performance Scorecard](#-empirical-results--benchmark-performance-scorecard)
- [Quick Start & Installation](#-quick-start--installation)
- [Usage Guide](#-usage-guide)
  - [1. Dataset Validation](#1-dataset-validation)
  - [2. Model Training](#2-model-training)
  - [3. Automated NDA Risk Assessment CLI](#3-automated-nda-risk-assessment-cli)
- [Research Design & Key Findings](#-research-design--key-findings)
- [Citation & License](#-citation--license)

---

## ✨ Key Features

- **Document-Disjoint Splitting**: Strictly enforces 0 document overlap between Train, Validation, and Test sets to eliminate data leakage.
- **14-Category Multi-Label Legal Classification**: Handles overlapping legal clauses (e.g., a clause containing both *Confidentiality Obligations* and *Authorized Disclosure*).
- **Dataset Augmentation & Scaling**: Integrates `nda_clause_dataset_5000.csv` (5,000 clause samples) combined with core benchmark data for high-capacity transformer training (5,344 total training samples).
- **Multi-Model Transformer Suite**: Evaluates `saibo/legal-roberta-base`, `nlpaueb/legal-bert-base-uncased`, and `microsoft/deberta-v3-base`.
- **Advanced Loss Functions**: Supports Standard BCE, Multi-Label Focal Loss ($\gamma=2.0, \alpha=0.25$), and Class-Weighted BCE to mitigate legal class imbalance.
- **Automated Risk Assessment CLI**: Includes `verify_nda_risk.py` to extract PDF text, segment clauses, compute category confidence, and output actionable risk recommendations (`SAFE TO SIGN`, `SIGN WITH CAUTION`, `DO NOT SIGN`).

---

## 📁 Project Architecture

```
NDA/
├── app/                        # Interactive annotation & review applications
├── configs/
│   ├── config.yaml             # Central project configuration parameters
│   └── config_loader.py        # YAML configuration parser
├── data/
│   ├── classification/
│   │   ├── module16_benchmark/ # Disjoint benchmark splits (train.csv, validation.csv, test.csv)
│   │   └── module18_results/   # Checkpoints & evaluation metrics
│   ├── processed/              # Extracted PDF texts and intermediate clause segments
│   └── raw/                    # Raw annotated NDA TXT files
├── evaluation/                 # Metrics calculators (Macro F1, Micro F1, MCC, Hamming Loss)
├── experiments/                # Model training runs (EXP-01 through EXP-12)
├── external_data/
│   └── kleister-nda/           # Raw Kleister-NDA PDF corpus
├── models/                     # Trained PyTorch transformer weights & tokenizers
├── preprocessing/              # Text extraction & clause segmentation
│   ├── clause_segmenter_v1.py  # Heuristic rule-based segmenter v1
│   ├── clause_segmenter_v2.py  # Improved boundary detector v2
│   ├── clause_segmenter_v3.py  # Fine-grained legal header & list parser v3
│   ├── dataset_loader.py       # Data loading utilities
│   └── pdf_extractor.py        # PyMuPDF (Fitz) text extraction engine
├── reports/                    # 119+ Research reports, paper tables, and scorecards
├── scratch/                    # Diagnostic scripts & dataset validators
│   ├── diagnose_deberta_nan.py # DeBERTa FP32 stability validator
│   └── validate_data.py        # Pre-flight data integrity checker
├── scripts/                    # Pipeline runners & model training scripts
│   ├── train_exp10_5000.py     # 10-Epoch dataset scaling training
│   ├── train_exp11_early_stopping.py     # Early stopping optimization
│   ├── train_exp12_model_comparison.py   # Legal-RoBERTa vs Legal-BERT vs DeBERTa-v3
│   └── verify_nda_risk.py                # Automated PDF Risk Assessment CLI
├── tests/                      # Unit and integration test suites
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
12. **Employees** — Employee obligations, solicitation restrictions, and coverage.
13. **Governing Law and Jurisdiction** — Choice of law, venue, and dispute resolution.
14. **Additional Information** — Miscellaneous provisions (severability, entire agreement, notices).

---

## 🛣️ Implementation Roadmap & Module Status

All 18 planned modules and experiment suites have been completed:

- [x] **Module 1: Project Foundation & Dataset Preparation** — Created folder architecture, configuration loader, and annotation parsers.
- [x] **Module 1b: Dataset Acquisition & Schema Auditing** — Audited Kleister-NDA corpus schema (document-level vs clause-level).
- [x] **Module 2: NDA Text Extraction & Clause Segmentation** — Built PDF text extraction and legal clause segmenters (`v1`, `v2`, `v3`).
- [x] **Module 3: Multi-Label Taxonomy & Protocol** — Standardized 14 legal categories and multi-label tagging guidelines.
- [x] **Module 4: Zero-Shot / Few-Shot LLM Pseudo-Labeling** — Integrated LLM API annotation (Gemini / OpenRouter).
- [x] **Module 5 & 5b: Pseudo-Label Quality Audit & Active Learning Log** — Audited pseudo-labels and initialized active learning tracking.
- [x] **Module 6: Dataset Cleaning & Feature Formatting** — Sanitized clause text and formatted binary multi-label matrices.
- [x] **Module 7: Baseline Classifier Setup** — Built PyTorch DataLoaders, training loops, and metric evaluation modules.
- [x] **Module 8: Active Learning Seed Selection** — Selected diverse seed subsets via length-bucket and document-spread sampling.
- [x] **Module 9: Benchmark Split & Leakage Audit** — Enforced 0 document leakage across Train, Validation, and Test sets.
- [x] **Module 10: Loss Function Engineering** — Formulated BCEWithLogits, Multi-Label Focal Loss, and Class-Weighted BCE.
- [x] **Module 11-15: Quality Gates & Benchmark Freeze** — Conducted category redundancy analysis, priority queue generation, and frozen benchmark validation.
- [x] **Module 16: Construction of 717-Clause Benchmark** — Finalized 20 disjoint documents (717 clauses) across 14 categories.
- [x] **Module 17: Active Learning Batch Evaluation** — Measured classifier performance across active learning iterations.
- [x] **Module 18: Controlled Classifier Experiment Matrix** — Trained initial matrix models (EXP-01 to EXP-09) and diagnosed FP16 stability in DeBERTa-v3.
- [x] **EXP-10: Dataset Scaling Experiment** — Trained `Legal-RoBERTa` on 5,344 clauses (344 core + 5,000 expanded dataset).
- [x] **EXP-11: Early Stopping Optimization** — Implemented early stopping (Patience = 2) monitoring Validation Macro F1.
- [x] **EXP-12: Multi-Model Benchmark Comparison** — Evaluated `Legal-RoBERTa`, `Legal-BERT`, and `DeBERTa-v3` on the augmented 5,344-clause dataset.

---

## 🧪 Experimental Matrix (EXP-01 to EXP-12)

| Experiment ID | Architecture | Loss Function | Training Set | Status |
|---|---|---|---|---|
| **EXP-01** | `saibo/legal-roberta-base` | BCEWithLogitsLoss | 344 Core Clauses | Completed |
| **EXP-02** | `saibo/legal-roberta-base` | Multi-Label Focal Loss | 344 Core Clauses | Completed |
| **EXP-03** | `saibo/legal-roberta-base` | Class-Weighted BCE | 344 Core Clauses | Completed |
| **EXP-04** | `nlpaueb/legal-bert-base-uncased` | BCEWithLogitsLoss | 344 Core Clauses | Completed |
| **EXP-05** | `nlpaueb/legal-bert-base-uncased` | Multi-Label Focal Loss | 344 Core Clauses | Completed |
| **EXP-06** | `nlpaueb/legal-bert-base-uncased` | Class-Weighted BCE | 344 Core Clauses | Completed |
| **EXP-07** | `microsoft/deberta-v3-base` | BCEWithLogitsLoss | 344 Core Clauses | Completed (FP32) |
| **EXP-08** | `microsoft/deberta-v3-base` | Multi-Label Focal Loss | 344 Core Clauses | Completed (FP32) |
| **EXP-09** | `microsoft/deberta-v3-base` | Class-Weighted BCE | 344 Core Clauses | Completed (FP32) |
| **EXP-10** | `saibo/legal-roberta-base` | Class-Weighted BCE | 5,344 (344 + 5,000 Expanded) | Completed (10 Epochs) |
| **EXP-11** | `saibo/legal-roberta-base` | Class-Weighted BCE | 5,344 (344 + 5,000 Expanded) | Completed (Early Stop) |
| **EXP-12** | Model Comparison (RoBERTa / BERT / DeBERTa) | Class-Weighted BCE | 5,344 (344 + 5,000 Expanded) | Completed |

---

## 📊 Empirical Results & Benchmark Performance Scorecard

### 1. Dataset Augmentation Impact (EXP-03 vs EXP-10)

Adding **5,000 NDA clauses** (`nda_clause_dataset_5000.csv`) to the initial training split increased the total training dataset from **344 to 5,344 clauses**. Evaluated on the **100% frozen, untouched test split** (236 clauses), dataset augmentation yielded significant performance gains across all major classification metrics:

| Classification Metric | Baseline EXP-03 (344 Clauses) | Augmented EXP-10 (5,344 Clauses) | Absolute Gain | Relative Improvement |
| :--- | :---: | :---: | :---: | :---: |
| **Macro F1** | `0.4295` | **`0.4643`** | `+0.0348` | **`+8.10%`** |
| **Micro F1** | `0.4940` | **`0.5543`** | `+0.0603` | **`+12.21%`** |
| **Weighted F1** | `0.5151` | **`0.5568`** | `+0.0417` | **`+8.10%`** |
| **Hamming Loss** | `0.1283` | **`0.1081`** | `-0.0202` | **`-15.74%` (Error Reduction)** |
| **Matthews Correlation (MCC)** | `0.3885` | **`0.4118`** | `+0.0233` | **`+6.00%`** |

#### Key Category-Specific Gains with Dataset Expansion:
- **Authorized Disclosure F1**: Increased from `0.3404` to **`0.6286`** (**+84.7%** gain)
- **Term & Termination F1**: Increased from `0.4524` to **`0.5714`** (**+26.3%** gain)
- **Intellectual Property F1**: Increased from `0.5714` to **`0.6667`** (**+16.7%** gain)
- **Liability for Damages F1**: Increased from `0.5957` to **`0.6667`** (**+11.9%** gain)
- **Party Identification F1**: Increased from `0.4318` to **`0.4950`** (**+14.6%** gain)

---

### 2. Multi-Model Architecture Comparison (EXP-12)

Evaluating three transformer architectures under identical training configurations (Class-Weighted BCE loss, 5,344 training clauses, Early Stopping patience=2):

| Model Architecture | Best Val Macro F1 | Optimal Threshold | Test Macro F1 | Test Micro F1 | Test Weighted F1 | Minority F1 | Hamming Loss | MCC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`saibo/legal-roberta-base`** | `0.5589` | `0.50` | **`0.4457`** | `0.5389` | `0.5366` | **`0.3574`** | `0.1077` | `0.3884` |
| **`nlpaueb/legal-bert-base-uncased`** | `0.5545` | `0.55` | `0.4443` | **`0.5597`** | **`0.5537`** | `0.3382` | **`0.1038`** | `0.3938` |
| **`microsoft/deberta-v3-base`** | `0.5588` | `0.60` | `0.4404` | `0.5252` | `0.5382` | `0.3377` | `0.1111` | **`0.3954`** |

---

### 3. Per-Category 14-Label F1 Score Breakdown (EXP-12)

| Legal Clause Category | Legal-RoBERTa | Legal-BERT | DeBERTa-v3 | Winning Architecture |
| :--- | :---: | :---: | :---: | :---: |
| **Party Identification** | `0.4375` | **`0.4419`** | `0.3908` | `Legal-BERT` |
| **Purpose** | **`0.1905`** | `0.0000` | **`0.1905`** | `Legal-RoBERTa / DeBERTa-v3` |
| **NDA Type** | `0.0000` | `0.0000` | `0.0000` | `Baseline` |
| **Definition of Confidential Information** | `0.3871` | **`0.4737`** | `0.4242` | `Legal-BERT` |
| **Confidentiality Obligations** | `0.4762` | **`0.5614`** | `0.5385` | `Legal-BERT` |
| **Authorized Disclosure** | **`0.6250`** | `0.6000` | `0.5625` | `Legal-RoBERTa` |
| **Non-Confidential Information** | `0.0000` | `0.0000` | `0.0000` | `Baseline` |
| **Liability for Damages** | **`0.6286`** | `0.6000` | `0.4179` | `Legal-RoBERTa` |
| **Competition Rights** | `0.5660` | **`0.5882`** | `0.5357` | `Legal-BERT` |
| **Term and Termination** | `0.5714` | `0.6076` | **`0.6197`** | `DeBERTa-v3` |
| **Intellectual Property** | `0.6897` | `0.6429` | **`0.7143`** | `DeBERTa-v3` |
| **Employees** | `0.5152` | `0.4941` | **`0.5455`** | `DeBERTa-v3` |
| **Governing Law and Jurisdiction** | `0.5455` | `0.5714` | **`0.6000`** | `DeBERTa-v3` |
| **Additional Information** | `0.6070` | **`0.6394`** | `0.6256` | `Legal-BERT` |

---

## 🚀 Quick Start & Installation

### Prerequisites

- Python 3.10 or higher
- NVIDIA GPU with CUDA support (recommended for training)

### Setup Virtual Environment

```bash
# Clone the repository
git clone https://github.com/Tharun-C0/NDA.git
cd NDA

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Windows
# source venv/bin/activate     # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

---

## 💻 Usage Guide

### 1. Dataset Validation

Run the dataset integrity check to verify split alignment, row counts, label distribution, and dataset loading:

```bash
python scratch/validate_data.py
```

*Output:*
```
=======================================================
         DATA VALIDATION & PRE-FLIGHT REPORT          
=======================================================
[CHECK 1 PASS] Clause dataset has exactly 5,000 rows.
[CHECK 2 PASS] All 14 labels exist in clause dataset.
[CHECK 3 PASS] No invalid labels (all binary 0 or 1).
[CHECK 4 PASS] No empty clause text.
[CHECK 5 PASS] No duplicate clause IDs.
[CHECK 6 PASS] No duplicate clause text within dataset.
[CHECK 7 PASS] Label columns match the existing benchmark.
[CHECK 8 PASS] Training, validation, and test schemas match perfectly.
[CHECK 9 PASS] Clause data is NOT present in validation set (0 overlap).
[CHECK 9 PASS] Clause data is NOT present in test set (0 overlap).
```

### 2. Model Training

Run the multi-model comparison training pipeline (EXP-12):

```bash
python scripts/train_exp12_model_comparison.py
```

Or run individual dataset scaling experiments:

```bash
# 10-epoch training on 5,344 clauses
python scripts/train_exp10_5000.py

# Early stopping training (patience = 2)
python scripts/train_exp11_early_stopping.py
```

### 3. Automated NDA Risk Assessment CLI

To assess risk levels and extract categories from any NDA PDF contract:

```bash
python scripts/verify_nda_risk.py --pdf "25f2299_1.pdf"
```

Or specify a custom classification threshold:

```bash
python scripts/verify_nda_risk.py --pdf "CONTRACT AGREEMENT.pdf" --threshold 0.60
```

---

## 🔬 Research Design & Key Findings

1. **Document-Disjoint Protocol**: Splitting data at the clause level introduces severe data leakage because clauses from the same NDA share stylistic and organizational patterns. Document-disjoint partitioning ensures strict out-of-sample generalization.
2. **DeBERTa-v3 Mixed Precision Stability**: DeBERTa-v3 embeddings utilize continuous scale projections that can cause gradient underflow/overflow when combined with mixed precision (FP16) under certain loss functions. Running DeBERTa-v3 in full `torch.float32` eliminates training instability.
3. **Class-Weighted BCE for Imbalanced Legal Data**: Minority categories (such as *Competition Rights* and *Employees*) benefit significantly from positive class weighting proportional to $\frac{N_{\text{neg}}}{N_{\text{pos}}}$, preventing the model from collapsing to all-zero predictions.
4. **Dataset Scaling & Augmentation**: Augmenting human-annotated clauses with the 5,000-clause dataset (`nda_clause_dataset_5000.csv`) improves representation of rare legal phrasing while preserving document-disjoint evaluation integrity.

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
