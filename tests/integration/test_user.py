import io
import grpc
from decouple import config

import user_pb2
import user_pb2_grpc


# TODO: make these actual tests
def test_user_flow():
    with grpc.insecure_channel(config("USER_SERVICE_ADDRESS")) as channel:
        stub = user_pb2_grpc.UserServiceStub(channel=channel)

        response = stub.SignUp(
            user_pb2.SignUpRequest(
                user_name="foo",
                full_name="foo bar",
                email="foo@bar.com",
                hashed_password="hashpwd",
            )
        )
        print(response)
        response = stub.Login(
            user_pb2.LoginRequest(email="foo@bar.com", hashed_password="hashpwd")
        )
        print(response)
        response = stub.RefreshToken(
            user_pb2.RefreshRequest(refresh_token=response.refresh_token)
        )
        print(response)


if __name__ == "__main__":
    test_user_flow()
