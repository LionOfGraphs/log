from pydantic import BaseModel
from typing import List, Dict
from models.plot import PlotModel


class GraphModel(BaseModel):
    graphID: int = 0
    plots: List[PlotModel] = [PlotModel()]


class LayoutModel(BaseModel):
    graphs: List[GraphModel] = [GraphModel()]
