import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from preprocessing.clause_segmenter_v3 import ClauseV3
from backend.app.services.model_service import APPROVED_CATEGORIES

logger = logging.getLogger(__name__)

# Category Risk Weights for Document Risk Index
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

TOTAL_MAX_CATEGORY_WEIGHT = sum(CATEGORY_RISK_WEIGHTS.values())  # 175 points

RISK_TIERS = {
    "Liability for Damages": "HIGH",
    "Competition Rights": "HIGH",
    "Intellectual Property": "HIGH",
    "Term and Termination": "HIGH",
    "Definition of Confidential Information": "MEDIUM",
    "Employees": "MEDIUM",
    "Governing Law and Jurisdiction": "MEDIUM",
}


def assess_clause_risk(predicted_categories: List[str]) -> str:
    """Determine single clause risk level (LOW, MEDIUM, HIGH)."""
    has_high = any(RISK_TIERS.get(cat) == "HIGH" for cat in predicted_categories)
    has_medium = any(RISK_TIERS.get(cat) == "MEDIUM" for cat in predicted_categories)

    if has_high:
        return "HIGH"
    elif has_medium:
        return "MEDIUM"
    return "LOW"


def evaluate_document_risk(
    clauses: List[ClauseV3],
    probabilities: np.ndarray,
    threshold: float = 0.60,
) -> Dict[str, Any]:
    """
    Evaluate document-level risk index using a classical normalized Operational Risk Model (ORM).
    Combines Category Exposure Breadth (60%) with Clause Risk Density (40%).
    """
    detected_risk_categories = set()
    high_risk_count = 0
    medium_risk_count = 0
    
    clause_evaluations = []

    for idx, (clause, prob_vector) in enumerate(zip(clauses, probabilities)):
        preds = []
        pred_details = []
        
        for cat_idx, cat_name in enumerate(APPROVED_CATEGORIES):
            prob = float(prob_vector[cat_idx])
            if prob >= threshold:
                preds.append(cat_name)
                pred_details.append({"category": cat_name, "confidence": round(prob, 4)})
                detected_risk_categories.add(cat_name)

        c_risk_level = assess_clause_risk(preds)
        if c_risk_level == "HIGH":
            high_risk_count += 1
        elif c_risk_level == "MEDIUM":
            medium_risk_count += 1

        clause_evaluations.append({
            "clause_id": clause.clause_id,
            "text": clause.text,
            "start": clause.start,
            "end": clause.end,
            "segment_type": clause.segment_type,
            "is_suspicious": clause.is_suspicious,
            "predicted_categories": pred_details,
            "risk_level": c_risk_level,
        })

    total_clauses = max(1, len(clauses))

    # 1. Category Exposure Score (Normalized to 100%)
    category_weight_sum = sum(CATEGORY_RISK_WEIGHTS.get(cat, 0) for cat in detected_risk_categories)
    category_exposure_score = (category_weight_sum / TOTAL_MAX_CATEGORY_WEIGHT) * 100.0

    # 2. Clause Risk Density Score (Proportion of High/Medium clauses relative to total length)
    weighted_clause_score = (high_risk_count * 1.0) + (medium_risk_count * 0.5)
    clause_density_score = min(100.0, (weighted_clause_score / total_clauses) * 100.0)

    # 3. Composite Classical ORM Risk Index (60% Category Breadth + 40% Clause Density)
    composite_risk_index = (0.60 * category_exposure_score) + (0.40 * clause_density_score)
    document_risk_pct = min(100.0, max(0.0, float(composite_risk_index)))

    # Classification Tiers
    if document_risk_pct >= 55.0 or high_risk_count >= 5:
        risk_label = "HIGH RISK"
        recommendation = "DO NOT SIGN (REQUIRES LEGAL REVISION)"
        advice = (
            "This document contains significant restrictive covenants (e.g., Liability, Non-Compete, "
            "or IP assignment). Do NOT execute this contract without prior legal counsel review."
        )
    elif document_risk_pct >= 25.0 or medium_risk_count >= 2 or high_risk_count >= 1:
        risk_label = "MEDIUM RISK"
        recommendation = "SIGN WITH CAUTION (REVIEW HIGHLIGHTED CLAUSES)"
        advice = (
            "This document contains standard confidentiality terms along with specific restrictions "
            "(e.g., broad definition of confidential information or employee non-solicitation). "
            "Carefully review the flagged clauses."
        )
    else:
        risk_label = "LOW RISK"
        recommendation = "SAFE TO SIGN"
        advice = (
            "This contract conforms to standard non-disclosure terms and poses low risk of unexpected "
            "restrictive obligations."
        )

    return {
        "overall_risk_index": round(document_risk_pct, 1),
        "risk_status": risk_label,
        "recommendation": recommendation,
        "advice": advice,
        "high_risk_clause_count": high_risk_count,
        "medium_risk_clause_count": medium_risk_count,
        "detected_categories": sorted(list(detected_risk_categories)),
        "clauses": clause_evaluations,
    }
