# ML Data Pipeline — ScriptChain Health Interview

**Objective:** Build a production-style ML data pipeline that ingests daily CSV files, validates and cleans the data, and triggers model training only when data quality passes — built for a churn prediction use case.

---

## What I Built

A fully automated ETL + validation + training pipeline orchestrated with **Prefect**. Every day a new CSV lands in `data/raw/`. The pipeline picks it up, runs it through two validation gates, cleans it, trains a versioned Random Forest model if everything passes, and writes structured reports at every step. Files that fail validation are quarantined to `data/rejected/` — no bad data ever reaches the model.

To demonstrate the full pipeline including failure handling, the demo dataset includes an intentionally corrupted Day 2 file (missing the `Churn` target column and containing negative numeric values). This lets you watch the pipeline validate, reject, and continue cleanly without interrupting the schedule.

---

## Pipeline Flow

```
A new CSV lands in data/raw/
         │
         ▼
  Already processed?  ──yes──▶  Skip (idempotent)
         │ no
         ▼
  Pre-clean validation
  (schema, required columns, target column exists and is valid)
         │
         ├── FAIL ──▶  Save to data/rejected/  ──▶  Write report  ──▶  Mark manifest  ──▶  Stop
         │
         ▼
  Clean
  (strip whitespace, remove duplicates, parse TotalCharges, add ingestion_date)
         │
         ▼
  Post-clean validation
  (row count, numeric columns non-negative, both churn classes present)
         │
         ├── FAIL ──▶  Save to data/rejected/  ──▶  Write report  ──▶  Mark manifest  ──▶  Stop
         │
         ▼
  Save processed CSV  ──▶  data/processed/
         │
         ▼
  Train Random Forest  ──▶  models/<date>_model.pkl
         │
         ▼
  Save metrics + combined validation report  ──▶  reports/
         │
         ▼
  Mark manifest as success
```

---

## Demo Results

The demo runs three days of data through the pipeline:

| Day | File | Outcome | Notes |
|---|---|---|---|
| 1 | `customer_churn_2026_05_29.csv` | ✅ Success | Model trained — accuracy 0.8016, F1 0.5823 |
| 2 | `customer_churn_2026_05_30.csv` | ❌ Rejected | Missing `Churn` column — pre-clean validation failed, training skipped |
| 3 | `customer_churn_2026_05_31.csv` | ✅ Success | Model trained — accuracy 0.7843, F1 0.5217 |

Day 2 corruption was intentional. It proves the pipeline catches bad data before it touches the model, writes a rejection report, and moves on to the next file without any manual intervention.

---

## Project Structure

```
ml-churn-data-pipeline/
├── data/
│   ├── raw/                    # Ingestion drop zone
│   ├── demo_daily_files/       # Pre-staged demo CSVs
│   ├── processed/              # Validated + cleaned output
│   └── rejected/               # Files that failed either validation gate
├── logs/
│   └── processed_files.json    # Idempotency manifest
├── models/                     # Versioned .pkl model artifacts
├── orchestration/
│   └── prefect_flow.py         # Prefect flow — polls every 20s (86400s in production)
├── reports/
│   ├── pre_clean/              # Schema validation reports (per file)
│   ├── post_clean/             # Post-cleaning validation reports (per file)
│   ├── combined/               # Single summary per file (both stages + overall_passed)
│   └── training/               # Accuracy, precision, recall, F1 (per model)
├── scripts/
│   ├── prepare_demo_data.py    # Splits source CSV into 3 daily files, corrupts Day 2
│   ├── reset_demo.sh           # Wipes runtime state for a clean re-run
│   └── run_demo_publisher.py   # Drops one CSV into data/raw/ every 20 seconds
└── src/
    ├── config.py               # Single source of truth for paths, columns, constants
    ├── ingest.py               # Finds next unprocessed CSV (sorted, deduped via manifest)
    ├── clean.py                # Cleaning logic (non-destructive, returns copy)
    ├── validate.py             # Both validation stages + report serialisation
    ├── train.py                # RandomForest training, versioned model + metrics output
    ├── state.py                # Reads/writes the processed-files manifest
    └── pipeline.py             # Composes all stages into one callable run_pipeline()
```

---

## Running the Demo

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Place `customer_churn_full.csv` in the project root (Telco Customer Churn dataset — not committed).

### Prepare the demo data

```bash
python -m scripts.prepare_demo_data
```

Splits the source file into three daily CSVs and corrupts Day 2.

### Run

Open two terminals.

**Terminal 1** — start the Prefect flow (polls every 20 seconds):
```bash
python -m orchestration.prefect_flow
```

**Terminal 2** — publish one file every 20 seconds:
```bash
python -m scripts.run_demo_publisher
```

Watch the pipeline process Day 1, reject Day 2, and process Day 3 automatically.

### Reset and re-run

```bash
bash scripts/reset_demo.sh
```

Clears all generated artefacts and re-stages the demo files.

---

## Validation Design

Two separate gates run at different points in the pipeline for different reasons.

**Pre-clean** checks whether the raw file is structurally usable at all — if the `Churn` column is missing there is nothing to clean or train on, so the file is rejected immediately without wasting resources.

**Post-clean** checks whether the cleaned data is actually fit for training — it catches issues like negative numeric values or a target column that ended up with only one class after cleaning.

| Stage | Checks |
|---|---|
| Pre-clean | Not empty, all 21 required columns present, `Churn` exists, not all null, values are `Yes`/`No` only |
| Post-clean | Minimum 100 rows, `Churn` has no nulls and both classes, `tenure`/`MonthlyCharges`/`TotalCharges` are numeric and non-negative |

Every validation run writes a JSON report. A combined summary (`overall_passed: true/false`) is written per file covering both stages.

---

## Model

Random Forest classifier (scikit-learn):

- 100 estimators, `class_weight="balanced"` to handle churn class imbalance
- 80/20 stratified train/test split, `random_state=42`
- Features one-hot encoded via `pd.get_dummies`, `customerID` and `ingestion_date` dropped before training
- One versioned `.pkl` artifact saved per source file (e.g. `models/customer_churn_2026_05_29_model.pkl`)
- Metrics (accuracy, precision, recall, F1, train/test row counts, feature count) written to `reports/training/`

---

## Idempotency

`logs/processed_files.json` is a running manifest of every file the pipeline has touched. On each Prefect run, the ingestion step reads this manifest and skips any file already listed — regardless of whether it succeeded or was rejected. This means the Prefect schedule can run continuously and will never double-process a file.

---

## Requirements

```
pandas
scikit-learn
joblib
prefect
pytest
```

Python 3.10+ required.