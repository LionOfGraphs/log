import grpc
import grpc_interceptor

from datetime import datetime
from jose import jwt
from grpc_interceptor.exceptions import GrpcException
from typing import Any, Callable, List


class AuthServerInterceptor(grpc_interceptor.ServerInterceptor):
    """TODO: write documentation on how to use this"""

    """
     The _jwks is a cache map of issuer -> jwk
     for supported issuers in the jwk_fetch function should support
     the invocation for that issuer, e.g., for our own user service:
    
     def jwk_fetch(iss: str) -> str:
        if iss not "user-svc-log":
           raise Exception("unsupported issuer")
        with grpc.insecure_channel(config("USER_SERVICE_ADDRESS")) as channel:
           stub = user_pb2_grpc.UserServiceStub(channel=channel)
           response = stub.GetJwk(user_pb2.GetJwkRequest())
           return response.jwk
    """
    _jwks: dict[str, str]
    """
    The list of endpoints for this interceptor to ignore.
    """
    _unprotected_endpoints: List[str]
    """
    The map of endpoints and roles that have access.
    """
    _permissions: dict[str, List[str]]
    """
    The audience for which this interceptor will validate.
    """
    _audience: str

    def __init__(
        self,
        jwk_fetch: Callable[[str], str],
        unprotected_endpoints: List[str],
        audience: str,
        permissions: dict[str, List[str]],
    ):
        self._jwks = {}
        self._jwk_fetch = jwk_fetch
        self._unprotected_endpoints = unprotected_endpoints
        self._audience = audience
        self._permissions = permissions

    def intercept(
        self,
        method: Callable[[Any, grpc.ServicerContext], Any],
        request: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        try:
            if method_name in self._unprotected_endpoints:
                return method(request, context)

            # NOTE: if it is protected: expect a token and validate it.
            metadata = context.invocation_metadata()
            access_token = [
                metadatum.value
                for metadatum in metadata
                if metadatum.key == "access_token"
            ]
            if len(access_token) < 1:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "no access token given")
            access_token = access_token[0]

            claims = jwt.get_unverified_claims(access_token)

            if "iss" not in claims:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "no iss")

            if int(datetime.utcnow().timestamp()) < int(claims["nbf"]):
                context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    "utilized before the not-before nbf",
                )

            # NOTE: if the jwk is not in the cache, load it with the given jwks loader
            if claims["iss"] not in self._jwks:
                self._jwks[claims["iss"]] = self._jwk_fetch(claims["iss"])

            if method_name in self._permissions:
                if claims["role"] not in self._permissions[method_name]:
                    context.abort(
                        grpc.StatusCode.UNAUTHENTICATED,
                        "unauthorized role",
                    )

            _ = jwt.decode(
                access_token,
                self._jwks[claims["iss"]],
                issuer=claims["iss"],
                audience=self._audience,
                options={"require_exp": True},
            )

            return method(request, context)
        except GrpcException as e:
            context.set_code(e.status_code)
            context.set_details(e.details)
            raise e
        except Exception as e:
            # NOTE: this is highly unexpected, means the service itself does not handle
            # its own exceptions before sending a gRPC response
            # TODO: do another thing instead of printing
            print(f"on method {method_name} got unexpected exception: {e}")
            raise e
