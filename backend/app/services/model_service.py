import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

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

CHECKPOINT_MAP = {
    "legal_roberta": ROOT / "experiments" / "EXP-12_model_comparison" / "legal_roberta" / "best_checkpoint",
    "legal_bert": ROOT / "experiments" / "EXP-12_model_comparison" / "legal_bert" / "best_checkpoint",
    "deberta_v3": ROOT / "experiments" / "EXP-12_model_comparison" / "deberta_v3" / "best_checkpoint",
    "exp03": ROOT / "data" / "classification" / "module18_results" / "checkpoints" / "EXP-03",
}

# Cache for loaded models and tokenizers
_MODEL_CACHE: Dict[str, Tuple[Any, Any, str]] = {}


def get_device() -> torch.device:
    """Return CUDA device if available, otherwise CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_model_and_tokenizer(model_key: str = "legal_roberta") -> Tuple[Any, Any, torch.device]:
    """
    Load tokenizer and PyTorch model weights from verified checkpoint.
    Uses cached instances to avoid repeated loading.
    """
    if model_key not in CHECKPOINT_MAP:
        model_key = "legal_roberta"

    if model_key in _MODEL_CACHE:
        tokenizer, model, dev_str = _MODEL_CACHE[model_key]
        device = torch.device(dev_str)
        return tokenizer, model, device

    ckpt_path = CHECKPOINT_MAP[model_key]
    if not ckpt_path.exists():
        # Fallback to EXP-03 if specific key directory is missing
        ckpt_path = CHECKPOINT_MAP["exp03"]
        if not ckpt_path.exists():
            raise FileNotFoundError(f"No valid model checkpoint found at {ckpt_path}")

    device = get_device()
    logger.info(f"Loading checkpoint {model_key} from {ckpt_path} onto {device}...")

    tokenizer = AutoTokenizer.from_pretrained(ckpt_path)
    model = AutoModelForSequenceClassification.from_pretrained(ckpt_path)
    model.to(device)
    model.eval()

    _MODEL_CACHE[model_key] = (tokenizer, model, str(device))
    return tokenizer, model, device


def predict_clause_categories(
    clause_texts: List[str],
    model_key: str = "legal_roberta",
    batch_size: int = 16,
    max_length: int = 256,
) -> np.ndarray:
    """
    Run multi-label classification inference on a list of clause texts.
    
    Returns:
        NumPy array of shape (num_clauses, 14) containing sigmoid probabilities.
    """
    if not clause_texts:
        return np.zeros((0, 14), dtype=np.float32)

    tokenizer, model, device = load_model_and_tokenizer(model_key)

    all_probabilities = []
    
    with torch.no_grad():
        for i in range(0, len(clause_texts), batch_size):
            batch_texts = clause_texts[i : i + batch_size]
            encoded = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt"
            )
            input_ids = encoded["input_ids"].to(device)
            attention_mask = encoded["attention_mask"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probs = torch.sigmoid(logits).cpu().numpy()
            all_probabilities.append(probs)

    if all_probabilities:
        return np.vstack(all_probabilities)
    return np.zeros((0, 14), dtype=np.float32)
