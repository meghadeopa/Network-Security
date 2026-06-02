# 🔐 Network Security — Phishing Website Detection

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100-green)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![AWS](https://img.shields.io/badge/AWS-EC2-orange)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black)

## 📌 Project Overview

An end-to-end **MLOps project** that detects whether a website is a **phishing website** (fake/dangerous) or a **legitimate website** using Machine Learning.

The system is not just a notebook, it is a complete **production-grade application** with:
- Automated data pipeline from MongoDB
- Data validation with drift detection
- Model training with automatic best model selection
- REST API built with FastAPI
- Docker containerisation
- Deployed on AWS EC2 via GitHub Actions CI/CD

---------------------------------------------------------------------------------------------------------------------------

## 🏗️ Project Architecture

MongoDB Atlas
↓
Data Ingestion → Data Validation → Data Transformation
↓                ↓                   ↓
Fetch Data      Schema Check        KNN Imputer
Split Train/    Drift Detection     SMOTETomek
Test            Column Check        RobustScaler
Save preprocessing.pkl
↓
Model Trainer
(Best Model Selection)
↓
Model Evaluation
(Accuracy Threshold Check)
↓
Model Pusher → AWS S3
↓
FastAPI Application
(Deployed on AWS EC2)

-----------------------------------------------------------------------------------------------------------------------------

## 📊 Dataset

| Property | Details |

| Source | UCI ML Repository — Phishing Websites |
| Total Records | 11,055 websites |
| Total Features | 30 input features + 1 target |
| Target | Result: 1 = Phishing, -1 = Legitimate |
| Phishing websites | 6,157 (55.7%) |
| Legitimate websites | 4,898 (44.3%) |
| Missing Values | Zero |

### Key Features Used
- `having_IP_Address` — IP instead of domain name
- `URL_Length` — suspicious URL length
- `SSLfinal_State` — valid SSL certificate check
- `age_of_domain` — how old the domain is
- `Page_Rank` — Google page rank
- `DNSRecord` — DNS record existence
- And 24 more URL and page-based features

----------------------------------------------------------------------------------------------------------------------------

## 🧩 Pipeline Components

### 1. Data Ingestion
- Connects to MongoDB Atlas database
- Fetches all website records
- Exports to Feature Store as CSV with timestamp
- Splits into train.csv (80%) and test.csv (20%)

### 2. Data Validation
- Validates number of columns matches schema
- Checks all numerical columns exist
- Detects data drift using statistical tests
- Generates drift report YAML file

### 3. Data Transformation
- Handles missing values using **KNN Imputer** (K=3)
- Handles class imbalance using **SMOTETomek**
- Scales features using **RobustScaler**
- Saves preprocessing pipeline as preprocessing.pkl
- Outputs train.npy and test.npy arrays

### 4. Model Trainer
- Loads transformed numpy arrays
- Trains multiple ML models via Model Factory
- Selects best model above accuracy threshold
- Saves model.pkl with embedded preprocessor

### 5. Model Evaluation
- Compares new model vs existing production model
- Accepts model only if accuracy improves
- Prevents model degradation in production

### 6. Model Pusher
- Pushes accepted model to AWS S3 bucket
- Updates final_model directory
- Makes model available for API serving

----------------------------------------------------------------------------------------------------------------------------

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.10 |
| Web Framework | FastAPI |
| Database | MongoDB Atlas |
| ML Libraries | Scikit-learn, XGBoost, Imbalanced-learn |
| Data Processing | Pandas, NumPy |
| Containerisation | Docker |
| Cloud | AWS EC2, AWS ECR, AWS S3 |
| CI/CD | GitHub Actions |
| Logging | Python logging module |
| Config Management | Python dataclasses |

-----------------------------------------------------------------------------------------------------------------------------

## 📁 Project Structure

Network-Security/
├── .github/
│   └── workflows/
│       └── main.yml          # GitHub Actions CI/CD
├── networksecurity/
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_transformation.py
│   │   ├── model_trainer.py
│   │   ├── model_evaluation.py
│   │   └── model_pusher.py
│   ├── entity/
│   │   ├── config_entity.py
│   │   └── artifact_entity.py
│   ├── exception/
│   │   └── exception.py
│   ├── logging/
│   │   └── logger.py
│   ├── pipeline/
│   │   └── training_pipeline.py
│   └── utils/
│       └── main_utils.py
├── data_schema/
│   └── schema.yaml
├── final_model/
│   ├── model.pkl
│   └── preprocessor.pkl
├── app.py                    # FastAPI application
├── main.py                   # Training pipeline runner
├── push_data.py              # MongoDB data pusher
├── Dockerfile
├── requirements.txt
├── setup.py
└── README.md

--------------------------------------------------------------------------------------------------------------------------

## 📈 Model Performance

| Metric | Value |
|---|---|
| Algorithm | [Add after training completes] |
| Training Accuracy | [Add after training completes] |
| Test Accuracy | [Add after training completes] |
| F1 Score | [Add after training completes] |

----------------------------------------------------------------------------------------------------------------------------

## 🎯 Key Learnings

- Building modular, production-grade ML pipelines
- ETL pipeline from CSV to MongoDB to Feature Store
- Data validation and drift detection with Evidently
- Handling class imbalance with SMOTETomek
- FastAPI for ML model serving
- Docker containerisation of ML applications
- AWS ECR + EC2 deployment
- GitHub Actions for CI/CD automation

-----------------------------------------------------------------------------------------------------------------------------

## 👩‍💻 Author

**Megha Deopa**
MBA in Artificial Intelligence & Machine Learning

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/megha-deopa1505/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/meghadeopa)

---

## 📄 License

This project is for educational purposes.
