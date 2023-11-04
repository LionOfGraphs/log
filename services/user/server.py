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

    def _access_token_from_context(self, context: grpc.ServicerContext) -> str:
        metadata = context.invocation_metadata()
        access_token = [
            metadatum.value for metadatum in metadata if metadatum.key == "access_token"
        ][0]
        return access_token

    def GetJwk(
        self, _: user_pb2.GetJwkRequest, context: grpc.ServicerContext
    ) -> user_pb2.GetJwkResponse:
        return user_pb2.GetJwkResponse(jwk=self._service_handler.GetJwk())

    def Login(
        self, request: user_pb2.LoginRequest, context: grpc.ServicerContext
    ) -> user_pb2.LoginResponse:
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
        self, request: user_pb2.RefreshRequest, context: grpc.ServicerContext
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
        self, request: user_pb2.SignUpRequest, context: grpc.ServicerContext
    ) -> user_pb2.SignUpResponse:
        # TODO: return early if request is invalid
        try:
            self._service_handler.SignUp(
                model.SignupRequest(
                    user_name=request.user_info.user_name,
                    full_name=request.user_info.full_name,
                    email=request.user_info.email,
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

    def Logout(
        self, _: user_pb2.LogoutRequest, context: grpc.ServicerContext
    ) -> user_pb2.LogoutResponse:
        # TODO: return early if request is invalid
        try:
            access_token = self._access_token_from_context(context=context)
            self._service_handler.Logout(
                model.Access(
                    access_token=access_token,
                )
            )
            return user_pb2.LogoutResponse()
        except Exception as e:
            # TODO: log exception with a decent logger, associated with a request
            print(e)
            # TODO: filter exceptions for different gRPC codes
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("S#$?*t happens")
            return user_pb2.LogoutResponse()

    def Unregister(
        self, _: user_pb2.UnregisterRequest, context: grpc.ServicerContext
    ) -> user_pb2.UnregisterResponse:
        # TODO: return early if request is invalid
        try:
            access_token = self._access_token_from_context(context=context)
            self._service_handler.Unregister(
                model.Access(
                    access_token=access_token,
                )
            )
            return user_pb2.UnregisterResponse()
        except Exception as e:
            # TODO: log exception with a decent logger, associated with a request
            print(e)
            # TODO: filter exceptions for different gRPC codes
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("S#$?*t happens")
            return user_pb2.UnregisterResponse()

    def GetUserInfo(
        self, _: user_pb2.GetUserInfoRequest, context: grpc.ServicerContext
    ) -> user_pb2.GetUserInfoResponse:
        # TODO: return early if request is invalid
        try:
            access_token = self._access_token_from_context(context=context)
            user_info = self._service_handler.GetUserInfo(
                model.Access(
                    access_token=access_token,
                )
            )
            return user_pb2.GetUserInfoResponse(
                user_info=user_pb2.UserInfo(
                    user_name=user_info.user_name,
                    full_name=user_info.full_name,
                    email=user_info.email,
                )
            )
        except Exception as e:
            # TODO: log exception with a decent logger, associated with a request
            print(e)
            # TODO: filter exceptions for different gRPC codes
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("S#$?*t happens")
            return user_pb2.UnregisterResponse()

    def ListUserInfo(
        self, request: user_pb2.ListUserInfoRequest, context: grpc.ServicerContext
    ) -> user_pb2.ListUserInfoResponse:
        # TODO: return early if request is invalid
        return super().ListUserInfo(request, context)

    def UpdateUserInfo(
        self, request: user_pb2.UpdateUserInfoRequest, context: grpc.ServicerContext
    ) -> user_pb2.UpdateUserInfoResponse:
        # TODO: return early if request is invalid
        try:
            access_token = self._access_token_from_context(context=context)
            self._service_handler.UpdateUserInfo(
                model.UpdateUserReq(
                    user_id="fake-user-id",  # NOTE: this will be replaced by access token value
                    user_name=request.user_info.user_name,
                    full_name=request.user_info.full_name,
                    email=request.user_info.email,
                    access_token=access_token,
                )
            )
            return user_pb2.UpdateUserInfoResponse()
        except Exception as e:
            # TODO: log exception with a decent logger, associated with a request
            print(e)
            # TODO: filter exceptions for different gRPC codes
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("S#$?*t happens")
            return user_pb2.UpdateUserInfoResponse()
