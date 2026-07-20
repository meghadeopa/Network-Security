# 🔐 Network Security — Phishing Website Detection

An end-to-end MLOps pipeline that classifies websites as **phishing** or **legitimate**
from 30 URL- and page-based features. The project covers the full lifecycle: a modular,
stage-based training pipeline with experiment tracking and a model-promotion gate, a
REST API for serving, artifact/model syncing to AWS S3, and **automated CI/CD
deployment to AWS EC2 via Docker, ECR, and GitHub Actions**.

---

## Project Overview

This is not a single notebook — it is a modular pipeline where each stage produces a
typed *artifact* that feeds the next stage. The pipeline covers data ingestion from
MongoDB, validation with drift detection, preprocessing, model training with
experiment tracking, an evaluation gate that decides whether a new model is good
enough to promote, and conditional pushing of the promoted model to a serving
location and S3. Every push to `main` triggers a CI/CD pipeline that builds a Docker
image, pushes it to Amazon ECR, and deploys it to an EC2 instance where the API is
served.

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

### Deployment Pipeline (CI/CD)

git push to main
│
▼
GitHub Actions
│
├─► Continuous Integration  — lint & test checks
│
├─► Continuous Delivery     — build Docker image ► push to Amazon ECR
│
└─► Continuous Deployment   — self-hosted runner on EC2 pulls the image,
stops the previous container, and starts the
new one (FastAPI served on port 8080)

Runtime configuration (database URI, MLflow credentials) is injected into the
container as environment variables from GitHub Actions secrets — no credentials are
baked into the image or the repository.

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

In deployment, the app runs inside a Docker container on AWS EC2, mapped to
port 8080.

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
| Containerization | Docker |
| Container registry | Amazon ECR |
| Compute / hosting | AWS EC2 (self-hosted GitHub Actions runner) |
| CI/CD | GitHub Actions |
| Config management | Python dataclasses |

---

## How to Run Locally

```bash
# install
pip install -r requirements.txt

# set environment variables in a .env file:
#   MONGO_DB_URL, MLFLOW_TRACKING_URI, MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD

# run the full pipeline
python main.py

# or serve the API
python app.py   # then open http://localhost:8080/docs
```

## How Deployment Works

Every push to `main` (except README-only changes) triggers `.github/workflows/main.yml`:
the workflow builds the Docker image, pushes it to Amazon ECR, and a self-hosted
runner on the EC2 instance pulls the new image, replaces the running container, and
serves the API on port 8080. AWS credentials and runtime secrets are stored as GitHub
Actions secrets.

---

## Model Performance

| Metric | Value |
|---|---|
| Best model | Random Forest |
| Test F1 | ~0.977 |
| Test precision | ~0.971 |
| Test recall | ~0.978 |

Recall is kept at or above precision by design: in phishing detection a missed
phishing site (false negative) is more costly than a false alarm. Metrics are logged
per run to MLflow on DagsHub.

---

## Design Decisions

A few deliberate choices worth noting:
- **F1 for model selection** — the task is binary classification, so models are ranked
  by F1 rather than a regression metric.
- **Drift tolerance over hard-fail** — on a random train/test split a few features
  drift by chance, so validation fails only when the *share* of drifted features
  exceeds a threshold, rather than on any single feature.
- **Evaluation gate before promotion** — a newly trained model replaces the production
  model only if it improves on it, preventing silent regression.
- **MLflow logs metrics only** — model artifacts are stored locally and in S3 rather
  than uploaded to the MLflow/DagsHub artifact store (which was slow for large models).
- **Secrets injected at runtime** — the Docker image contains no credentials; all
  runtime configuration is passed as environment variables from CI/CD secrets.
- **Class-imbalance handling evaluated but not applied** — the dataset is
  near-balanced, so SMOTE was deemed unnecessary.

---

## Author

Megha Deopa