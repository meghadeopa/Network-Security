import os
import mlflow
from dotenv import load_dotenv

load_dotenv()

print("URI:", os.getenv("MLFLOW_TRACKING_URI"))
print("User:", os.getenv("MLFLOW_TRACKING_USERNAME"))
print("Token loaded:", "Yes" if os.getenv("MLFLOW_TRACKING_PASSWORD") else "No ❌")

os.environ["MLFLOW_TRACKING_URI"] = os.getenv("MLFLOW_TRACKING_URI")
os.environ["MLFLOW_TRACKING_USERNAME"] = os.getenv("MLFLOW_TRACKING_USERNAME")
os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("MLFLOW_TRACKING_PASSWORD")

with mlflow.start_run(run_name="connection_test"):
    mlflow.log_metric("test_metric", 1.0)

print("✅ Success! Check your DagsHub experiments page.")