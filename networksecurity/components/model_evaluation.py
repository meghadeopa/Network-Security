import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    DataValidationArtifact,
    ModelTrainerArtifact,
    ModelEvaluationArtifact,
)
from networksecurity.entity.config_entity import ModelEvaluationConfig
from networksecurity.utils.main_utils.utils import load_object, write_yaml_file
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.constants.training_pipeline import TARGET_COLUMN

import pandas as pd


class ModelEvaluation:
    def __init__(self,
                 model_eval_config: ModelEvaluationConfig,
                 data_validation_artifact: DataValidationArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):
        try:
            self.model_eval_config = model_eval_config
            self.data_validation_artifact = data_validation_artifact
            self.model_trainer_artifact = model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        """
        Compares the newly trained model against the current best model
        (saved locally in final_model/model.pkl) on the validation/test data.

        - If no current best model exists (first run), the new model is accepted.
        - Otherwise the new model is accepted only if its test F1 beats the
          current best by at least `change_threshold`.
        """
        try:
            # 1. Load the held-out test data and split features/target
            test_df = pd.read_csv(self.data_validation_artifact.valid_test_file_path)
            x_test = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            y_test = test_df[TARGET_COLUMN].replace(-1, 0)

            # 2. Load the newly trained model (preprocessor + model bundled in NetworkModel)
            trained_model_path = self.model_trainer_artifact.trained_model_file_path
            trained_model = load_object(trained_model_path)

            # 3. Metric for the new model on test data
            y_pred_trained = trained_model.predict(x_test)
            trained_metric = get_classification_score(y_true=y_test, y_pred=y_pred_trained)

            best_model_path = self.model_eval_config.best_model_path

            # 4. First-run case: no current best to compare against -> accept
            if not os.path.exists(best_model_path):
                logging.info("No existing best model found. Accepting trained model by default.")
                model_evaluation_artifact = ModelEvaluationArtifact(
                    is_model_accepted=True,
                    improved_accuracy=trained_metric.f1_score,
                    best_model_path=None,
                    trained_model_path=trained_model_path,
                    train_model_metric_artifact=trained_metric,
                    best_model_metric_artifact=None,
                )
                self._write_report(model_evaluation_artifact)
                return model_evaluation_artifact

            # 5. Compare against the current best model
            #    NOTE: final_model/model.pkl is the raw estimator (no preprocessor),
            #    so we transform x_test with the trained model's preprocessor first.
            best_model = load_object(best_model_path)
            x_test_transformed = trained_model.preprocessor.transform(x_test)
            y_pred_best = best_model.predict(x_test_transformed)
            best_metric = get_classification_score(y_true=y_test, y_pred=y_pred_best)

            improved_accuracy = trained_metric.f1_score - best_metric.f1_score
            is_accepted = improved_accuracy > self.model_eval_config.change_threshold

            logging.info(
                f"Trained F1: {trained_metric.f1_score:.4f}, "
                f"Best F1: {best_metric.f1_score:.4f}, "
                f"Improvement: {improved_accuracy:.4f}, "
                f"Accepted: {is_accepted}"
            )

            model_evaluation_artifact = ModelEvaluationArtifact(
                is_model_accepted=is_accepted,
                improved_accuracy=improved_accuracy,
                best_model_path=best_model_path,
                trained_model_path=trained_model_path,
                train_model_metric_artifact=trained_metric,
                best_model_metric_artifact=best_metric,
            )
            self._write_report(model_evaluation_artifact)
            return model_evaluation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def _write_report(self, artifact: ModelEvaluationArtifact):
        """Write a small YAML summary of the evaluation decision."""
        try:
            os.makedirs(self.model_eval_config.model_evaluation_dir, exist_ok=True)
            report_path = os.path.join(
                self.model_eval_config.model_evaluation_dir, "evaluation_report.yaml"
            )
            report = {
                "is_model_accepted": bool(artifact.is_model_accepted),
                "improved_accuracy": float(artifact.improved_accuracy),
                "trained_model_f1": float(artifact.train_model_metric_artifact.f1_score),
                "best_model_f1": (
                    float(artifact.best_model_metric_artifact.f1_score)
                    if artifact.best_model_metric_artifact else None
                ),
                "change_threshold": float(self.model_eval_config.change_threshold),
            }
            write_yaml_file(file_path=report_path, content=report)
        except Exception as e:
            raise NetworkSecurityException(e, sys)