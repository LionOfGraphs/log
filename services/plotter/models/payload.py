from pydantic import BaseModel
from typing import List, Optional

from models.image import ImageModel
from models.data import FileModel, FunctionModel


class PayloadModel(BaseModel):
    data: Optional[List[FileModel | FunctionModel]]
    image: ImageModel = ImageModel()
