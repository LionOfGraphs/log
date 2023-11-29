from pydantic import BaseModel, List
from pandas import DataFrame


class Plot(BaseModel):
    id: int 
    data: DataFrame = None
    xlabel: str = "x"
    ylabel: str = "y"


class Graph(BaseModel):
    plot: List[Plot] = [Plot()]


class Image(BaseModel):
    pass

