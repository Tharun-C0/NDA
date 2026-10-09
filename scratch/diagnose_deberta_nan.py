"""
scratch/diagnose_deberta_nan.py
Layer-by-layer AdamW update diagnostic for DeBERTa-v3.
"""

import os
import sys
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig

ROOT = Path(__file__).resolve().parents[1]

APPROVED_CATEGORIES = [
    "Party Identification", "Purpose", "NDA Type",
    "Definition of Confidential Information", "Confidentiality Obligations",
    "Authorized Disclosure", "Non-Confidential Information",
    "Liability for Damages", "Competition Rights", "Term and Termination",
    "Intellectual Property", "Employees", "Governing Law and Jurisdiction",
    "Additional Information"
]
CAT_TO_LABEL = {c: f"label_{c.lower().replace(' ', '_')}" for c in APPROVED_CATEGORIES}
LABEL_COLS = list(CAT_TO_LABEL.values())

def run_layer_diagnostic(use_autocast_bf16=True):
    device = torch.device("cuda")
    print(f"\n=======================================================")
    print(f" TESTING OPTIMIZER.STEP() (use_autocast_bf16={use_autocast_bf16})")
    print(f"=======================================================")

    synthetic_path = ROOT / "nda_clause_dataset_5000.csv"
    train_path = ROOT / "data/classification/module16_benchmark/train.csv"
    df_synth_raw = pd.read_csv(synthetic_path)
    df_train = pd.read_csv(train_path)
    df_synth = df_synth_raw.copy()
    for cat, label_col in CAT_TO_LABEL.items():
        if cat in df_synth.columns:
            df_synth[label_col] = df_synth[cat]
            
    synth_formatted = df_synth.copy()
    if "document_id" not in synth_formatted.columns:
        synth_formatted["document_id"] = "SYNTHETIC_DOC"
    for col in df_train.columns:
        if col not in synth_formatted.columns:
            synth_formatted[col] = 0 if col.startswith("label_") else "SYNTHETIC"
    synth_formatted = synth_formatted[df_train.columns]
    df_combined_train = pd.concat([df_train, synth_formatted], ignore_index=True)
    train_labels = df_combined_train[LABEL_COLS].values
    pos_counts = train_labels.sum(axis=0)
    neg_counts = len(df_combined_train) - pos_counts
    pos_weights_tensor = torch.tensor(neg_counts / np.maximum(pos_counts, 1.0), dtype=torch.float32, device=device)

    hf_model_id = "microsoft/deberta-v3-base"
    tokenizer = AutoTokenizer.from_pretrained(hf_model_id)
    config = AutoConfig.from_pretrained(hf_model_id, num_labels=14, problem_type="multi_label_classification")
    model = AutoModelForSequenceClassification.from_pretrained(hf_model_id, config=config)
    model.to(device)

    batch_texts = df_combined_train["clause_text"].iloc[:16].tolist()
    batch_labels = torch.tensor(train_labels[:16], dtype=torch.float32, device=device)
    encoding = tokenizer(batch_texts, max_length=256, padding="max_length", truncation=True, return_tensors="pt")
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weights_tensor)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)

    model.train()
    optimizer.zero_grad()

    if use_autocast_bf16:
        with torch.amp.autocast('cuda', dtype=torch.bfloat16):
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
    else:
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits

    loss = criterion(logits.float(), batch_labels)
    loss.backward()

    print("\n--- PRE-STEP GRADIENT CHECK (by layer group) ---")
    nan_layers_pre = []
    for name, p in model.named_parameters():
        if p.grad is not None:
            if torch.isnan(p.grad).any() or torch.isinf(p.grad).any():
                nan_layers_pre.append((name, p.grad.dtype, p.grad.norm().item()))
    print(f"Pre-step NaN/Inf gradients count: {len(nan_layers_pre)}")

    # Clip grads
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

    # Record parameter values before step
    params_before = {name: p.clone().detach() for name, p in model.named_parameters()}

    optimizer.step()

    print("\n--- POST-STEP PARAMETER CHECK (by layer group) ---")
    nan_params_post = []
    for name, p in model.named_parameters():
        if torch.isnan(p).any() or torch.isinf(p).any():
            nan_params_post.append(name)

    print(f"Post-step NaN/Inf parameters count: {len(nan_params_post)} / {len(list(model.parameters()))}")
    if nan_params_post:
        print("First 15 NaN parameters:")
        for name in nan_params_post[:15]:
            p_old = params_before[name]
            p_new = dict(model.named_parameters())[name]
            p_grad = dict(model.named_parameters())[name].grad
            print(f"  - {name} | dtype: {p_new.dtype} | old_min/max: {p_old.min().item():.4f}/{p_old.max().item():.4f} | grad_norm: {p_grad.norm().item() if p_grad is not None else 'None'}")

if __name__ == "__main__":
    run_layer_diagnostic(use_autocast_bf16=True)
    run_layer_diagnostic(use_autocast_bf16=False)
