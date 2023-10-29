from typing import List, Literal, Optional
from matplotlib.colors import Colormap, Normalize
from matplotlib.markers import MarkerStyle
from models.kwargs import KwargsCollectionModel, KwargsLine2DModel
from pandas import DataFrame
from pydantic import BaseModel


class PlotModel(BaseModel):
    plotID: int = 0
    plotType: str = "LinePlotModel"

    class Config:
        arbitrary_types_allowed = True


class BasicPlotModel(PlotModel):
    pass


class ArraysFieldsPlotModel(PlotModel):
    pass


class StastisticsPlotModel(PlotModel):
    pass


class UnstructuredCoordinatesPlotModel(PlotModel):
    pass


class Plot3DModel(PlotModel):
    pass


class LinePlotModel(BasicPlotModel):
    x: List[float]
    y: List[float]
    fmt: Optional[str]
    data: Optional[dict | DataFrame]
    scalex: bool = True
    scaley: bool = True
    kwargs: Optional[KwargsLine2DModel]


class ScatterPlotModel(BasicPlotModel):
    x: List[float]
    y: List[float]
    s: Optional[float | List[float]]
    c: Optional[str | List[str]]
    marker: MarkerStyle = "o"
    cmap: str | Colormap = "viridis"
    norm: Optional[str | Normalize]
    vmin: Optional[float]
    vax: Optional[float]
    alpha: float = None
    linewidths: float | List[float] = 1.5
    edgecolors: Literal["face", "none", None] | str | List[str] = "face"
    plotnonfinite: bool = False
    data: Optional[dict | DataFrame]
    kwargs: Optional[KwargsCollectionModel]
