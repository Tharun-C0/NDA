import os
import sys
import logging
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

try:
    from backend.app.core.config import settings
    DEFAULT_HF_MODEL_ID = getattr(settings, "HF_MODEL_ID", "THARUNC0/legal-roberta-nda-clause-classifier")
    DEFAULT_HF_TOKEN = getattr(settings, "HF_TOKEN", None)
except Exception:
    DEFAULT_HF_MODEL_ID = "THARUNC0/legal-roberta-nda-clause-classifier"
    DEFAULT_HF_TOKEN = None

logger = logging.getLogger(__name__)

# Approved 14 taxonomy categories (Authoritative Order)
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

# Cache for loaded models, tokenizers, and devices
# Structure: {model_key: (tokenizer, model, dev_str, categories, threshold)}
_MODEL_CACHE: Dict[str, Tuple[Any, Any, str, List[str], float]] = {}
_LOADING_LOCK = threading.Lock()


def get_device() -> torch.device:
    """Return CUDA device if available, otherwise CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def get_hf_config() -> Tuple[str, Optional[str]]:
    """Retrieve HF_MODEL_ID and HF_TOKEN safely from environment."""
    model_id = os.environ.get("HF_MODEL_ID", DEFAULT_HF_MODEL_ID)
    token = os.environ.get("HF_TOKEN", DEFAULT_HF_TOKEN)
    if token == "":
        token = None
    return model_id, token


def load_model_and_tokenizer(
    model_key: str = "legal_roberta",
    force_reload: bool = False
) -> Tuple[Any, Any, torch.device, List[str], float]:
    """
    Load tokenizer and PyTorch model weights from Hugging Face Hub (or verified local checkpoint fallback).
    Uses thread-safe singleton caching to avoid repeated process loads.
    """
    if model_key not in CHECKPOINT_MAP:
        model_key = "legal_roberta"

    with _LOADING_LOCK:
        if not force_reload and model_key in _MODEL_CACHE:
            tokenizer, model, dev_str, categories, threshold = _MODEL_CACHE[model_key]
            device = torch.device(dev_str)
            return tokenizer, model, device, categories, threshold

        device = get_device()
        hf_model_id, hf_token = get_hf_config()
        local_path = CHECKPOINT_MAP.get(model_key)

        model_loaded = False
        tokenizer = None
        model = None
        categories = APPROVED_CATEGORIES
        threshold = 0.50

        # Attempt 1: Load from Hugging Face Hub
        if model_key == "legal_roberta" and hf_model_id:
            try:
                logger.info(f"Loading model '{model_key}' from Hugging Face Hub ID '{hf_model_id}' onto {device}...")
                tokenizer = AutoTokenizer.from_pretrained(hf_model_id, token=hf_token)
                model = AutoModelForSequenceClassification.from_pretrained(hf_model_id, token=hf_token)
                model_loaded = True
                logger.info(f"Successfully loaded '{hf_model_id}' from Hugging Face Hub.")
            except Exception as hf_err:
                logger.warning(
                    f"Hugging Face Hub load failed for repository '{hf_model_id}'. "
                    f"Error type: {type(hf_err).__name__}. Attempting local checkpoint fallback if available..."
                )

        # Attempt 2: Fallback to local checkpoint path if HF load skipped or failed
        if not model_loaded:
            if local_path and local_path.exists():
                try:
                    logger.info(f"Loading local checkpoint '{model_key}' from {local_path} onto {device}...")
                    tokenizer = AutoTokenizer.from_pretrained(local_path)
                    model = AutoModelForSequenceClassification.from_pretrained(local_path)
                    model_loaded = True
                    logger.info(f"Successfully loaded local checkpoint from {local_path}.")
                except Exception as local_err:
                    logger.error(f"Local checkpoint load failed at {local_path}: {local_err}")
            else:
                # Check EXP-03 fallback
                exp03_path = CHECKPOINT_MAP.get("exp03")
                if exp03_path and exp03_path.exists():
                    try:
                        logger.info(f"Fallback loading local EXP-03 checkpoint from {exp03_path}...")
                        tokenizer = AutoTokenizer.from_pretrained(exp03_path)
                        model = AutoModelForSequenceClassification.from_pretrained(exp03_path)
                        model_loaded = True
                    except Exception:
                        pass

        if not model_loaded or model is None or tokenizer is None:
            safe_msg = (
                f"Failed to load multi-label classification model '{model_key}'. "
                f"Please verify HF_MODEL_ID ('{hf_model_id}') and HF_TOKEN environment variables."
            )
            logger.error(safe_msg)
            raise RuntimeError(safe_msg)

        model.to(device)
        model.eval()

        # Extract category mapping from model config if custom id2label exists
        if hasattr(model.config, "id2label") and model.config.id2label:
            cfg_id2label = model.config.id2label
            # If config id2label contains non-default categories (not LABEL_0)
            if not str(cfg_id2label.get(0, cfg_id2label.get("0", ""))).startswith("LABEL_"):
                extracted_cats = []
                for i in range(model.config.num_labels):
                    cat_name = cfg_id2label.get(i, cfg_id2label.get(str(i)))
                    if cat_name:
                        extracted_cats.append(str(cat_name))
                if len(extracted_cats) == len(APPROVED_CATEGORIES):
                    categories = extracted_cats

        _MODEL_CACHE[model_key] = (tokenizer, model, str(device), categories, threshold)
        return tokenizer, model, device, categories, threshold


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

    tokenizer, model, device, categories, threshold = load_model_and_tokenizer(model_key)

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

            kwargs = {"input_ids": input_ids, "attention_mask": attention_mask}
            if "token_type_ids" in encoded:
                kwargs["token_type_ids"] = encoded["token_type_ids"].to(device)

            outputs = model(**kwargs)
            logits = outputs.logits
            probs = torch.sigmoid(logits).cpu().numpy()
            all_probabilities.append(probs)

    if all_probabilities:
        res = np.vstack(all_probabilities)
        return res
    return np.zeros((0, 14), dtype=np.float32)
