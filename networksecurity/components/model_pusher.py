import os
import sys
import shutil

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    ModelEvaluationArtifact,
    ModelPusherArtifact,
)
from networksecurity.entity.config_entity import ModelPusherConfig
from networksecurity.cloud.s3_syncer import S3Sync
from networksecurity.constants.training_pipeline import TRAINING_BUCKET_NAME


class ModelPusher:
    """
    Promotes a trained model only if model evaluation accepted it.

    - If accepted: copy the trained model into the serving location (final_model/)
      and sync final_model/ to S3.
    - If rejected: do nothing; the current production model stays in place.
    """

    def __init__(self,
                 model_pusher_config: ModelPusherConfig,
                 model_evaluation_artifact: ModelEvaluationArtifact):
        try:
            self.model_pusher_config = model_pusher_config
            self.model_evaluation_artifact = model_evaluation_artifact
            self.s3_sync = S3Sync()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            if not self.model_evaluation_artifact.is_model_accepted:
                logging.info("Model was not accepted by evaluation. Skipping push; "
                             "current production model is retained.")
                return ModelPusherArtifact(
                    saved_model_path=None,
                    model_file_path=self.model_pusher_config.model_file_path,
                )

            # Accepted: copy the trained model into the serving location
            trained_model_path = self.model_evaluation_artifact.trained_model_path
            os.makedirs(self.model_pusher_config.model_dir, exist_ok=True)
            shutil.copy(trained_model_path, self.model_pusher_config.model_file_path)
            logging.info(f"Accepted model promoted to {self.model_pusher_config.model_file_path}")

            # Sync the serving model dir to S3
            aws_bucket_url = (
                f"s3://{TRAINING_BUCKET_NAME}/final_model/"
                f"{self.model_pusher_config.timestamp}"
            )
            self.s3_sync.sync_folder_to_s3(
                folder=self.model_pusher_config.model_dir,
                aws_bucket_url=aws_bucket_url,
            )
            logging.info(f"Promoted model synced to {aws_bucket_url}")

            return ModelPusherArtifact(
                saved_model_path=aws_bucket_url,
                model_file_path=self.model_pusher_config.model_file_path,
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)