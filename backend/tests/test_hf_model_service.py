import os
import logging
import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from backend.app.services.model_service import (
    load_model_and_tokenizer,
    predict_clause_categories,
    APPROVED_CATEGORIES,
    _MODEL_CACHE,
    get_hf_config
)


def test_approved_categories_count_and_order():
    """Verify standard 14 taxonomy categories and index order."""
    assert len(APPROVED_CATEGORIES) == 14
    assert APPROVED_CATEGORIES[0] == "Party Identification"
    assert APPROVED_CATEGORIES[3] == "Definition of Confidential Information"
    assert APPROVED_CATEGORIES[12] == "Governing Law and Jurisdiction"
    assert APPROVED_CATEGORIES[13] == "Additional Information"


def test_hf_config_retrieval(monkeypatch):
    """Verify environment variables HF_MODEL_ID and HF_TOKEN resolution."""
    monkeypatch.setenv("HF_MODEL_ID", "custom/test-repo")
    monkeypatch.setenv("HF_TOKEN", "test_secret_token_123")

    model_id, token = get_hf_config()
    assert model_id == "custom/test-repo"
    assert token == "test_secret_token_123"


def test_mocked_model_service_singleton_loading(monkeypatch):
    """Verify model loading occurs only ONCE per process and caches singleton instance."""
    # Reset model cache for test
    _MODEL_CACHE.clear()

    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    mock_model.config.num_labels = 14
    mock_model.config.id2label = {}

    with patch("backend.app.services.model_service.AutoTokenizer.from_pretrained", return_value=mock_tokenizer) as mock_tok_fn, \
         patch("backend.app.services.model_service.AutoModelForSequenceClassification.from_pretrained", return_value=mock_model) as mock_mod_fn:

        # First call triggers load
        tok1, mod1, dev1, cats1, thresh1 = load_model_and_tokenizer("legal_roberta")
        assert mock_tok_fn.call_count == 1
        assert mock_mod_fn.call_count == 1

        # Second call reuses cached singleton without re-downloading
        tok2, mod2, dev2, cats2, thresh2 = load_model_and_tokenizer("legal_roberta")
        assert mock_tok_fn.call_count == 1  # Still 1 call!
        assert mock_mod_fn.call_count == 1
        assert tok1 is tok2
        assert mod1 is mod2


def test_mocked_predict_clause_categories():
    """Verify predict_clause_categories returns np.ndarray of shape (N, 14) with sigmoid probs."""
    _MODEL_CACHE.clear()

    mock_tokenizer = MagicMock()
    # Mock tokenizer output
    mock_tokenizer.return_value = {
        "input_ids": MagicMock(to=lambda d: MagicMock()),
        "attention_mask": MagicMock(to=lambda d: MagicMock())
    }

    mock_model = MagicMock()
    mock_model.config.num_labels = 14
    mock_model.config.id2label = {}

    # Mock output logits shape (2 clauses, 14 classes)
    import torch
    mock_logits = torch.tensor([
        [0.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, 5.0, -10.0],
        [-10.0, -10.0, -10.0, 4.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0]
    ])
    mock_outputs = MagicMock()
    mock_outputs.logits = mock_logits
    mock_model.return_value = mock_outputs

    with patch("backend.app.services.model_service.AutoTokenizer.from_pretrained", return_value=mock_tokenizer), \
         patch("backend.app.services.model_service.AutoModelForSequenceClassification.from_pretrained", return_value=mock_model):

        sample_clauses = [
            "This Agreement shall be governed by the laws of Delaware.",
            "Confidential Information means all trade secrets disclosed."
        ]
        probs = predict_clause_categories(sample_clauses, model_key="legal_roberta")

        assert isinstance(probs, np.ndarray)
        assert probs.shape == (2, 14)
        # Check sigmoid range [0, 1]
        assert (probs >= 0.0).all() and (probs <= 1.0).all()

        # Clause 1 index 12 (Governing Law) sigmoid(5.0) > 0.99
        assert probs[0, 12] > 0.95
        # Clause 2 index 3 (Definition) sigmoid(4.0) > 0.95
        assert probs[1, 3] > 0.95


def test_safe_error_handling_without_token_leakage(caplog, monkeypatch):
    """Verify safe error messages when model fails to load without leaking access token."""
    _MODEL_CACHE.clear()
    secret_token = "hf_SUPERSECRETKEY12345"
    monkeypatch.setenv("HF_TOKEN", secret_token)

    with patch("backend.app.services.model_service.AutoTokenizer.from_pretrained", side_effect=Exception("HF 401 Unauthorized")), \
         patch("backend.app.services.model_service.CHECKPOINT_MAP", {}):

        with caplog.at_level(logging.INFO):
            with pytest.raises(RuntimeError) as exc_info:
                load_model_and_tokenizer("legal_roberta", force_reload=True)

            # Confirm RuntimeError raised
            assert "Failed to load multi-label classification model" in str(exc_info.value)

            # SECURITY CONFIRMATION: Token must NOT be present in log output or exception message
            assert secret_token not in str(exc_info.value)
            assert secret_token not in caplog.text


def test_real_model_inference_with_local_or_cached():
    """Real non-retrained inference test using export or cached checkpoint if present."""
    from pathlib import Path
    export_path = Path("artifacts/legal_roberta_nda")

    if not export_path.exists():
        pytest.skip("Export directory artifacts/legal_roberta_nda not available for real model test.")

    _MODEL_CACHE.clear()
    sample_text = ["This Agreement shall be governed by the laws of the State of Delaware."]

    # Predict using model service
    probs = predict_clause_categories(sample_text, model_key="legal_roberta")

    assert isinstance(probs, np.ndarray)
    assert probs.shape == (1, 14)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()
    # Check index 12 (Governing Law and Jurisdiction)
    assert probs[0, 12] >= 0.50
