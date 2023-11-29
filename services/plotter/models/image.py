from pydantic import BaseModel
from typing import List

from models.figure import FigureModel
from models.layout import LayoutModel


class ImageModel(BaseModel):
    save: bool = True
    format: str = "png"
    figure: FigureModel = FigureModel()
    layout: LayoutModel = LayoutModel()

    class Config:
        arbitrary_types_allowed = True
