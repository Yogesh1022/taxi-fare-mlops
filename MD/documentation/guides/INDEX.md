# 📖 GUIDES FOLDER

**Purpose**: How-to guides, quick-start instructions, and reference documentation

## 📋 FILES IN THIS FOLDER

### 1. QUICK_COMMAND_REFERENCE.md ⭐ START HERE
**Location**: Root  
**Read Time**: 5 minutes  
**Audience**: Developers  

**Contents**:
- One-liner commands for common tasks
- Makefile targets with descriptions
- Quick setup instructions
- Common troubleshooting fixes
- Command categories: Setup, Testing, Training, Serving, Docker

**When to Use**: 
- Can't remember a command
- Quick reference while coding
- First thing to check for syntax

---

### 2. RUN_AND_TEST_GUIDE.md ⭐ COMPREHENSIVE
**Location**: Root  
**Read Time**: 45 minutes (or skim for specific day)  
**Audience**: Developers  

**Contents**:
- Step-by-step walkthrough of Days 1-10
- Code examples for each day
- Test commands and expected outputs
- Troubleshooting section
- Performance metrics
- 10 High-Priority & Medium-Priority improvements

**When to Use**: 
- Learning how to run each day's tasks
- Executing full pipeline end-to-end
- Validating that everything works
- After setup, before deploying

---

### 3. DOCUMENTATION_INDEX.md
**Location**: Root  
**Read Time**: 20 minutes  

**Contents**:
- Master index of all documentation
- Navigation guide
- File organization overview
- Learning paths
- Quick lookup tables

---

### 4. DATA_CLEANING_GUIDE.md
**Location**: Root  
**Read Time**: 15 minutes  
**Audience**: Data Engineers  

**Contents**:
- Data quality issues found in real data
- How to detect problems
- Cleaning procedures
- Validation checks
- Day 2 data validation details

---

### 5. MLFLOW_QUICKSTART_GUIDE.md
**Location**: Root  
**Read Time**: 20 minutes  
**Audience**: ML Engineers  

**Contents**:
- MLflow concepts overview
- How to track experiments
- Logging parameters, metrics, artifacts
- Model registry workflow
- Example outputs from real runs
- Comparison results

---

### 6. MLFLOW_VISUAL_GUIDE.md
**Location**: Root  
**Read Time**: 25 minutes  
**Audience**: ML Engineers  

**Contents**:
- Visual walkthrough of MLflow interface
- Screenshot descriptions (conceptual)
- Dashboard navigation
- Experiment comparison
- Model registry stages

---

### 7. MLFLOW_COMPLETE_SETUP.md
**Location**: Root  
**Read Time**: 30 minutes  
**Audience**: ML Engineers  

**Contents**:
- Complete MLflow setup from scratch
- Configuration details
- Server startup
- Integration with training pipeline
- Best practices
- Production considerations

---

## 🎯 QUICK NAVIGATION WITHIN FOLDER

```
JUST STARTED?                    → QUICK_COMMAND_REFERENCE.md
Want step-by-step guidance?      → RUN_AND_TEST_GUIDE.md
Need ALL documentation?          → DOCUMENTATION_INDEX.md
Data quality questions?          → DATA_CLEANING_GUIDE.md
MLflow tracking / experiments?   → MLFLOW_QUICKSTART_GUIDE.md + VISUAL_GUIDE.md
MLflow complete setup?           → MLFLOW_COMPLETE_SETUP.md
```

---

## 🎓 LEARNING PATHS

### Path 1: Setup to First Test (30 minutes)
1. Read QUICK_COMMAND_REFERENCE.md (5 min)
2. Run `make setup` from command reference
3. Follow RUN_AND_TEST_GUIDE.md Day 1 (15 min)
4. Run `make test` to verify

### Path 2: Understanding MLflow (45 minutes)
1. Read MLFLOW_QUICKSTART_GUIDE.md (20 min)
2. Read MLFLOW_VISUAL_GUIDE.md (15 min)
3. Follow MLFLOW_COMPLETE_SETUP.md (10 min hands-on)

### Path 3: Full End-to-End Run (120 minutes)
1. Start with QUICK_COMMAND_REFERENCE.md
2. Follow RUN_AND_TEST_GUIDE.md Days 1-10
3. Use DOCUMENTATION_INDEX.md for cross-references

---

## 💡 TIPS

- **One-liners**: Search QUICK_COMMAND_REFERENCE.md first
- **Step-by-step**: RUN_AND_TEST_GUIDE.md has everything
- **Getting lost**: Check DOCUMENTATION_INDEX.md
- **MLflow questions**: Quickstart > Visual > Complete Setup progression

---

**Last Updated**: April 11, 2026  
**Folder Purpose**: Practical guides & how-to documentation  
**Primary Audience**: Developers, ML Engineers, Data Engineers
