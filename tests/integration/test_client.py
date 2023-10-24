import sys
sys.path.append("..\..\services\plotter")

import io
import grpc
import PIL.Image as Image
from decouple import config
from proto.plotter_pb2 import PlotRequest
from proto.plotter_pb2_grpc import PlotterServiceStub


def client():
    with grpc.insecure_channel(config("PLOTTER_ADDRESS")) as channel:
        stub = PlotterServiceStub(channel=channel)

        with open("..\\data\\test_01.csv", "rb") as f:
            rawData = f.read()

        encodedPayload = b'{ "data":[{"datatype":"file", "filename":"test_01.csv"}]}'
        response = stub.GeneratePlot(
            PlotRequest(encodedPayload=encodedPayload, rawData=rawData)
        )
        return response
    

if __name__ == "__main__":
    r = client()
    print(type(r.image))
    image = Image.open(io.BytesIO(r.image))
    image.save('tmp\\test.png')
