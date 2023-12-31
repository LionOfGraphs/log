from typing import List
from pandas import DataFrame, read_csv

from models.data import DataModel
from utils.exceptions import InvalidRequestError

from io import BytesIO


def validate_data(dataList: List[DataModel], rawData: bytes = None) -> None:
    for data in dataList:
        if data.datatype == "file":
            if rawData is None:
                raise Exception("Expected file for file datatype.")

            dataframe = read_csv(BytesIO(rawData), sep=",", index_col=0)
            dataframe = dataframe.rename(data.column_names, axis="columns")

            dataframe = validate_dataframe(dataframe=dataframe)

            data.dataframe = dataframe
            print(dataframe)
        elif data.datatype == "Function":
            validate_latex(data.function)
        else:
            raise Exception("Invalid File Type")


def validate_dataframe(dataframe: DataFrame) -> DataFrame:
    """Validates input data"""
    data_nulls = dataframe.isnull()
    if data_nulls.any().any():
        raise InvalidRequestError("Found NaN value in provided data")

    for col in dataframe.columns:
        dataframe[col] = dataframe[col].astype(float)

    index = dataframe.index.values
    if not len(index) == len(set(index)):
        raise InvalidRequestError("Found duplicated entry in provided data")

    return dataframe


def validate_latex(function: str) -> str:
    return function
