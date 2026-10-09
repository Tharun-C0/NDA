"""
scripts/verify_nda_risk.py

Terminal-Based NDA PDF Risk Assessment & Signing Verification Tool.

Analyzes an input PDF contract, segments it into legal clauses, performs multi-label
clause classification using fine-tuned transformer model checkpoints,
calculates a cumulative Document Risk Index, and provides a clear recommendation:
- SAFE TO SIGN (Low Risk)
- SIGN WITH CAUTION (Medium Risk)
- DO NOT SIGN (High Risk / Requires Legal Revision)

Usage:
    # Legacy mode (EXP-03 checkpoint):
    python scripts/verify_nda_risk.py --pdf path/to/document.pdf

    # Parity mode (Reuses backend services with legal_roberta):
    python scripts/verify_nda_risk.py --pdf path/to/document.pdf --model_choice legal_roberta --parity
"""

import argparse
import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Ensure stdout is unbuffered and UTF-8 encoded for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF is required. Install with: pip install PyMuPDF")

try:
    from preprocessing.clause_segmenter_v3 import ImprovedSegmenterV3
    from preprocessing.pdf_extractor import extract_text_from_pdf
except ImportError:
    ImprovedSegmenterV3 = None

# Approved 14 taxonomy categories
APPROVED_CATEGORIES = [
    "Party Identification",
    "Purpose",
    "NDA Type",
    "Definition of Confidential Information",
    "Confidentiality Obligations",
    "Authorized Disclosure",
    "Non-Confidential Information",
    "Liability for Damages",
    "Competition Rights",
    "Term and Termination",
    "Intellectual Property",
    "Employees",
    "Governing Law and Jurisdiction",
    "Additional Information",
]

# Risk weights for legacy calculating Document Risk Index (0-100%)
CATEGORY_RISK_WEIGHTS = {
    "Liability for Damages": 35,
    "Competition Rights": 35,
    "Intellectual Property": 30,
    "Term and Termination": 25,
    "Definition of Confidential Information": 15,
    "Employees": 15,
    "Governing Law and Jurisdiction": 15,
    "Confidentiality Obligations": 5,
    "Authorized Disclosure": 0,
    "Non-Confidential Information": 0,
    "Party Identification": 0,
    "Purpose": 0,
    "NDA Type": 0,
    "Additional Information": 0,
}

RISK_TIERS = {
    "Liability for Damages": "HIGH",
    "Competition Rights": "HIGH",
    "Intellectual Property": "HIGH",
    "Term and Termination": "HIGH",
    "Definition of Confidential Information": "MEDIUM",
    "Employees": "MEDIUM",
    "Governing Law and Jurisdiction": "MEDIUM",
}


def load_model_and_tokenizer(checkpoint_path: Path):
    """Load PyTorch sequence classifier & tokenizer from checkpoint (Legacy EXP-03 mode)."""
    if not checkpoint_path.exists():
        # Fallback search for any existing checkpoint
        ckpt_root = ROOT / "data" / "classification" / "module18_results" / "checkpoints"
        available = [d for d in ckpt_root.glob("*") if d.is_dir()]
        if available:
            checkpoint_path = available[0]
            print(f"[!] Warning: Specified checkpoint not found. Falling back to: {checkpoint_path.name}")
        else:
            sys.exit(f"[X] Error: No model checkpoints found at {checkpoint_path}")

    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
    model.eval()
    return tokenizer, model


def extract_pdf_clauses(pdf_path: Path) -> Tuple[str, List[str]]:
    """Extract full text from PDF and segment into clause text strings (Legacy mode)."""
    doc = fitz.open(pdf_path)
    full_text_pages = []
    for page in doc:
        full_text_pages.append(page.get_text())
    full_text = "\n".join(full_text_pages).strip()

    if not full_text:
        return "", []

    # Use ImprovedSegmenterV3 if available
    if ImprovedSegmenterV3 is not None:
        segmenter = ImprovedSegmenterV3(min_clause_length=30)
        seg_doc = segmenter.segment(full_text, document_id=pdf_path.stem)
        clauses = [c.text.strip() for c in seg_doc.clauses if c.segment_type == "legal_clause" and len(c.text.strip()) >= 30]
        if not clauses:
            # Fallback if no specific legal_clause identified
            clauses = [c.text.strip() for c in seg_doc.clauses if len(c.text.strip()) >= 30]
    else:
        # Fallback paragraph splitter
        paragraphs = re.split(r"\n\s*\n", full_text)
        clauses = [p.strip() for p in paragraphs if len(p.strip()) >= 30]

    return full_text, clauses


def analyze_document_legacy(pdf_path: Path, checkpoint_path: Path, threshold: float = 0.60):
    """Run legacy EXP-03 NDA risk assessment pipeline on input PDF."""
    print(f"\n================================================================================")
    print(f"            NDA AUTOMATED RISK ASSESSMENT REPORT (LEGACY EXP-03 MODE)          ")
    print(f"================================================================================")
    print(f"  Input File  : {pdf_path.name}")
    print(f"  Path        : {pdf_path}")
    print(f"  Checkpoint  : {checkpoint_path.name}")
    print(f"  Threshold   : {threshold:.2f}")

    if not pdf_path.exists():
        print(f"\n[X] Error: PDF file not found at path: {pdf_path}")
        return

    full_text, clauses = extract_pdf_clauses(pdf_path)
    if not clauses:
        print(f"\n[!] Warning: Could not extract text/clauses from {pdf_path.name}")
        return

    print(f"  Extracted   : {len(clauses)} legal clauses")
    print(f"--------------------------------------------------------------------------------")

    tokenizer, model = load_model_and_tokenizer(checkpoint_path)

    clause_results = []
    high_risk_count = 0
    medium_risk_count = 0
    detected_risk_categories = set()
    total_risk_score = 0.0

    print("\nProcessing clauses through transformer model...")
    with torch.no_grad():
        for i, clause in enumerate(clauses, 1):
            inputs = tokenizer(
                clause,
                max_length=256,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            outputs = model(**inputs)
            logits = outputs.logits.squeeze(0)
            probs = torch.sigmoid(logits).cpu().numpy()

            preds = []
            for cat_idx, prob in enumerate(probs):
                if prob >= threshold and cat_idx < len(APPROVED_CATEGORIES):
                    cat_name = APPROVED_CATEGORIES[cat_idx]
                    preds.append((cat_name, float(prob)))
                    detected_risk_categories.add(cat_name)

            # Evaluate Clause Risk
            clause_risk_level = "LOW"
            for cat_name, prob in preds:
                tier = RISK_TIERS.get(cat_name, "LOW")
                if tier == "HIGH":
                    clause_risk_level = "HIGH"
                elif tier == "MEDIUM" and clause_risk_level != "HIGH":
                    clause_risk_level = "MEDIUM"

            if clause_risk_level == "HIGH":
                high_risk_count += 1
            elif clause_risk_level == "MEDIUM":
                medium_risk_count += 1

            clause_results.append({
                "index": i,
                "text": clause,
                "predictions": preds,
                "risk_level": clause_risk_level
            })

    # Compute Document Risk Score (0-100%)
    for cat in detected_risk_categories:
        total_risk_score += CATEGORY_RISK_WEIGHTS.get(cat, 0)
    
    # Cap total score at 100%
    document_risk_pct = min(100.0, total_risk_score)

    # Determine Recommendation
    if document_risk_pct >= 65.0 or high_risk_count >= 2:
        risk_label = "HIGH RISK"
        recommendation = "DO NOT SIGN (REQUIRES LEGAL REVISION)"
        color_symbol = "[X] RED FLAG"
        advice = (
            "This NDA contains significant restrictive covenants (e.g. Liability, Non-Compete, "
            "or IP assignment). Do NOT execute this contract without prior legal counsel review."
        )
    elif document_risk_pct >= 35.0 or medium_risk_count >= 2:
        risk_label = "MEDIUM RISK"
        recommendation = "SIGN WITH CAUTION (REVIEW HIGHLIGHTED CLAUSES)"
        color_symbol = "[!] YELLOW WARNING"
        advice = (
            "This NDA contains standard confidentiality terms along with specific restrictions "
            "(e.g. broad definition of confidential information or employee non-solicitation). "
            "Carefully review the flagged clauses below."
        )
    else:
        risk_label = "LOW RISK"
        recommendation = "SAFE TO SIGN"
        color_symbol = "[+] GREEN LIGHT"
        advice = (
            "This NDA conforms to standard non-disclosure terms and poses low risk of unexpected "
            "restrictive obligations."
        )

    # Print Summary Report
    print(f"\n================================================================================")
    print(f"                            FINAL RISK SUMMARY                                  ")
    print(f"================================================================================")
    print(f"  High-Risk Clauses Found  : {high_risk_count}")
    print(f"  Medium-Risk Clauses Found: {medium_risk_count}")
    print(f"  Document Risk Index      : {document_risk_pct:.1f}%")
    print(f"  Risk Status              : {color_symbol} ({risk_label})")
    print(f"--------------------------------------------------------------------------------")
    print(f"  >>> DECISION: {recommendation} <<<")
    print(f"  Advice: {advice}")
    print(f"================================================================================\n")


def analyze_document_parity(pdf_path: Path, model_choice: str = "legal_roberta", threshold: float = 0.60):
    """Run backend-parity NDA risk assessment pipeline re-using backend services."""
    from backend.app.services.pdf_service import extract_pdf_content
    from backend.app.services.segmentation_service import segment_nda_text
    from backend.app.services.model_service import predict_clause_categories
    from backend.app.services.risk_service import evaluate_document_risk

    print(f"\n================================================================================")
    print(f"            NDA AUTOMATED RISK ASSESSMENT REPORT (PARITY MODE)                  ")
    print(f"================================================================================")
    print(f"  Input File  : {pdf_path.name}")
    print(f"  Path        : {pdf_path}")
    print(f"  Model Choice: {model_choice}")
    print(f"  Threshold   : {threshold:.2f}")

    if not pdf_path.exists():
        print(f"\n[X] Error: PDF file not found at path: {pdf_path}")
        return

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    text, pdf_result = extract_pdf_content(content=pdf_bytes, filename=pdf_path.name)
    segmented_doc = segment_nda_text(text=text, document_id=pdf_path.stem)
    clause_texts = [c.text for c in segmented_doc.clauses]

    print(f"  Page Count  : {pdf_result.page_count}")
    print(f"  Extracted   : {len(clause_texts)} total clauses")
    print(f"--------------------------------------------------------------------------------")

    print("\nRunning inference using backend model service...")
    probabilities = predict_clause_categories(
        clause_texts=clause_texts,
        model_key=model_choice,
        batch_size=16,
        max_length=256
    )

    risk_report = evaluate_document_risk(
        clauses=segmented_doc.clauses,
        probabilities=probabilities,
        threshold=threshold
    )

    high_risk_count = risk_report["high_risk_clause_count"]
    medium_risk_count = risk_report["medium_risk_clause_count"]
    total_clauses = len(risk_report["clauses"])
    low_risk_count = max(0, total_clauses - (high_risk_count + medium_risk_count))

    risk_label = risk_report["risk_status"]
    recommendation = risk_report["recommendation"]
    advice = risk_report["advice"]
    risk_index = risk_report["overall_risk_index"]

    print(f"\n================================================================================")
    print(f"                            FINAL RISK SUMMARY                                  ")
    print(f"================================================================================")
    print(f"  High-Risk Clauses Found  : {high_risk_count}")
    print(f"  Medium-Risk Clauses Found: {medium_risk_count}")
    print(f"  Low-Risk Clauses Found   : {low_risk_count}")
    print(f"  Document Risk Index      : {risk_index:.1f}%")
    print(f"  Risk Status              : {risk_label}")
    print(f"--------------------------------------------------------------------------------")
    print(f"  >>> DECISION: {recommendation} <<<")
    print(f"  Advice: {advice}")
    print(f"================================================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Terminal NDA PDF Risk Assessment & Signing Decision Tool")
    parser.add_argument("--pdf", type=str, required=True, help="Path to input NDA PDF document")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=str(ROOT / "data" / "classification" / "module18_results" / "checkpoints" / "EXP-03"),
        help="Path to fine-tuned transformer model checkpoint directory (Legacy mode)"
    )
    parser.add_argument(
        "--model_choice",
        type=str,
        default="exp03",
        choices=["legal_roberta", "legal_bert", "deberta_v3", "exp03"],
        help="Model choice key for backend parity execution (default: exp03)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.60,
        help="Probability threshold for multi-label classification (default: 0.60)"
    )
    parser.add_argument(
        "--parity",
        action="store_true",
        help="Run terminal evaluation in full backend parity mode (re-using backend services)"
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()

    if args.parity:
        # Determine model choice
        m_choice = args.model_choice if args.model_choice != "exp03" else "legal_roberta"
        analyze_document_parity(pdf_path, model_choice=m_choice, threshold=args.threshold)
    else:
        checkpoint_path = Path(args.checkpoint).resolve()
        analyze_document_legacy(pdf_path, checkpoint_path, threshold=args.threshold)


if __name__ == "__main__":
    main()
