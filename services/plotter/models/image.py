from pydantic import BaseModel
from typing import List, Dict

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
    graphs: Dict[int, GraphModel] = {0: GraphModel()}
    plots: Dict[int, PlotModel] = {0: PlotModel()}

    class Config:
        arbitrary_types_allowed = True
