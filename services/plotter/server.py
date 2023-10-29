import json
from decouple import config
from concurrent import futures
from models.payload import PayloadModel

import grpc
from proto.plotter_pb2 import PlotRequest, PlotResponse
import proto.plotter_pb2_grpc as plotter_grpc


from service import plot


class PlotterServiceServicer(plotter_grpc.PlotterServiceServicer):
    def GeneratePlot(self, request: PlotRequest, context):
        decodedPayload = request.encodedPayload.decode("utf8")
        payload = PayloadModel(**json.loads(decodedPayload))

        image = plot(rawData=request.rawData, payload=payload)

        return PlotResponse(image=image)


def run():
    address = config("SERVER_ADDRESS")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    plotter_grpc.add_PlotterServiceServicer_to_server(PlotterServiceServicer(), server)
    server.add_insecure_port(address)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    run()
