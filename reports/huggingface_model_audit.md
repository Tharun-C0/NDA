# Hugging Face Model Audit Report: EXP-12 Legal-RoBERTa

**Date**: October 9, 2026  
**Project**: NDA Multi-Label Clause Classification Architecture  
**Experiment**: EXP-12 Model Comparison (`Legal-RoBERTa` vs `Legal-BERT` vs `DeBERTa-v3`)  
**Target Model**: `Legal-RoBERTa` Baseline (`saibo/legal-roberta-base` fine-tuned)  

---

## 1. Executive Summary

This audit assesses the readiness of the fine-tuned **Legal-RoBERTa** model checkpoint from **EXP-12** for publishing on the Hugging Face Hub. The audit verifies checkpoint file integrity, model architecture specs, label mappings, evaluation decision threshold, and non-retrained local inference.

---

## 2. Checkpoint Location & File Inventory

### Exact Checkpoint Directory
`f:\NDA\experiments\EXP-12_model_comparison\legal_roberta\best_checkpoint`

### Files Found & Sizes
| File Name | File Size (Bytes) | Human Readable Size | Purpose / Contents |
| :--- | :---: | :---: | :--- |
| `model.safetensors` | 498,649,736 B | ~498.65 MB | Model weights (Safetensors format, 124.66M parameters) |
| `tokenizer.json` | 3,558,907 B | ~3.56 MB | Fast Tokenizer vocabulary & merge tables |
| `config.json` | 1,461 B | ~1.46 KB | Transformer model architecture & label configuration |
| `tokenizer_config.json` | 405 B | ~0.41 KB | Tokenizer settings and special token mappings |

### Total Checkpoint Size
- **Total Bytes**: 502,210,509 bytes  
- **Total Size**: **502.21 MB** (~478.94 MiB)

---

## 3. Model Architecture & Classification Head

- **Base Model**: `saibo/legal-roberta-base`
- **Architecture Class**: `RobertaForSequenceClassification`
- **Model Type**: `roberta`
- **Total Parameters**: **124,656,398** (~124.66 Million parameters)
- **Hidden Size**: 768
- **Attention Heads**: 12
- **Hidden Layers**: 12
- **Max Sequence Length**: 256
- **Problem Type**: `multi_label_classification`
- **Classification Head**: Dense projection layer (`768 -> 14`), outputting 14 independent binary logits per clause.

---

## 4. Output Labels & Label Mapping Assessment

### Number of Output Labels
**14 distinct NDA clause categories**

### Current Label Mapping State in `config.json`
> [!WARNING]
> In `experiments/EXP-12_model_comparison/legal_roberta/best_checkpoint/config.json`, the `id2label` mapping is currently saved with generic default placeholders:
> ```json
> "id2label": {
>   "0": "LABEL_0",
>   "1": "LABEL_1",
>   ...
>   "13": "LABEL_13"
> }
> ```

### Authoritative Category Index Mapping
The exact order of the 14 NDA clause categories as trained in EXP-12 (from `scripts/train_exp12_model_comparison.py` and `test_metrics.json`) is:

| Index | Category Name | Column Name |
| :---: | :--- | :--- |
| 0 | Party Identification | `label_party_identification` |
| 1 | Purpose | `label_purpose` |
| 2 | NDA Type | `label_nda_type` |
| 3 | Definition of Confidential Information | `label_definition_of_confidential_information` |
| 4 | Confidentiality Obligations | `label_confidentiality_obligations` |
| 5 | Authorized Disclosure | `label_authorized_disclosure` |
| 6 | Non-Confidential Information | `label_non-confidential_information` |
| 7 | Liability for Damages | `label_liability_for_damages` |
| 8 | Competition Rights | `label_competition_rights` |
| 9 | Term and Termination | `label_term_and_termination` |
| 10 | Intellectual Property | `label_intellectual_property` |
| 11 | Employees | `label_employees` |
| 12 | Governing Law and Jurisdiction | `label_governing_law_and_jurisdiction` |
| 13 | Additional Information | `label_additional_information` |

---

## 5. Classification Threshold Configuration

- **Optimal Decision Threshold**: **`0.50`**
- **Derivation Method**: Empirically selected via validation set Macro F1 sweep (`0.30` to `0.70`).
- **Validation Macro F1 Peak at 0.50**: `0.5736`
- **Test Set Macro F1 at 0.50**: `0.4457` (Test Micro F1: `0.5389`, Weighted F1: `0.5366`)
- **Source Verification**: Recorded in `test_metrics.json` (`"selected_threshold": 0.5`) and `threshold_sweep_results.csv`.

---

## 6. Local Checkpoint Loading & Verification

The checkpoint was loaded into Python using Hugging Face `transformers` without downloading remote weights or retraining:

```python
tokenizer = AutoTokenizer.from_pretrained("experiments/EXP-12_model_comparison/legal_roberta/best_checkpoint")
model = AutoModelForSequenceClassification.from_pretrained("experiments/EXP-12_model_comparison/legal_roberta/best_checkpoint")
```

**Verification Status**: **PASSED (100% Offline Load Success)**

---

## 7. Inference Test Results

### Test Input 1: Governing Law Clause
**Sample Text**:
> *"This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of laws principles."*

**Inference Scores & Predictions (Threshold = 0.50)**:
| Index | Category Name | Raw Sigmoid Score | Met Threshold (>= 0.50) | Prediction |
| :---: | :--- | :---: | :---: | :---: |
| 0 | Party Identification | 0.0574 | False | |
| 1 | Purpose | 0.0652 | False | |
| 2 | NDA Type | 0.0446 | False | |
| 3 | Definition of Confidential Information | 0.0525 | False | |
| 4 | Confidentiality Obligations | 0.0481 | False | |
| 5 | Authorized Disclosure | 0.0540 | False | |
| 6 | Non-Confidential Information | 0.0587 | False | |
| 7 | Liability for Damages | 0.0574 | False | |
| 8 | Competition Rights | 0.0525 | False | |
| 9 | Term and Termination | 0.0533 | False | |
| 10 | Intellectual Property | 0.0549 | False | |
| 11 | Employees | 0.0394 | False | |
| **12** | **Governing Law and Jurisdiction** | **0.9896** | **True** | **[MATCH]** |
| 13 | Additional Information | 0.1054 | False | |

**Predicted Category**: `['Governing Law and Jurisdiction']` (Confidence: **98.96%**)

---

### Test Input 2: Confidential Information Definition Clause
**Sample Text**:
> *"Confidential Information means all non-public information disclosed by Disclosing Party to Receiving Party, including trade secrets, proprietary software code, and customer lists."*

**Predicted Category**: `['Definition of Confidential Information']` (Confidence: **98.12%**)

---

## 8. Missing Files & Identified Deficiencies

Before pushing to Hugging Face Hub, the following 3 items should be resolved:

1. **Generic `id2label` / `label2id` in `config.json`**:
   - *Problem*: HF Inference API and pipeline widgets will output `"LABEL_12"` instead of `"Governing Law and Jurisdiction"`.
   - *Fix*: Replace `LABEL_0`..`LABEL_13` strings in `config.json` with the actual category names prior to upload.

2. **Missing `README.md` (Model Card)**:
   - *Problem*: Missing documentation of model performance, training data, license, and usage instructions on Hugging Face Hub.
   - *Fix*: Generate a standard Hugging Face model card detailing EXP-12 results, test set F1 scores, decision threshold (`0.50`), and dataset size (5,344 combined training clauses).

3. **Explicit Decision Threshold Documentation**:
   - *Problem*: Hugging Face multi-label pipeline uses default `0.50` threshold, but documenting this explicitly in model card or config prevents user misconfiguration.

---

## 9. Recommended Upload Workflow & Directory Structure

Create a clean export directory at `models/huggingface_export/legal_roberta_nda` containing:

```
models/huggingface_export/legal_roberta_nda/
├── config.json               # Updated with proper id2label / label2id mapping
├── model.safetensors         # Copied from best_checkpoint (498.65 MB)
├── tokenizer.json            # Copied from best_checkpoint
├── tokenizer_config.json     # Copied from best_checkpoint
├── special_tokens_map.json   # Standard special tokens mapping
└── README.md                 # Complete Model Card for Hugging Face Hub
```

---

## 10. Audit Checklist Summary

- [x] EXP-12 model comparison directory inspected (`experiments/EXP-12_model_comparison`).
- [x] Fine-tuned Legal-RoBERTa model checkpoint located (`.../legal_roberta/best_checkpoint`).
- [x] Checkpoint contains weights (`model.safetensors`), config, tokenizer files, and 14-label classification head.
- [x] Exact model directory identified for Hugging Face Transformers loading.
- [x] Label mapping investigated (found generic `LABEL_0`..`LABEL_13` in `config.json`, needing update).
- [x] Classification threshold confirmed from experiment evaluation results (`0.50`).
- [x] Model successfully loaded offline without retraining or remote downloads.
- [x] Small inference test executed; predicted categories verified (`Governing Law and Jurisdiction` @ 98.96%).
- [x] Suitability for Hugging Face Hub confirmed with recommendations.
- [x] Audit report created at `reports/huggingface_model_audit.md`.

---
*End of Audit Report.*
