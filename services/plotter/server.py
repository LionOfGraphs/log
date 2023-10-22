import grpc
import proto.plotter_pb2
from proto.plotter_pb2_grpc import PlotterServiceServicer

from service import plot


class Plotter(PlotterServiceServicer):
    def GeneratePlot(self,):
