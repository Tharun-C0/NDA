import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup

device = torch.device("cuda")
model_id = "microsoft/deberta-v3-base"

print(f"Loading {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=14)
model.to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
total_steps = 100
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=10, num_training_steps=total_steps)
scaler = torch.amp.GradScaler('cuda')
criterion = nn.BCEWithLogitsLoss()

sample_text = ["This is a test confidential clause for DeBERTa-v3 classification."] * 16
inputs = tokenizer(sample_text, padding="max_length", truncation=True, max_length=256, return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items()}
targets = torch.zeros((16, 14), device=device)

print("Running 5 AMP forward/backward passes...")
for step in range(1, 6):
    optimizer.zero_grad()
    with torch.amp.autocast('cuda'):
        outputs = model(**inputs)
        loss = criterion(outputs.logits, targets)
        
    scaler.scale(loss).backward()
    
    # Safe unscale & step pattern
    try:
        scaler.unscale_(optimizer)
    except Exception as e:
        print(f"  Step {step}: unscale_ exception: {e}")
        
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    
    scale_before = scaler.get_scale()
    scaler.step(optimizer)
    scaler.update()
    scale_after = scaler.get_scale()
    
    # Only step scheduler if optimizer was actually stepped (no inf/nan occurred)
    if scale_before <= scale_after:
        scheduler.step()
        print(f"  Step {step}: Loss = {loss.item():.4f} | Scaler stepped & Scheduler updated")
    else:
        print(f"  Step {step}: Loss = {loss.item():.4f} | Inf/NaN detected, scale reduced from {scale_before} to {scale_after}, scheduler step skipped")

print("DeBERTa-v3 AMP test finished cleanly!")
