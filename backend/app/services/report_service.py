import sys
import logging
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


def generate_pdf_report(analysis_dict: Dict[str, Any]) -> bytes:
    """
    Generate a downloadable PDF executive risk assessment report from stored analysis data.
    
    Returns:
        Bytes of valid PDF document (%PDF-).
    """
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # Standard A4 size

    # Margin & Header setup
    margin_x = 40
    curr_y = 50

    def draw_header(p):
        p.insert_text((margin_x, 40), "NDA AUTOMATED RISK ASSESSMENT REPORT", fontsize=14, fontname="helv", color=(0.1, 0.2, 0.5))
        p.draw_line(fitz.Point(margin_x, 46), fitz.Point(555, 46), color=(0.1, 0.2, 0.5), width=1)

    draw_header(page)
    curr_y = 65

    # Document Information Block
    doc_id = analysis_dict.get("document_id", "N/A")
    filename = analysis_dict.get("filename", "N/A")
    page_count = analysis_dict.get("page_count", 0)
    total_clauses = analysis_dict.get("total_clauses", 0)
    risk_index = analysis_dict.get("overall_risk_index", 0.0)
    risk_status = analysis_dict.get("risk_status", "UNKNOWN")
    raw_rec = analysis_dict.get("recommendation", "")

    # Qualified Wording mapping
    if "HIGH" in risk_status:
        qualified_rec = "HIGH RISK — Legal counsel review recommended."
        rec_color = (0.8, 0.1, 0.1)
    elif "MEDIUM" in risk_status:
        qualified_rec = "MEDIUM RISK — Review highlighted clauses."
        rec_color = (0.8, 0.5, 0.0)
    else:
        qualified_rec = "LOW RISK — No high-risk categories detected by current rules; independent review may still be necessary."
        rec_color = (0.0, 0.5, 0.2)

    info_box = (
        f"Document ID     : {doc_id}\n"
        f"Filename        : {filename}\n"
        f"Page Count      : {page_count}\n"
        f"Segmented Clauses: {total_clauses}\n"
        f"Analysis Status : Completed"
    )
    page.insert_textbox(fitz.Rect(margin_x, curr_y, 555, curr_y + 70), info_box, fontsize=10, fontname="courier")
    curr_y += 80

    # Risk Summary Box
    page.draw_rect(fitz.Rect(margin_x, curr_y, 555, curr_y + 85), color=rec_color, width=1.5)
    
    score_text = f"OVERALL RISK INDEX: {risk_index:.1f}% (Weighted Risk Index, 0 - 100%)"
    page.insert_text((margin_x + 10, curr_y + 20), score_text, fontsize=11, fontname="helv", color=(0, 0, 0))
    page.insert_text((margin_x + 10, curr_y + 40), f"STATUS: {risk_status}", fontsize=11, fontname="helv", color=rec_color)
    page.insert_text((margin_x + 10, curr_y + 65), f"DECISION: {qualified_rec}", fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))

    curr_y += 105

    # Detected Categories Section
    detected_cats = analysis_dict.get("detected_categories", [])
    page.insert_text((margin_x, curr_y), "DETECTED LEGAL CATEGORIES ACROSS DOCUMENT:", fontsize=11, fontname="helv", color=(0.1, 0.2, 0.5))
    curr_y += 15

    if detected_cats:
        cats_str = ", ".join(detected_cats)
        page.insert_textbox(fitz.Rect(margin_x, curr_y, 555, curr_y + 40), cats_str, fontsize=9, fontname="helv")
        curr_y += 45
    else:
        page.insert_text((margin_x, curr_y), "None detected above threshold.", fontsize=9, fontname="helv")
        curr_y += 20

    # High & Medium Risk Clause Summaries
    page.insert_text((margin_x, curr_y), "FLAGGED CLAUSE SUMMARIES:", fontsize=11, fontname="helv", color=(0.1, 0.2, 0.5))
    curr_y += 20

    clauses = analysis_dict.get("clauses", [])
    flagged = [c for c in clauses if c.get("risk_level") in ["HIGH", "MEDIUM"]]

    if not flagged:
        page.insert_text((margin_x, curr_y), "No clauses flagged as High or Medium risk.", fontsize=9, fontname="helv")
        curr_y += 20
    else:
        for c in flagged[:8]:  # Top 8 flagged clauses
            if curr_y > 750:  # New page if bottom reached
                page = doc.new_page(width=595, height=842)
                draw_header(page)
                curr_y = 65

            r_lvl = c.get("risk_level")
            c_text = c.get("text", "").replace("\n", " ")
            if len(c_text) > 120:
                c_text = c_text[:117] + "..."

            preds = c.get("predicted_categories", [])
            preds_str = ", ".join([f"{p['category']} ({p['confidence'] * 100:.1f}%)" for p in preds])

            c_box = f"[{r_lvl} RISK] Clause ID: {c.get('clause_id')}\n  Snippet: \"{c_text}\"\n  Categories: {preds_str}"
            page.insert_textbox(fitz.Rect(margin_x, curr_y, 555, curr_y + 45), c_box, fontsize=8, fontname="helv")
            curr_y += 50

    # Methodology & Disclaimer at Footer
    if curr_y > 720:
        page = doc.new_page(width=595, height=842)
        draw_header(page)
        curr_y = 65

    curr_y = max(curr_y + 10, 720)
    page.draw_line(fitz.Point(margin_x, curr_y), fitz.Point(555, curr_y), color=(0.7, 0.7, 0.7), width=0.5)
    curr_y += 12

    methodology = (
        "METHODOLOGY NOTE: The Document Risk Index is a rule-based weighted index (0-100%) calculated "
        "by identifying unique legal clause categories using fine-tuned transformer classification and "
        "aggregating established category risk weights. It is not a statistical probability of breach.\n"
        "DISCLAIMER: Automated AI analysis report for informational purposes. Does not constitute legal advice."
    )
    page.insert_textbox(fitz.Rect(margin_x, curr_y, 555, 820), methodology, fontsize=7, fontname="helv", color=(0.4, 0.4, 0.4))

    return doc.tobytes()
