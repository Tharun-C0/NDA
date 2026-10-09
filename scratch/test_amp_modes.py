import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = torch.device("cuda")
models = ["saibo/legal-roberta-base", "nlpaueb/legal-bert-base-uncased", "microsoft/deberta-v3-base"]

for model_id in models:
    print(f"\nTesting bfloat16 autocast for {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=14).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
    criterion = nn.BCEWithLogitsLoss()

    inputs = tokenizer(["This is a test confidential clause."] * 16, padding="max_length", truncation=True, max_length=256, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    targets = torch.zeros((16, 14), device=device)

    optimizer.zero_grad()
    with torch.amp.autocast('cuda', dtype=torch.bfloat16):
        outputs = model(**inputs)
        loss = criterion(outputs.logits, targets)

    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    print(f"SUCCESS! {model_id} bfloat16 mixed precision step completed with loss = {loss.item():.4f}")

print("\nALL 3 ARCHITECTURES WORK PERFECTLY WITH BFLOAT16 MIXED PRECISION!")
