import grpc
import user_pb2
import user_pb2_grpc

import model
import service


class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    """UserServiceServicer is the request/response handler for the user service"""

    _service_handler: service.UserService

    def __init__(self, service_handler: service.UserService) -> None:
        self._service_handler = service_handler

    def Login(self, request: user_pb2.LoginRequest, context) -> user_pb2.LoginResponse:
        # TODO: return early if request is invalid
        try:
            res: model.LoginResponse = self._service_handler.Login(
                model.LoginRequest(
                    email=request.email,
                    hashed_password=request.hashed_password,
                )
            )
            return user_pb2.LoginResponse(
                identity_token=res.identity_token,
                access_token=res.access_token,
                refresh_token=res.refresh_token,
            )
        except Exception as e:
            # TODO: log exception with a decent logger, associated with a request
            print(e)
            # TODO: filter exceptions for different gRPC codes
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("S#$?*t happens")
            return user_pb2.LoginResponse()

    def RefreshToken(
        self, request: user_pb2.RefreshRequest, context
    ) -> user_pb2.RefreshResponse:
        # TODO: return early if request is invalid
        try:
            res: model.RefreshResponse = self._service_handler.RefreshToken(
                model.RefreshRequest(
                    refresh_token=request.refresh_token,
                )
            )
            return user_pb2.RefreshResponse(
                access_token=res.access_token,
                new_refresh_token=res.new_refresh_token,
            )
        except Exception as e:
            # TODO: log exception with a decent logger, associated with a request
            print(e)
            # TODO: filter exceptions for different gRPC codes
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("S#$?*t happens")
            return user_pb2.RefreshResponse()

    def SignUp(
        self, request: user_pb2.SignUpRequest, context
    ) -> user_pb2.SignUpResponse:
        # TODO: return early if request is invalid
        try:
            self._service_handler.SignUp(
                model.SignupRequest(
                    user_name=request.user_name,
                    full_name=request.full_name,
                    email=request.email,
                    hashed_password=request.hashed_password,
                )
            )
            return user_pb2.SignUpResponse()
        except Exception as e:
            # TODO: log exception with a decent logger, associated with a request
            print(e)
            # TODO: filter exceptions for different gRPC codes
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("S#$?*t happens")
            return user_pb2.SignUpResponse()
