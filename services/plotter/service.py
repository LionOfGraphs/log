from fastapi import FastAPI, UploadFile

from models.payload import PayloadModel
from utils.validator import validate_data
from utils.wrapper import build_image


def service(rawData: UploadFile, payload: PayloadModel) -> bytes:
    """Triggers the plotter engine for the given request"""

    validate_data(dataList=payload.data, rawData=rawData)

    image_buffer = build_image(payload=payload)

    return image_buffer
