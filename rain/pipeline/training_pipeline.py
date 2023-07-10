from rain.entity.config_entity import (DataIngestionConfig,
DataValidationConfig, DataTransformationConfig, ModelTrainerConfig)
from rain.entity.artifacts_entity import (DataIngestionArtifacts,
DataValidationArtifacts, DataTransformationArtifacts, ModelTrainerArtifacts)
from rain.configuration.mongo_operations import MongoDBOperation
from rain.components.data_ingestion import DataIngestion
from rain.components.data_validation import DataValidation
from rain.components.data_transformation import DataTransformation
from rain.components.model_trainer import ModelTrainer
from rain.exceptions import rainPredictionException
import sys


class TrainingPipeline:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        self.data_validation_config = DataValidationConfig()
        self.data_transformation_config = DataTransformationConfig()
        self.model_trainer_config = ModelTrainerConfig()
        self.mongo_op = MongoDBOperation()


    def start_data_ingestion(self) -> DataIngestionArtifacts:
        try:
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config,
                                           mongo_op=self.mongo_op)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            return data_ingestion_artifact
        except Exception as e:
            raise rainPredictionException(e, sys)


    def start_data_validation(self, data_ingestion_artifacts:DataIngestionArtifacts)->DataValidationArtifacts:
        try:
            data_validation = DataValidation(data_validation_config=self.data_validation_config,
                                             data_ingestion_artifacts=data_ingestion_artifacts)
            data_validation_artifacts = data_validation.initiate_data_validation()
            return data_validation_artifacts
        except Exception as e:
            raise rainPredictionException(e, sys)

    def start_data_transformation(self,
                                  data_ingestion_artifacts: DataIngestionArtifacts) -> DataTransformationArtifacts:
        try:
            data_transformation = DataTransformation(data_transformation_config=self.data_transformation_config,
                                                     data_ingestion_artifacts=data_ingestion_artifacts)
            data_transformation_artifacts = data_transformation.initiate_data_transformation()
            return data_transformation_artifacts
        except Exception as e:
            raise rainPredictionException(e, sys)

    def start_model_trainer(self, data_transformation_artifacts: DataTransformationArtifacts) -> ModelTrainerArtifacts:
        try:
            model_trainer = ModelTrainer(data_transformation_artifact=data_transformation_artifacts,
                                         model_trainer_config=self.model_trainer_config)
            model_trainer_artifacts = model_trainer.initiate_model_trainer()
            return model_trainer_artifacts
        except Exception as e:
            raise rainPredictionException(e, sys)



    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifacts=data_ingestion_artifact)
            data_transformation_artifacts = self.start_data_transformation(data_ingestion_artifacts=data_ingestion_artifact)
            model_trainer_artifacts = self.start_model_trainer(
                data_transformation_artifacts=data_transformation_artifacts)

        except Exception as e:
            raise rainPredictionException(e, sys)
