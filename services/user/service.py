from typing import List
from jose import jwt
from datetime import datetime, timedelta
import hashlib
import uuid

import model
import database


class UserService(object):
    """UserService is the service logic responsible for the user management"""

    _database_client: database.DatabaseClient
    _jwk: str
    _issuer: str
    _algorithm: str
    _audience: str

    def __init__(
        self,
        db: database.DatabaseClient,
        jwk: str,
        issuer: str = "user-svc-log",
        algorithm: str = "HS256",
        audience: str = "log-svcs",
    ) -> None:
        self._database_client = db
        self._jwk = jwk
        self._issuer = issuer
        self._algorithm = algorithm
        self._audience = audience
        self._expired_token_family = {}

    def GetJwk(self) -> str:
        return self._jwk

    def Login(self, req: model.LoginRequest) -> model.LoginResponse:
        user_entry = self._database_client.GetUser({"email": req.email})

        double_hashed_password = hashlib.sha256(req.hashed_password.encode("utf-8"))
        if double_hashed_password.hexdigest() != user_entry.double_hashed_password:
            # TODO: don't expose info and make it custom exception
            raise Exception(
                f"password hash missmatch {double_hashed_password.hexdigest()} != {user_entry.double_hashed_password}"
            )

        if user_entry.user_disabled:
            # TODO: don't expose info and make it custom exception
            raise Exception(f"user {user_entry.user_name} is disabled")

        # NOTE: we create a session ID in every login to ensure we
        # only keep track of the latest refresh token usage within the session,
        # if there is a re-usage (i.e., the expiry date is closer than the one
        # cached for the session) we "kill" the session and force re-login.
        # if the user logs out, we also terminate the session and invalidate
        # the refresh token usage.
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        access_expiration_delta = timedelta(seconds=3600)
        access_expiration = now + access_expiration_delta
        access_token_payload = {
            "sub": user_entry.user_id,
            "iss": self._issuer,
            "nbf": now,
            "iat": now,
            "exp": access_expiration,
            "aud": self._audience,
            "sid": session_id,
        }
        access_token = jwt.encode(
            access_token_payload, self._jwk, algorithm=self._algorithm
        )

        id_expiration = access_expiration
        id_token_payload = {
            "sub": user_entry.user_id,
            "iss": self._issuer,
            "nbf": now,
            "iat": now,
            "exp": id_expiration,
            "aud": self._audience,
            "user_name": user_entry.user_name,
            "full_name": user_entry.full_name,
            "email": user_entry.email,
        }
        id_token = jwt.encode(id_token_payload, self._jwk, algorithm=self._algorithm)

        refresh_expiration_delta = timedelta(days=1)
        refresh_expiration = now + refresh_expiration_delta
        self._database_client.UpsertSession(
            model.DbSession(
                session_id=session_id,
                user_id=user_entry.user_id,
                # NOTE: refresh token into UNIX int timestamp
                # the record is inserted with "no refresh token used"
                lastest_refresh_token_exp="0",
                device_context="foo",
            )
        )
        refresh_token_payload = {
            "sub": user_entry.user_id,
            "iss": self._issuer,
            "nbf": now,
            "iat": now,
            "exp": refresh_expiration,
            "aud": self._audience,
            "sid": session_id,
        }
        refresh_token = jwt.encode(
            refresh_token_payload, self._jwk, algorithm=self._algorithm
        )

        return model.LoginResponse(
            identity_token=id_token,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def RefreshToken(self, req: model.RefreshRequest) -> model.RefreshResponse:
        try:
            claims = jwt.decode(
                req.refresh_token,
                self._jwk,
                algorithms=self._algorithm,
                issuer=self._issuer,
                audience=self._audience,
                options={"require_exp": True},
            )

            if "sid" not in claims:
                # TODO: don't expose info, log it, and make it custom exception
                raise Exception(f"refresh token did not have session ID claim")
            session_entry = self._database_client.GetSession(
                filters={"session_id": claims["sid"]}
            )

            # NOTE: if we attempt to re-use a refresh token, remove the session and
            # force the user to re-login
            if int(session_entry.lastest_refresh_token_exp) >= int(claims["exp"]):
                self._database_client.DeleteSession(session_id=session_entry.session_id)
                raise Exception(
                    f"refresh token re-usage, exp got {claims['exp']}, exp stored {session_entry.lastest_refresh_token_exp}"
                )

            # NOTE: if it's a first refresh token usage, refresh the DB record
            session_entry.lastest_refresh_token_exp = claims["exp"]
            self._database_client.UpsertSession(session=session_entry)

            now = datetime.utcnow()

            access_expiration_delta = timedelta(seconds=3600)
            access_expiration = now + access_expiration_delta
            access_token_payload = {
                "sub": claims["sub"],
                "iss": self._issuer,
                "nbf": now,
                "iat": now,
                "exp": access_expiration,
                "aud": self._audience,
                "sid": claims["sid"],
            }
            access_token = jwt.encode(
                access_token_payload, self._jwk, algorithm=self._algorithm
            )

            refresh_expiration_delta = timedelta(days=1)
            refresh_expiration = now + refresh_expiration_delta
            refresh_token_payload = {
                "sub": claims["sub"],
                "iss": self._issuer,
                "nbf": now,
                "iat": now,
                "exp": refresh_expiration,
                "aud": self._audience,
                "sid": claims["sid"],
            }
            new_refresh_token = jwt.encode(
                refresh_token_payload, self._jwk, algorithm=self._algorithm
            )

            return model.RefreshResponse(
                access_token=access_token,
                new_refresh_token=new_refresh_token,
            )
        except jwt.JWTClaimsError as e:
            # TODO: don't expose info, log it, and make it custom exception
            raise e
        except jwt.JWTError as e:
            # TODO: don't expose info, log it, and make it custom exception
            raise e
        except jwt.ExpiredSignatureError as e:
            # TODO: don't expose info, log it, and make it custom exception
            raise e
        # catch-all
        except Exception as e:
            # TODO: don't expose info, log it, and make it custom exception
            raise e

    def SignUp(self, req: model.SignupRequest) -> None:
        try:
            self._database_client.GetUser({"email": req.email})
            # TODO: named exception to give a nice gRPC code that the front-end can indicate
            # this following message to the user.
            raise Exception(
                f"the email {req.email} already has a user associated with it"
            )
        except:
            # expected path if the user was not yet in the database.
            pass

        new_user_id = str(uuid.uuid4())
        double_hashed_password = hashlib.sha256(
            req.hashed_password.encode("utf-8")
        ).hexdigest()
        self._database_client.UpsertUser(
            model.DbUser(
                user_id=new_user_id,
                user_name=req.user_name,
                full_name=req.full_name,
                email=req.email,
                # TODO: start users as disabled (True) and ask email check when we have an SMTP server
                user_disabled=False,
                double_hashed_password=double_hashed_password,
            )
        )

    def Logout(self, req: model.Access) -> None:
        # NOTE: this assumes the server already verified them, being the entry point of the request
        claims = jwt.get_unverified_claims(req.access_token)
        self._database_client.DeleteSession(session_id=claims["sid"])

    def Unregister(self, req: model.Access) -> None:
        # NOTE: this assumes the server already verified them, being the entry point of the request
        claims = jwt.get_unverified_claims(req.access_token)
        # TODO: make the delete user call a bit safer, not only token based
        # but some sort of confirmation, e.g., email
        self._database_client.DeleteUser(user_id=claims["sub"])

    def GetUserInfo(self, req: model.Access) -> model.UserInfo:
        # NOTE: this assumes the server already verified them, being the entry point of the request
        claims = jwt.get_unverified_claims(req.access_token)
        user_entry = self._database_client.GetUser({"user_id": claims["sub"]})
        return user_entry

    def ListUserInfo(self, _: model.Access) -> List[model.UserInfo]:
        # TODO: check against a DB admin if we have permissions to check this up
        return []

    def UpdateUserInfo(self, req: model.UpdateUserReq) -> model.UserInfo:
        # NOTE: this assumes the server already verified them, being the entry point of the request
        claims = jwt.get_unverified_claims(req.access_token)
        # NOTE: always force you can only update your user entry
        req.user_id = claims["sub"]

        # NOTE: read before write, do not do this if you're a sane person
        user_entry = self._database_client.GetUser({"user_id": claims["sub"]})
        user_entry_attrs = vars(user_entry)
        for key, value in vars(req).items():
            if key in user_entry_attrs and value != "":
                user_entry_attrs[key] = value
        self._database_client.UpsertUser(user=user_entry)
        return user_entry
