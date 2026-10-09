import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from preprocessing.clause_segmenter_v3 import ImprovedSegmenterV3, SegmentedDocumentV3, ClauseV3

logger = logging.getLogger(__name__)


def segment_nda_text(text: str, document_id: str = "doc_uploaded") -> SegmentedDocumentV3:
    """
    Segment extracted NDA text into legal clauses using existing ImprovedSegmenterV3.
    
    Args:
        text: Extracted raw NDA document text.
        document_id: Unique document identifier.
        
    Returns:
        SegmentedDocumentV3 object containing structured ClauseV3 list.
    """
    segmenter = ImprovedSegmenterV3(min_clause_length=20)
    segmented_doc = segmenter.segment(text=text, document_id=document_id)
    return segmented_doc
