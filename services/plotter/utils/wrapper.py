from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from models.payload import PayloadModel
from models.image import FigureModel, LayoutModel, GraphModel, PlotModel

from pandas import DataFrame


matplotlib.use("agg")


def build_image(payload: PayloadModel):
    fig: Figure = build_figure(figureModel=payload.image.figure)
    axes: dict = build_layout(layoutModel=payload.image.layout, fig=fig)

    for graph_id, ax in axes.items():
        graphModel = payload.image.graphs.get(graph_id)
        build_graphs(ax, graphModel)
        for plot_id in graphModel.plot_id_list:
            build_plots(ax, payload.image.plots.get(plot_id), payload.data[0].dataframe)

    buffer = BytesIO()
    if payload.image.save:
        fig.savefig(buffer, format=payload.image.format)

    return buffer.getvalue()


def build_figure(figureModel: FigureModel) -> Figure:
    fig: Figure = plt.figure(**figureModel.model_dump())

    return fig


def build_layout(layoutModel: LayoutModel, fig: Figure) -> dict:
    id0: int = 0
    axes0: Axes = fig.subplots(1, 1)

    return {id0: axes0}


def build_graphs(axes: Axes, graphModel: GraphModel):
    pass


def build_plots(axes: Axes, plotModel: PlotModel, data: DataFrame):
    if plotModel.plotType == "LinePlotModel":
        for col in data.columns:
            axes.plot(data.index, data[col])
