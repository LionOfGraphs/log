from concurrent import futures
from decouple import config

import grpc
import user_pb2_grpc

import server
import service
import database

def serve():
    address = config("SERVER_ADDRESS")
    database_address = config("DATABASE_ADDRESS")

    service_database_client = database.DatabaseClient(
        address = database_address,
    )
    service_handler = service.UserService(
        db = service_database_client,
    )
    service_servicer = server.UserServiceServicer(
        service_handler = service_handler,
    )

    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(
       service_servicer, grpc_server
    )
    grpc_server.add_insecure_port(address)
    grpc_server.start()
    grpc_server.wait_for_termination()


if __name__ == "__main__":
    serve()