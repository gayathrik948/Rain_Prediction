import sys
from typing import Dict
from pandas import DataFrame
import pandas as pd
from rain.constants import *
from rain.exceptions import rainPredictionException
from rain.entity.artifacts_entity import ModelTrainerArtifacts
from rain.utils.main_utils import MainUtils

class RainPredictionData:
    def __init__(self,
                 Date,
                 Location,
                 MinTemp,
                 MaxTemp,
                 Rainfall,
                 WindGustDir,
                 WindGustSpeed,
                 WindDir9am,
                 WindDir3pm,
                 WindSpeed9am,
                 WindSpeed3pm,
                 Humidity9am,
                 Humidity3pm,
                 Pressure9am,
                 Pressure3pm,
                 Cloud9am,
                 Cloud3pm,
                 Temp9am,
                 Temp3pm,
                 RainToday,
                 RISK_MM,
                 ):
        self.Date= Date
        self.Location =  Location
        self.MinTemp= MinTemp
        self.MaxTemp = MaxTemp
        self.Rainfall = Rainfall
        self.WindGustDir = WindGustDir
        self.WindGustSpeed = WindGustSpeed
        self.WindDir9am = WindDir9am
        self.WindDir3pm = WindDir3pm
        self.WindSpeed9am = WindSpeed9am
        self.WindSpeed3pm = WindSpeed3pm
        self.Humidity9am = Humidity9am
        self.Humidity3pm = Humidity3pm
        self.Pressure9am = Pressure9am
        self.Pressure3pm = Pressure3pm
        self.Cloud9am = Cloud9am
        self.Cloud3pm = Cloud3pm
        self.Temp9am = Temp9am
        self.Temp3pm = Temp3pm
        self.RainToday = RainToday
        self.RISK_MM = RISK_MM



    def get_data(self)->Dict:
        try:
            input_data = {
                "Date": [self.Date],
                "Location": [self.Location],
                "MinTemp": [self.MinTemp],
                "MaxTemp": [self.MaxTemp],
                "Rainfall": [self.Rainfall],
                "WindGustDir": [self.WindGustDir],
                "WindGustSpeed": [self.WindGustSpeed],
                "WindDir9am": [self.WindDir9am],
                "WindDir3pm": [self.WindDir3pm],
                "WindSpeed9am": [self.WindSpeed9am],
                "WindSpeed3pm": [self.WindSpeed3pm],
                "Humidity9am": [self.Humidity9am],
                "Humidity3pm": [self.Humidity3pm],
                "Pressure9am": [self.Pressure9am],
                "Pressure3pm": [self.Pressure3pm],
                "Cloud9am": [self.Cloud9am],
                "Cloud3pm": [self.Cloud3pm],
                "Temp9am": [self.Temp9am],
                "Temp3pm": [self.Temp3pm],
                "RainToday": [self.RainToday],
                 "RISK_MM": [self.RISK_MM]
            }
            return input_data
        except Exception as e:
            raise rainPredictionException(e, sys)

    def get_input_data_frame(self) -> DataFrame:
        try:
            input_dict = self.get_data()
            return pd.DataFrame(input_dict)
        except Exception as e:
            raise rainPredictionException(e, sys)



class CostPredictor:


    def predict(self, X)->float:
        try:
            utils = MainUtils()
            trained_model = ModelTrainerArtifacts()
            best_model = utils.load_object(trained_model.trained_model_file_path)
            result = best_model.predict(X)
            return result
        except Exception as e:
            raise rainPredictionException(e, sys)