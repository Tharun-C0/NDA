import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(r"c:\Users\ADMIN\Downloads\NDA")

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

# Map category names to label_... columns matching benchmark
CAT_TO_LABEL = {c: f"label_{c.lower().replace(' ', '_')}" for c in APPROVED_CATEGORIES}
LABEL_COLS = list(CAT_TO_LABEL.values())

synthetic_file = ROOT / "nda_clause_dataset_5000.csv"
train_file = ROOT / "data/classification/module16_benchmark/train.csv"
val_file = ROOT / "data/classification/module16_benchmark/validation.csv"
test_file = ROOT / "data/classification/module16_benchmark/test.csv"

df_synth_raw = pd.read_csv(synthetic_file)
df_train = pd.read_csv(train_file)
df_val = pd.read_csv(val_file)
df_test = pd.read_csv(test_file)

print(f"=======================================================")
print(f"         DATA VALIDATION & PRE-FLIGHT REPORT          ")
print(f"=======================================================")

# Map category columns to label_... in synthetic dataset
df_synth = df_synth_raw.copy()
for cat, label_col in CAT_TO_LABEL.items():
    if cat in df_synth.columns:
        df_synth[label_col] = df_synth[cat]

# Check 1: Exactly 5,000 rows
synth_rows = len(df_synth)
assert synth_rows == 5000, f"Expected 5000 rows, got {synth_rows}"
print(f"[CHECK 1 PASS] Synthetic dataset has exactly 5,000 rows.")

# Check 2: All 14 labels exist
missing_labels = [c for c in LABEL_COLS if c not in df_synth.columns]
assert len(missing_labels) == 0, f"Missing label columns: {missing_labels}"
print(f"[CHECK 2 PASS] All 14 labels exist in synthetic dataset.")

# Check 3: No invalid labels (must be strictly binary 0 or 1)
label_vals = set(df_synth[LABEL_COLS].values.flatten())
invalid_vals = label_vals - {0, 1}
assert len(invalid_vals) == 0, f"Invalid label values found: {invalid_vals}"
print(f"[CHECK 3 PASS] No invalid labels (all binary 0 or 1).")

# Check 4: No empty clause text
empty_text = df_synth[df_synth["clause_text"].isna() | (df_synth["clause_text"].str.strip() == "")]
assert len(empty_text) == 0, f"Found {len(empty_text)} empty clause text rows"
print(f"[CHECK 4 PASS] No empty clause text.")

# Check 5: No duplicate clause IDs
dup_cids = df_synth[df_synth.duplicated(subset=["clause_id"])]
assert len(dup_cids) == 0, f"Found {len(dup_cids)} duplicate clause IDs"
print(f"[CHECK 5 PASS] No duplicate clause IDs.")

# Check 6: No duplicate clause text within synthetic dataset
dup_texts = df_synth[df_synth.duplicated(subset=["clause_text"])]
assert len(dup_texts) == 0, f"Found {len(dup_texts)} duplicate clause text rows"
print(f"[CHECK 6 PASS] No duplicate clause text within synthetic dataset.")

# Check 7: Label columns match existing benchmark
benchmark_label_cols = [c for c in df_train.columns if c.startswith("label_") and c != "label_source"]
assert sorted(LABEL_COLS) == sorted(benchmark_label_cols), f"Label columns mismatch:\nLABEL_COLS: {sorted(LABEL_COLS)}\nbenchmark: {sorted(benchmark_label_cols)}"
print(f"[CHECK 7 PASS] Label columns match the existing benchmark.")

# Check 8: Training/validation/test schemas match
train_cols = list(df_train.columns)
val_cols = list(df_val.columns)
test_cols = list(df_test.columns)
assert train_cols == val_cols == test_cols, "Training/validation/test schemas mismatch"
print(f"[CHECK 8 PASS] Training, validation, and test schemas match perfectly.")

# Check 9: Synthetic data is NOT present in validation or test
val_texts = set(df_val["clause_text"].str.strip())
test_texts = set(df_test["clause_text"].str.strip())
synth_texts = set(df_synth["clause_text"].str.strip())

synth_in_val = synth_texts.intersection(val_texts)
synth_in_test = synth_texts.intersection(test_texts)
assert len(synth_in_val) == 0, f"Found {len(synth_in_val)} synthetic clauses in validation set!"
assert len(synth_in_test) == 0, f"Found {len(synth_in_test)} synthetic clauses in test set!"
print(f"[CHECK 9 PASS] Synthetic data is NOT present in validation set (0 overlap).")
print(f"[CHECK 9 PASS] Synthetic data is NOT present in test set (0 overlap).")

print(f"\n=======================================================")
print(f"                  DATASET ROW COUNTS                  ")
print(f"=======================================================")
print(f"Existing training rows:  {len(df_train)}")
print(f"Synthetic training rows: {len(df_synth)}")
print(f"Combined training rows:  {len(df_train) + len(df_synth)}")
print(f"Validation rows:        {len(df_val)}")
print(f"Test rows:              {len(df_test)}")
print(f"=======================================================\n")
