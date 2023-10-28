from pydantic import BaseModel
from typing import List, Optional

from models.figure import FigureModel
from models.layout import LayoutModel
from models.plot import PlotModel


class GraphModel(BaseModel):
    graphID: int = 0
    plot_id_list: List[int] = [0]


class ImageModel(BaseModel):
    save: bool = True
    format: str = "png"
    figure: FigureModel = FigureModel()
    layout: LayoutModel = LayoutModel()
    graphs: List[GraphModel] = [GraphModel()]
    plots: Optional[List[PlotModel]] = [PlotModel()]

    class Config:
        arbitrary_types_allowed = True

