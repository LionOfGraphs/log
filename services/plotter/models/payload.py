from pydantic import BaseModel
from typing import List

from models.image import ImageModel
from models.data import FileModel, FunctionModel


class PayloadModel(BaseModel):
    data: List[FileModel | FunctionModel] | None = None
    image: ImageModel = ImageModel()
