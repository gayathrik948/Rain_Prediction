import os
from rain.entity.config_entity import DataTransformationConfig
from rain.entity.artifacts_entity import (DataIngestionArtifacts, DataTransformationArtifacts)
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from category_encoders.binary import BinaryEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from rain.exceptions import rainPredictionException
import sys
from pandas import DataFrame
import numpy as np
from rain.components.output_label_encoding import TargetValueMapping

from rain.logger import logging

class DataTransformation:
    def __init__(self,
                 data_ingestion_artifacts: DataIngestionArtifacts,
                 data_transformation_config: DataTransformationConfig):
        self.data_ingestion_artifacts = data_ingestion_artifacts
        self.data_transformation_config = data_transformation_config

        self.train_set = pd.read_csv(self.data_ingestion_artifacts.train_data_file_path)
        self.test_set = pd.read_csv(self.data_ingestion_artifacts.test_data_file_path)
        logging.info(f"{self.train_set.columns}")
        logging.info(f"{self.test_set.columns}")


    def get_data_transformation_object(self)->object:
        try:
            columns = self.data_transformation_config.SCHEMA_CONFIG["columns"]
            numerical_columns = self.data_transformation_config.SCHEMA_CONFIG["numerical_columns"]
            print(numerical_columns)
            onehot_columns = self.data_transformation_config.SCHEMA_CONFIG["onehot_columns"]
            print(onehot_columns )
            binary_columns = self.data_transformation_config.SCHEMA_CONFIG["binary_columns"]
            print(binary_columns)
            output_columns = self.data_transformation_config.SCHEMA_CONFIG["target_column"]
            print(output_columns)

            numeric_transformer = StandardScaler()
            simple_imputer = SimpleImputer(strategy="constant", fill_value=0)
            oh_transformer = OneHotEncoder(handle_unknown="ignore")
            binary_transformer = BinaryEncoder()

            preprocessor = ColumnTransformer(
                [("OnHotEncoder", oh_transformer, onehot_columns),
                 ("StandardScaler", numeric_transformer, numerical_columns),
                 ("BinaryEncoder", binary_transformer, binary_columns)])
            return preprocessor
        except Exception as e:
            raise rainPredictionException(e, sys)



    @staticmethod
    def outlier_capping(col, df:DataFrame)->DataFrame:
        try:
            percentile25 = df[col].quantile(0.25)
            percentile75 = df[col].quantile(0.75)
            iqr = percentile75-percentile25
            upper_limit = percentile75+1.5 * iqr
            lower_limit = percentile25-1.5 * iqr
            df.loc[(df[col] > upper_limit), col]=upper_limit
            df.loc[(df[col] < lower_limit), col]=lower_limit
            return df
        except Exception as e:
            raise rainPredictionException(e, sys)


    def initiate_data_transformation(self)->DataTransformationArtifacts:
        try:
            os.makedirs(self.data_transformation_config.DATA_TRANSFORMATION_ARTIFACT_DIR, exist_ok=True)

            preprocessor = self.get_data_transformation_object()

            target_column = self.data_transformation_config.SCHEMA_CONFIG["target_column"]

            numerical_columns = self.data_transformation_config.SCHEMA_CONFIG["numerical_columns"]
            continious_columnns = [feature for feature in numerical_columns if len(self.train_set[feature].unique())>=25]
            [self.outlier_capping(col, self.train_set) for col in continious_columnns]
            [self.outlier_capping(col, self.test_set) for col in continious_columnns]

            input_feature_train_df = self.train_set.drop(columns=[target_column], axis=1).reset_index(drop=True)
            input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df)
            target_feature_train_df = self.train_set[target_column].reset_index(drop=True)
            target_feature_train_df = target_feature_train_df.replace(TargetValueMapping().to_dict())
            target_feature_train_arr = np.reshape(target_feature_train_df, (-1, 1))
            train_arr = np.c_[input_feature_train_arr.todense(), np.array(target_feature_train_arr)]
            os.makedirs(self.data_transformation_config.TRANSFORMED_TRAIN_ARTIFACT_DATA_DIR, exist_ok=True)
            transformed_train_file = self.data_transformation_config.UTILS.save_numpy_array_data(
                self.data_transformation_config.TRANSFORMED_TRAIN_ARTIFACT_DATA_FILE_NAME, train_arr
            )


            input_feature_test_df = self.test_set.drop(columns=[target_column], axis=1).reset_index(drop=True)
            input_feature_test_arr = preprocessor.transform(input_feature_test_df)
            target_feature_test_df= self.test_set[target_column].reset_index(drop=True)
            target_feature_test_df = target_feature_test_df.replace(TargetValueMapping().to_dict())
            target_feature_test_arr = np.reshape(target_feature_test_df, (-1, 1))
            test_arr = np.c_[input_feature_test_arr.todense(), np.array(target_feature_test_arr)]
            os.makedirs(self.data_transformation_config.TRANSFORMED_TEST_ARTIFACT_DATA_DIR, exist_ok=True)
            transformed_test_file = self.data_transformation_config.UTILS.save_numpy_array_data(
                self.data_transformation_config.TRANSFORMED_TEST_ARTIFACT_DATA_FILE_NAME, test_arr
            )


            preprocessor_file = self.data_transformation_config.UTILS.save_object(
                self.data_transformation_config.PREPROCESSOR_OBJECT_ARTIFACT_FILE_NAME, preprocessor)
            data_transformation_artifacts = DataTransformationArtifacts(
                preprocessor_object_file_path=preprocessor_file,
                transformed_train_data_file_path=transformed_train_file,
                transformed_test_data_file_path=transformed_test_file
            )
            return data_transformation_artifacts
        except Exception as e:
            raise rainPredictionException(e, sys)