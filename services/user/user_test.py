import unittest
import grpc
import sqlite3
import os
from jose import jwt
from decouple import config
import time

import main as user_server
import user_pb2_grpc as user_client
import user_pb2


class TestUserService(unittest.TestCase):
    grpc_channel: grpc.Channel = None
    client: user_client.UserServiceStub = None
    db_connection: sqlite3.Connection = None

    @classmethod
    def setUpClass(cls):
        cls.db_connection = sqlite3.connect(
            config("DATABASE_ADDRESS"), check_same_thread=False
        )
        # NOTE: this starts the server in the background threads
        user_server.grpc_server.start()
        cls.grpc_channel = grpc.insecure_channel(config("SERVER_ADDRESS"))
        cls.client = user_client.UserServiceStub(channel=cls.grpc_channel)

    @classmethod
    def tearDownClass(cls):
        # NOTE: close down in the inverse order of openning up
        cls.grpc_channel.close()
        user_server.grpc_server.stop(grace=1.0)
        user_server.grpc_server.wait_for_termination()
        user_server.service_database_client.close()
        cls.db_connection.close()
        # TODO: remove this once we don't use sqlite3 for the test
        os.remove(config("DATABASE_ADDRESS"))

    def setUp(self):
        # NOTE: setup a clean database for each test case
        cur = self.db_connection.cursor()
        with open("dbinit-up.sql", "r") as f:
            q = f.read()
        cur.executescript(q)
        self.db_connection.commit()
        cur.close()

    def tearDown(self):
        # NOTE: clean "dirty" test database
        cur = self.db_connection.cursor()
        with open("dbinit-down.sql", "r") as f:
            q = f.read()
        cur.executescript(q)
        self.db_connection.commit()
        cur.close()

    # NOTE: tests begin here

    def test_getjwk(self):
        response: user_pb2.GetJwkResponse = self.client.GetJwk(user_pb2.GetJwkRequest())
        self.assertEqual(response, user_pb2.GetJwkResponse(jwk=config("JWK")))

    def test_signup_login_logout(self):
        signup_res: user_pb2.SignUpResponse = self.client.SignUp(
            user_pb2.SignUpRequest(
                user_info=user_pb2.UserInfo(
                    user_name="foo",
                    full_name="foo bar",
                    email="foo@bar.com",
                ),
                hashed_password="hashpwd",
            )
        )
        self.assertEqual(signup_res, user_pb2.SignUpResponse())

        login_res: user_pb2.LoginResponse = self.client.Login(
            user_pb2.LoginRequest(email="foo@bar.com", hashed_password="hashpwd")
        )
        _ = jwt.decode(
            login_res.access_token,
            config("JWK"),
            issuer="user-svc-log",
            audience="log-svcs",
            options={"require_exp": True},
        )

        logout_res: user_pb2.LogoutResponse = self.client.Logout(
            user_pb2.LogoutRequest(),
            metadata=(("access_token", login_res.access_token),),
        )
        self.assertEqual(logout_res, user_pb2.LogoutResponse())

    def test_signup_login_unregister_signup(self):
        signup_response: user_pb2.SignUpResponse = self.client.SignUp(
            user_pb2.SignUpRequest(
                user_info=user_pb2.UserInfo(
                    user_name="foo",
                    full_name="foo bar",
                    email="foo@bar.com",
                ),
                hashed_password="hashpwd",
            )
        )
        self.assertEqual(signup_response, user_pb2.SignUpResponse())

        login_res: user_pb2.LoginResponse = self.client.Login(
            user_pb2.LoginRequest(email="foo@bar.com", hashed_password="hashpwd")
        )

        unregister_response: user_pb2.UnregisterResponse = self.client.Unregister(
            user_pb2.UnregisterRequest(),
            metadata=(("access_token", login_res.access_token),),
        )
        self.assertEqual(unregister_response, user_pb2.UnregisterResponse())

        signup_response: user_pb2.SignUpResponse = self.client.SignUp(
            user_pb2.SignUpRequest(
                user_info=user_pb2.UserInfo(
                    user_name="foo",
                    full_name="foo bar",
                    email="foo@bar.com",
                ),
                hashed_password="hashpwd",
            )
        )
        self.assertEqual(signup_response, user_pb2.SignUpResponse())

    def test_refresh_flows(self):
        signup_response: user_pb2.SignUpResponse = self.client.SignUp(
            user_pb2.SignUpRequest(
                user_info=user_pb2.UserInfo(
                    user_name="foo",
                    full_name="foo bar",
                    email="foo@bar.com",
                ),
                hashed_password="hashpwd",
            )
        )
        self.assertEqual(signup_response, user_pb2.SignUpResponse())

        login_res: user_pb2.LoginResponse = self.client.Login(
            user_pb2.LoginRequest(email="foo@bar.com", hashed_password="hashpwd")
        )

        refresh_token_1 = login_res.refresh_token
        refresh_response: user_pb2.RefreshResponse = self.client.RefreshToken(
            user_pb2.RefreshRequest(refresh_token=refresh_token_1)
        )
        refresh_token_2 = refresh_response.new_refresh_token

        # NOTE: old token raises an error and forces logout
        self.assertRaises(
            Exception,
            lambda: self.client.RefreshToken(
                user_pb2.RefreshRequest(refresh_token=refresh_token_1)
            ),
        )
        # NOTE: new token after forced logout raises an error
        self.assertRaises(
            Exception,
            lambda: self.client.RefreshToken(
                user_pb2.RefreshRequest(refresh_token=refresh_token_2)
            ),
        )

        login_res_2: user_pb2.LoginResponse = self.client.Login(
            user_pb2.LoginRequest(email="foo@bar.com", hashed_password="hashpwd")
        )

        logout_response: user_pb2.LogoutResponse = self.client.Logout(
            user_pb2.LogoutRequest(),
            metadata=(("access_token", login_res_2.access_token),),
        )
        self.assertEqual(logout_response, user_pb2.LogoutResponse())

        # NOTE: refresh after voluntary logout raises exception
        self.assertRaises(
            Exception,
            lambda: self.client.RefreshToken(
                user_pb2.RefreshRequest(refresh_token=login_res_2.refresh_token)
            ),
        )

    def test_user_info_flows(self):
        signup_response: user_pb2.SignUpResponse = self.client.SignUp(
            user_pb2.SignUpRequest(
                user_info=user_pb2.UserInfo(
                    user_name="foo",
                    full_name="foo bar",
                    email="foo@bar.com",
                ),
                hashed_password="hashpwd",
            )
        )
        self.assertEqual(signup_response, user_pb2.SignUpResponse())

        login_res: user_pb2.LoginResponse = self.client.Login(
            user_pb2.LoginRequest(email="foo@bar.com", hashed_password="hashpwd")
        )

        user_info_res: user_pb2.GetUserInfoResponse = self.client.GetUserInfo(
            user_pb2.GetUserInfoRequest(),
            metadata=(("access_token", login_res.access_token),),
        )
        self.assertEqual(
            user_info_res,
            user_pb2.GetUserInfoResponse(
                user_info=user_pb2.UserInfo(
                    user_name="foo",
                    full_name="foo bar",
                    email="foo@bar.com",
                )
            ),
        )

        update_user_info_res: user_pb2.UpdateUserInfoResponse = (
            self.client.UpdateUserInfo(
                user_pb2.UpdateUserInfoRequest(
                    user_info=user_pb2.UserInfo(
                        full_name="bar foo",
                    )
                ),
                metadata=(("access_token", login_res.access_token),),
            )
        )
        self.assertEqual(update_user_info_res, user_pb2.UpdateUserInfoResponse())

        user_info_res_2 = self.client.GetUserInfo(
            user_pb2.GetUserInfoRequest(),
            metadata=(("access_token", login_res.access_token),),
        )
        self.assertEqual(
            user_info_res_2,
            user_pb2.GetUserInfoResponse(
                user_info=user_pb2.UserInfo(
                    user_name="foo",
                    full_name="bar foo",
                    email="foo@bar.com",
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
