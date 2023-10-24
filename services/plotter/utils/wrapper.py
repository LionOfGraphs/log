from io import BytesIO
from typing import List

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from models.payload import PayloadModel
from models.image import FigureModel, LayoutModel, GraphModel, PlotModel


matplotlib.use("agg")


def build_image(payload: PayloadModel):
    fig: Figure = build_figure(figureModel=payload.image.figure)
    axes: dict = build_layout(layoutModel=payload.image.layout, fig=fig)
    
    buffer = BytesIO()
    if payload.image.save:
        fig.savefig(buffer, format=payload.image.format)

    return buffer.getvalue()


def build_figure(figureModel: FigureModel) -> Figure:
    fig: Figure = plt.figure(**figureModel.dict())

    return fig


def build_layout(layoutModel: LayoutModel, fig: Figure) -> dict:
    id0: int = 0
    axes0: Axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    return {id0: axes0}


def build_graphs():
    pass

def build_plots():
    pass

