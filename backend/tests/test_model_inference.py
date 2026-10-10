import pytest
import numpy as np
from backend.app.services.model_service import (
    load_model_and_tokenizer,
    predict_clause_categories,
    APPROVED_CATEGORIES,
    CHECKPOINT_MAP
)


@pytest.mark.parametrize("model_key", ["legal_roberta", "legal_bert", "deberta_v3"])
def test_real_checkpoint_loading_and_inference(model_key):
    """Real inference test on verified trained checkpoints."""
    ckpt_path = CHECKPOINT_MAP[model_key]
    if not ckpt_path.exists():
        pytest.skip(f"Checkpoint path {ckpt_path} does not exist.")

    tokenizer, model, device, *rest = load_model_and_tokenizer(model_key)
    assert tokenizer is not None
    assert model is not None
    assert model.config.num_labels == 14


    test_clauses = [
        "The Receiving Party shall maintain all Confidential Information in strict confidence.",
        "Either party may terminate this Agreement upon thirty (30) days written notice."
    ]

    probs = predict_clause_categories(test_clauses, model_key=model_key, batch_size=2)
    assert isinstance(probs, np.ndarray)
    assert probs.shape == (2, 14)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()
