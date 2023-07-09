from rain.entity.config_entity import DataIngestionConfig
from rain.entity.artifacts_entity import DataIngestionArtifacts
from rain.configuration.mongo_operations import MongoDBOperation
from rain.components.data_ingestion import DataIngestion
from rain.exceptions import rainPredictionException
import sys


class TrainingPipeline:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        self.mongo_op = MongoDBOperation()


    def start_data_ingestion(self) -> DataIngestionArtifacts:
        try:
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config,
                                           mongo_op=self.mongo_op)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            return data_ingestion_artifact
        except Exception as e:
            raise rainPredictionException(e, sys)

    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()

        except Exception as e:
            raise rainPredictionException(e, sys)
