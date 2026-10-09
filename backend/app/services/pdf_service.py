import sys
import os
import tempfile
import logging
from pathlib import Path
from typing import Tuple, Dict, Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from preprocessing.pdf_extractor import extract_text_from_pdf, ExtractionResult

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB Limit


class PDFProcessingError(Exception):
    """Custom exception for PDF processing failures."""
    pass


def validate_pdf_bytes(content: bytes, filename: str) -> None:
    """Validate PDF magic bytes, extension, and file size."""
    if len(content) == 0:
        raise PDFProcessingError("Uploaded file is empty (0 bytes).")
    
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise PDFProcessingError(
            f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    if not filename.lower().endswith(".pdf"):
        raise PDFProcessingError("Invalid file extension. File must be a .pdf document.")

    # Check PDF magic header (%PDF-)
    if not content.startswith(b"%PDF-"):
        raise PDFProcessingError("Invalid file format. File does not contain valid PDF magic header.")


def extract_pdf_content(content: bytes, filename: str) -> Tuple[str, ExtractionResult]:
    """
    Safely process uploaded PDF bytes using existing preprocessing.pdf_extractor module.
    
    Returns:
        Tuple of (extracted_text, extraction_result_object)
    """
    validate_pdf_bytes(content, filename)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            temp_path = tmp.name

        result = extract_text_from_pdf(temp_path, min_characters=30)
        
        if result.status == "failed" or not result.text.strip():
            raise PDFProcessingError(
                f"Failed to extract readable text from PDF: {result.error_message or 'No text found'}"
            )
            
        return result.text, result

    except PDFProcessingError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error extracting PDF text: {e}", exc_info=True)
        raise PDFProcessingError(f"Error processing PDF document: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp PDF file {temp_path}: {e}")
