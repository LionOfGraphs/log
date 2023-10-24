from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID, uuid4

from matplotlib.layout_engine import LayoutEngine

from models.kwargs import KwargsFigureModel


"""
References:
Figure      https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure
RcParams    https://matplotlib.org/stable/tutorials/introductory/customizing.html#matplotlibrc-sample
Config      https://docs.pydantic.dev/usage/model_config/
"""


class SubplotParamsModel(BaseModel):
    left: float = 0.125
    right: float = 0.9
    bottom: float = 0.11
    top: float = 0.88
    wspace: float = 0.2
    hspace: float = 0.2


class FigureModel(BaseModel):
    num: UUID = uuid4()
    figsize: tuple[float] = (6.4, 4.8)
    dpi: float = 100.0
    facecolor: str = "white"
    edgecolor: str = "white"
    linewidth: float = 0.0
    frameon: bool = True
    subplotpars: SubplotParamsModel = SubplotParamsModel()
    # layout: Optional[Literal["constrained", "compressed", "tight"] | LayoutEngine | None]
    # kwargs: Optional[KwargsFigureModel]

    class Config:
        arbitrary_types_allowed = True
