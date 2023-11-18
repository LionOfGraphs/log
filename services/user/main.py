from concurrent import futures
from decouple import config

import grpc
import user_pb2_grpc

import server
import service
import database

import auth

address = config("SERVER_ADDRESS")
database_address = config("DATABASE_ADDRESS")
jwk = config("JWK")

service_database_client = database.DatabaseClient(
    address=database_address,
)
service_handler = service.UserService(
    db=service_database_client,
    jwk=jwk,
)
service_servicer = server.UserServiceServicer(
    service_handler=service_handler,
)


# TODO: don't have this so hardcoded like this
def jwk_fetch(_: str) -> str:
    return jwk


interceptors = [
    auth.AuthServerInterceptor(
        jwk_fetch=jwk_fetch,
        unprotected_endpoints=[
            "/user.UserService/GetJwk",
            "/user.UserService/Login",
            "/user.UserService/SignUp",
            "/user.UserService/RefreshToken",
        ],
        audience="log-svcs",
    )
]

grpc_server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
)
user_pb2_grpc.add_UserServiceServicer_to_server(service_servicer, grpc_server)
grpc_server.add_insecure_port(address)


if __name__ == "__main__":
    try:
        grpc_server.start()
        grpc_server.wait_for_termination()
    # NOTE: expected exception
    except KeyboardInterrupt:
        grpc_server.stop(grace=1.0)
        service_database_client.close()
    except Exception as e:
        print("unexpected exception")
        print(e)
        exit(1)
