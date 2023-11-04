import grpc
import time
from decouple import config

import user_pb2
import user_pb2_grpc


# TODO: make these actual tests
def test_user_flow():
    with grpc.insecure_channel(config("USER_SERVICE_ADDRESS")) as channel:
        stub = user_pb2_grpc.UserServiceStub(channel=channel)

        response = stub.GetJwk(user_pb2.GetJwkRequest())
        print("GetJwk success")

        response = stub.SignUp(
            user_pb2.SignUpRequest(
                user_info=user_pb2.UserInfo(
                    user_name="foo",
                    full_name="foo bar",
                    email="foo@bar.com",
                ),
                hashed_password="hashpwd",
            )
        )
        print("SignUp success")
        response = stub.Login(
            user_pb2.LoginRequest(email="foo@bar.com", hashed_password="hashpwd")
        )
        print("Login success")
        tk1 = response.refresh_token
        response = stub.RefreshToken(user_pb2.RefreshRequest(refresh_token=tk1))
        tk2 = response.new_refresh_token

        print("RefreshToken success")
        try:
            response = stub.RefreshToken(user_pb2.RefreshRequest(refresh_token=tk1))
        except:
            print("RefreshToken: token re-usage failed")

        try:
            response = stub.RefreshToken(user_pb2.RefreshRequest(refresh_token=tk2))
        except:
            print("RefreshToken: token usage when forced log out happned failed")

        response = stub.Login(
            user_pb2.LoginRequest(email="foo@bar.com", hashed_password="hashpwd")
        )
        print("Login success")

        response = stub.Logout(
            user_pb2.LogoutRequest(),
            metadata=(("access_token", response.access_token),),
        )
        print("Logout success")

        try:
            response = stub.RefreshToken(
                user_pb2.RefreshRequest(refresh_token=response.refresh_token)
            )
        except:
            print("RefreshToken: token usage when log out invoked")

        response = stub.Login(
            user_pb2.LoginRequest(email="foo@bar.com", hashed_password="hashpwd")
        )
        print("Login success")
        tk3 = response.access_token

        response = stub.GetUserInfo(
            user_pb2.GetUserInfoRequest(),
            metadata=(("access_token", tk3),),
        )
        print("GetUserInfo success")
        print(response)

        response = stub.UpdateUserInfo(
            user_pb2.UpdateUserInfoRequest(
                user_info=user_pb2.UserInfo(
                    full_name="bar foo",
                )
            ),
            metadata=(("access_token", tk3),),
        )
        print("UpdateUserInfo success")

        response = stub.GetUserInfo(
            user_pb2.GetUserInfoRequest(),
            metadata=(("access_token", tk3),),
        )
        print("GetUserInfo success")
        print(response)

        response = stub.Unregister(
            user_pb2.UnregisterRequest(),
            metadata=(("access_token", tk3),),
        )
        print("Unregister success")


if __name__ == "__main__":
    test_user_flow()
