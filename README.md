# 🔐 Network Security — Phishing Website Detection

An end-to-end MLOps pipeline that classifies websites as **phishing** or **legitimate**
from 30 URL- and page-based features. The project is structured as a modular,
stage-based pipeline with experiment tracking, a model-promotion gate, a REST API
for serving, and artifact/model syncing to AWS S3.

---

## Project Overview

This is not a single notebook — it is a modular pipeline where each stage produces a
typed *artifact* that feeds the next stage. The pipeline covers data ingestion from
MongoDB, validation with drift detection, preprocessing, model training with
experiment tracking, an evaluation gate that decides whether a new model is good
enough to promote, and conditional pushing of the promoted model to a serving
location and S3.

---

## Architecture

MongoDB Atlas

│

▼

Data Ingestion ──► Data Validation ──► Data Transformation ──► Model Trainer

(fetch + split)   (schema +           (KNN imputer +          (GridSearchCV over

drift detection)     RobustScaler)           multiple models,

MLflow tracking)

│

▼

Model Evaluation

(compare vs current

best; accept/reject)

│

▼

Model Pusher

(promote + S3 sync ONLY

if model was accepted)
All artifacts and the promoted model are synced to AWS S3 each run.

A FastAPI app exposes /train and /predict endpoints for serving.

---

## Dataset

| Property | Details |
|---|---|
| Source | UCI ML Repository — Phishing Websites |
| Records | ~11,000 websites |
| Features | 30 URL/page-based features + 1 target |
| Target | `Result` (phishing vs legitimate) |

Representative features: `having_IP_Address`, `URL_Length`, `SSLfinal_State`,
`age_of_domain`, `Page_Rank`, `DNSRecord`, and others.

---

## Pipeline Components

**1. Data Ingestion** — Connects to MongoDB Atlas, pulls the collection into a
DataFrame, writes a timestamped feature-store CSV, and splits into train/test.

**2. Data Validation** — Checks the column count against a schema and runs a
per-feature Kolmogorov–Smirnov test to detect distribution drift between train and
test. Uses a drift *tolerance* (fails only if the share of drifted features exceeds a
threshold) and writes a drift report.

**3. Data Transformation** — Builds an sklearn `Pipeline` with a `KNNImputer` followed
by a `RobustScaler`, fits it on train only, transforms both sets, and saves the fitted
preprocessor for consistent train/serve transformation.

**4. Model Trainer** — Runs `GridSearchCV` across several classifiers (Random Forest,
Decision Tree, Gradient Boosting, Logistic Regression, AdaBoost), selects the best by
F1 score, and logs parameters and metrics to **MLflow on DagsHub**. The fitted model
is bundled with its preprocessor in a `NetworkModel` wrapper for inference.

**5. Model Evaluation** — Compares the newly trained model's test F1 against the
current best model in `final_model/`. Accepts the new model only if it improves on the
current best by a configurable threshold; on the first run (no incumbent), it accepts
by default. Writes an evaluation report.

**6. Model Pusher** — Acts on the evaluation decision: if the model was **accepted**,
it promotes the model to the serving location (`final_model/`) and syncs it to S3. If
**rejected**, it does nothing and the current production model is retained.

---

## Serving (FastAPI)

`app.py` exposes:
- `GET /train` — runs the full training pipeline.
- `POST /predict` — accepts a CSV upload, returns predictions rendered as an HTML table.

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Web framework | FastAPI |
| Database | MongoDB Atlas |
| ML | scikit-learn |
| Experiment tracking | MLflow on DagsHub |
| Cloud storage | AWS S3 |
| Config management | Python dataclasses |

---

## How to Run

```bash
# install
pip install -r requirements.txt

# set environment variables in a .env file:
#   MONGO_DB_URL, MLFLOW_TRACKING_URI, MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD

# run the full pipeline
python main.py

# or serve the API
python app.py   # then open http://localhost:8000/docs
```

---

## Model Performance

| Metric | Value |
|---|---|
| Best model | Random Forest |
| Test F1 | ~0.97 |
| Test precision | ~0.97 |
| Test recall | ~0.98 |

(Metrics are logged per run to MLflow on DagsHub.)


---

## Author

Megha Deopa
