import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = torch.device("cuda")
model_id = "microsoft/deberta-v3-base"

print(f"Loading {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=14).to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
criterion = nn.BCEWithLogitsLoss()

sample_text = ["This is a test confidential clause for DeBERTa-v3 classification."] * 16
inputs = tokenizer(sample_text, padding="max_length", truncation=True, max_length=256, return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items()}
targets = torch.zeros((16, 14), device=device)

print("Running 5 passes in FP32 (autocast disabled for DeBERTa-v3)...")
for step in range(1, 6):
    optimizer.zero_grad()
    outputs = model(**inputs)
    loss = criterion(outputs.logits, targets)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    print(f"Step {step}: Loss = {loss.item():.4f} | Is Finite: {torch.isfinite(loss).item()}")

print("DeBERTa-v3 FP32 test finished cleanly!")
