import pandas as pd
from rain.entity.config_entity import DataValidationConfig
from rain.entity.artifacts_entity import (DataIngestionArtifacts, DataValidationArtifacts)
from pandas import DataFrame
import sys, os, json
from rain.exceptions import rainPredictionException
from rain.logger import logging
from typing import Tuple, Union
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset



class DataValidation:
    def __init__(self, data_ingestion_artifacts:DataIngestionArtifacts,
                 data_validation_config:DataValidationConfig):
        self.data_ingestion_artifacts=data_ingestion_artifacts
        self.data_validation_config=data_validation_config


    def validate_schema_columns(self, df:DataFrame)->bool:
        try:
            if len(df.columns) == len(self.data_validation_config.SCHEMA_CONFIG["columns"]):
                validation_status=True
            else:
                validation_status=False
            return validation_status
        except Exception as e:
            raise rainPredictionException(e, sys)


    def validate_numerical_columns(self, df:DataFrame)->bool:
        try:
            validation_status = False
            for column in self.data_validation_config.SCHEMA_CONFIG["numerical_columns"]:
                if column in df.columns:
                    logging.info(f"numerical column - {column} not found in dataframe")
                else:
                    validation_status=True
            return validation_status
        except Exception as e:
            raise rainPredictionException(e, sys)

    def validate_categorical_columns(self, df:DataFrame)->bool:
        try:
            validation_status = False
            for column in self.data_validation_config.SCHEMA_CONFIG["categorical_columns"]:
                if column in df.columns:
                    logging.info(f"categorical_columns - {column} not found in dataframe")
                else:
                    validation_status=True
            return validation_status
        except Exception as e:
            raise rainPredictionException(e, sys)


    def validate_dataset_schema_columns(self)->Tuple[bool, bool]:
        try:
            train_schema_status = self.validate_schema_columns(self.train_set)
            test_schema_status = self.validate_schema_columns(self.test_set)
            return train_schema_status, test_schema_status
        except Exception as e:
            raise rainPredictionException(e, sys)


    def validate_dataset_numerical_columns(self)->Tuple[bool,bool]:
        try:
            train_numerical_columns_status = self.validate_numerical_columns(self.train_set)
            test_numerical_columns_status = self.validate_numerical_columns(self.test_set)
            return train_numerical_columns_status, test_numerical_columns_status
        except Exception as e:
            raise rainPredictionException(e, sys)

    def validate_dataset_categorical_columns(self)->Tuple[bool,bool]:
        try:
            train_categorical_columns_status = self.validate_categorical_columns(self.train_set)
            test_categorical_columns_status = self.validate_categorical_columns(self.test_set)
            return train_categorical_columns_status, test_categorical_columns_status
        except Exception as e:
            raise rainPredictionException(e, sys)


    def detect_dataset_drift(
            self, reference: DataFrame, production: DataFrame, get_ratio: bool = False) -> Union[bool, float]:
        try:
            data_drift_profile = Report(metrics=[DataDriftPreset(),])
            data_drift_profile.run(reference_data=reference, current_data=production)
            report = data_drift_profile.json()
            json_report = json.loads(report)

            data_drift_file_path = self.data_validation_config.DATA_DRIFT_FILE_PATH
            self.data_validation_config.UTILS.write_json_to_yaml_file(json_report, data_drift_file_path)

            n_features = []
            for i in json_report['metrics']:
                n_features.append(i['result']['number_of_columns'])
            n_features = n_features[0]

            n_drifted_features = []
            for i in json_report['metrics']:
                n_drifted_features.append(i['result']['number_of_drifted_columns'])
            n_drifted_features = n_drifted_features[0]

            status = []
            for i in json_report['metrics']:
                status.append(i['result']['dataset_drift'])
            status = status[0]

            if get_ratio:
                return n_drifted_features / n_features  # Calculating the drift ratio
            else:
                return status

        except Exception as e:
            raise rainPredictionException(e, sys)

    def initiate_data_validation(self)->DataValidationArtifacts:
        try:
            self.train_set = pd.read_csv(self.data_ingestion_artifacts.train_data_file_path)
            self.test_set = pd.read_csv(self.data_ingestion_artifacts.test_data_file_path)
            os.makedirs(self.data_validation_config.DATA_VALIDATION_ARTIFACTS_DIR, exist_ok=True)
            (train_schema_status, test_schema_status) = self.validate_dataset_schema_columns()
            (train_numerical_columns_status, test_numerical_columns_status) = self.validate_dataset_numerical_columns()
            (train_categorical_columns_status, test_categorical_columns_status) = self.validate_dataset_categorical_columns()
            drift = self.detect_dataset_drift(self.train_set, self.test_set)
            drift_status = None
            if (train_schema_status is True and
                test_schema_status is True and
                train_numerical_columns_status is True and
                test_numerical_columns_status is True and
                train_categorical_columns_status is True and
                test_categorical_columns_status is True and
                drift is False):
                drift_status == False
            else:
                drift_status == True
            data_validation_artifacts = DataValidationArtifacts(
                data_drift_file_path=self.data_validation_config.DATA_DRIFT_FILE_PATH,
                validation_status=drift_status
            )
            return data_validation_artifacts
        except Exception as e:
            raise rainPredictionException(e, sys)