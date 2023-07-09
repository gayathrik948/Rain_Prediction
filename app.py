from rain.configuration.mongo_operations import MongoDBOperation
import pandas as pd
from rain.constants import *
from rain.exceptions import rainPredictionException
import sys



if __name__ == "__main__":
    try:
        df = pd.read_csv("weatherAUS.csv")
        mongo_op = MongoDBOperation()
        mongo_op.insert_dataframe_as_record(df, DB_NAME, COLLECTION_NAME)
    except Exception as e:
        raise rainPredictionException(e, sys) from e