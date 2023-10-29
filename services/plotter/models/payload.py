from pydantic import BaseModel
from typing import Optional, List

from models.image import ImageModel
from models.data import FileModel, FunctionModel


class PayloadModel(BaseModel):
    data: Optional[List[FileModel | FunctionModel]] = None
    image: ImageModel = ImageModel()
