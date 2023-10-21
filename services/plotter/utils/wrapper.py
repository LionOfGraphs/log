from io import BytesIO
from matplotlib.pyplot import figure
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from typing import List
from matplotlib.axes import Axes
from pandas import DataFrame
from numpy import arange

from models.payload import PayloadModel
from models.image import FigureModel, LayoutModel, GraphModel


def build_image(payload: PayloadModel):
    fig: Figure = build_figure(figureModel=payload.image.figure)
    axes: dict = build_layout(layoutModel=payload.image.layout, fig=fig)

    buffer = BytesIO()
    if payload.image.save:
        fig.savefig(buffer, format=payload.image.format)

    return buffer.getvalue()


def build_figure(figureModel: FigureModel) -> Figure:
    fig: Figure = figure(**figureModel.dict())

    return fig


def build_layout(layoutModel: LayoutModel, fig: Figure) -> dict:
    id0: int = 0
    axes0: Axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    return {
        id0: axes0
    }


def build_graphs(graphModel: GraphModel):
    pass