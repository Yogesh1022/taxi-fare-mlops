# Data Quality Fix - Complete Step-by-Step Guide

This guide walks you through fixing the 13 data quality issues manually.

## 🎯 Overview of Issues

```
✅ SOLVED AUTOMATICALLY:
├─ Issue 1: Missing total_amount (test) → Generated from components
├─ Issues 2-6: 55 nulls in 5 columns → Filled with mode/defaults
├─ Issue 7: passenger_count < 1 → Set to 1.0
├─ Issue 8: RatecodeID > 5 → Set to 1.0
├─ Issue 9: Negative fee values → Set to 0.0
├─ Issue 10: Invalid payment types → Standardized to 'other'
├─ Issues 11-13: Outliers → Capped at 95th percentile
```

## 📋 Step-by-Step Workflow

### **Step 1: Create Clean Data Directory**
```powershell
# Create folder if it doesn't exist
New-Item -Type Directory -Path "data/clean" -Force
```

### **Step 2: Run Data Cleaning**
```powershell
# Navigate to project
cd e:\TaxiFare\ MLOps

# Activate environment (if not already)
.\.venv\Scripts\Activate.ps1

# Run cleaning script
python -m src.data.clean
```

**Expected Output:**
```
Starting data cleaning (test=False)...
Initial shape: (10000, 17)
Handling missing values...
Filling 366 null passenger_count with 1.0
... [similar for other columns]
Cleaning complete! Final shape: (10000, 17)

Starting data cleaning (test=True)...
Initial shape: (1500, 17)
... [cleaning steps]
Generated total_amount column (estimated)
Cleaning complete! Final shape: (1500, 17)
```

**Files Created:**
- ✅ `data/clean/train_clean.csv` (10,000 rows, cleaned)
- ✅ `data/clean/test_clean.csv` (1,500 rows, cleaned)

### **Step 3: Verify Cleaned Data Passes Validation**
```powershell
# Run verification script
python -m src.data.verify_clean
```

**Expected Output:**
```
============================================================
VERIFYING CLEANED TRAINING DATA
============================================================
✅ TRAINING DATA PASSED VALIDATION!

============================================================
VERIFYING CLEANED TEST DATA
============================================================
✅ TEST DATA PASSED VALIDATION!

============================================================
VERIFICATION COMPLETE
============================================================
```

### **Step 4: Option A - Use Cleaned Data for Next Run**

**If NOT using DVC (Simple Approach):**

```powershell
# Backup original data
Copy-Item "data/raw/train.csv" "data/raw/train_ORIGINAL.csv"
Copy-Item "data/raw/test.csv" "data/raw/test_ORIGINAL.csv"

# Use cleaned data
Copy-Item "data/clean/train_clean.csv" "data/raw/train.csv" -Force
Copy-Item "data/clean/test_clean.csv" "data/raw/test.csv" -Force
```

### **Step 4: Option B - Use With DVC (Recommended)**

**If using DVC (Production Approach):**

✅ Already configured! The `dvc.yaml` now has a `clean` stage:

```yaml
stages:
  clean:
    cmd: python -m src.data.clean
    deps:
      - data/raw/train.csv
      - data/raw/test.csv
    outs:
      - data/clean/train_clean.csv
      - data/clean/test_clean.csv
  
  ingest:
    cmd: python -m src.data.ingest
    deps:
      - data/clean/train_clean.csv      ← Now reads from clean folder
      - data/clean/test_clean.csv
    outs:
      - data/processed/ingested_train.csv
      - data/processed/ingested_test.csv
```

**Run the DVC pipeline:**
```powershell
# Install DVC if needed
pip install dvc

# Initialize DVC (if not already done)
dvc init

# Run full pipeline: clean → ingest → validate
dvc repro

# Or run just cleaning
dvc repro -s clean
```

### **Step 5: Re-validate Your Data**

```powershell
# Validate the fixed data
python src/data/validate_run.py
```

**Expected Output:**
```
============================================================
Validating TRAINING data...
============================================================
✅ Data validation PASSED

============================================================
Validating TEST data...
============================================================
✅ Data validation PASSED

============================================================
Data Validation Summary
============================================================
Training data: ✓ PASS
Test data: ✓ PASS
```

### **Step 6: Check Your Data Quality Reports**

```powershell
# New reports will be generated in mlops/data_quality/
Get-ChildItem "mlops/data_quality/" -Name
```

Expected files:
```
data_quality_TIMESTAMP.json    ← Machine-readable report
data_quality_TIMESTAMP.md      ← Human-readable report
validation_metrics.json        ← Summary metrics
```

---

## 🤔 DVC vs Manual: Quick Decision Guide

| Aspect | Manual (Option A) | DVC (Option B) |
|--------|-------------------|----------------|
| **Setup** | 2 minutes | 5 minutes |
| **Learning Curve** | Simple | Moderate |
| **Data Versioning** | ❌ No | ✅ Yes |
| **Reproducibility** | ⚠️ Manual | ✅ Automatic |
| **Tracking Changes** | ❌ No | ✅ Yes |
| **Collaboration** | ❌ Hard | ✅ Easy |
| **For Production** | ❌ Not ideal | ✅ Recommended |

### **My Recommendation:**

**For Learning/Quick Testing:**
→ Use **Option A (Manual)** - faster to iterate

**For Production/Team Project:**
→ Use **Option B (DVC)** - reproducible and trackable

---

## 🔍 What Gets Fixed

### **Null Values Handling:**
```
passenger_count null → Filled with mode (most common value)
RatecodeID null → Filled with 1.0 (standard rate)
store_and_fwd_flag null → Filled with 'N' (no forwarding)
congestion_surcharge null → Filled with 0.0
Airport_fee null → Filled with 0.0
```

### **Out-of-Range Values:**
```
passenger_count < 1 → Changed to 1.0
RatecodeID > 5 → Changed to 1.0
All fees < 0 → Changed to 0.0
```

### **Invalid Categories:**
```
payment_type: 'Wallet' → 'other'
payment_type: 'UPI' → 'other'
payment_type: 'unknown' → 'other'
```

### **Outliers:**
```
passenger_count capped at 6
trip_distance capped at 95th percentile
tip_amount capped at 95th percentile
```

### **Missing Features (Test Data):**
```
total_amount = fare(estimated) + extra + tip + tolls + surcharges
```

---

## 🚨 Troubleshooting

### **Error: "FileNotFoundError: data/raw/train.csv"**
```powershell
# Run cleaning first
python -m src.data.clean

# Then verify
python -m src.data.verify_clean
```

### **Error: "Module not found: src.data.clean"**
```powershell
# Make sure you're in the correct directory
cd e:\TaxiFare\ MLOps

# Check __init__.py files exist
Get-ChildItem -Path "src/data/__init__.py"
```

### **Data Still Failing Validation?**
```powershell
# Check what's failing
python src/data/validate_run.py

# Review the markdown report
Get-Content "mlops/data_quality/data_quality_*.md" | Select -First 50
```

---

## ✅ Verification Checklist

After following all steps:

- [ ] Ran `python -m src.data.clean` successfully
- [ ] Created `data/clean/train_clean.csv` and `data/clean/test_clean.csv`
- [ ] Ran `python -m src.data.verify_clean` - both PASSED
- [ ] Backed up original raw data
- [ ] (Option A) Copied clean data to raw folder
- [ ] (Option B) Set up DVC pipeline
- [ ] Ran validation: `python src/data/validate_run.py` - ✅ PASSED

---

## 📊 Next Steps After Data Fix

1. **Data Splitting:** `python -m src.data.split`
2. **Feature Engineering:** `python -m src.features.pipeline`
3. **Model Training:** `python -m pipelines.training_pipeline`
4. **Evaluation:** Check MLflow in `mlruns/` folder

---

## 💾 Reference: File Structure After Cleanup

```
data/
├── raw/
│   ├── train.csv                    ← Original (backed up)
│   ├── test.csv                     ← Original (backed up)
│   ├── train_ORIGINAL.csv           ← Backup
│   └── test_ORIGINAL.csv            ← Backup
├── clean/                           ← NEW
│   ├── train_clean.csv              ← After cleaning
│   └── test_clean.csv               ← After cleaning
├── processed/
│   ├── ingested_train.csv           ← After ingestion
│   └── ingested_test.csv            ← After ingestion
└── interim/
    └── [feature splits]             ← After splitting
```

---

## 📞 Questions?

Common issues:
- **Clean script fails?** → Check `src/data/clean.py` has proper imports
- **Still getting errors?** → Run verify script to see exact failures
- **DVC not working?** → Run `dvc dag` to see pipeline structure
