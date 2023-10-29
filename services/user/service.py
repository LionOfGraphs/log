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
    # TODO: make this a data base table with cleanup
    # user logout should also kill all its tokens on the cache
    # current format: { "token_family": "expiry_date" }
    _expired_token_family: dict

    def __init__(
        self,
        db: database.DatabaseClient,
        jwk: str,
        issuer: str = "logusersvc",
        algorithm: str = "HS256",
        audience: str = "logsvcs",
    ) -> None:
        self._database_client = db
        self._jwk = jwk
        self._issuer = issuer
        self._algorithm = algorithm
        self._audience = audience
        self._expired_token_family = {}

    def FetchKeys(self) -> str:
        return self._jwks

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
        # NOTE: we create a refresh token "family" in every login to ensure we
        # only keep track of the latest refresh token usage within the family,
        # if there is a re-usage (i.e., the expiry date is closer than the one
        # cached for the family) we "kill" the family
        refresh_token_family = str(uuid.uuid4())
        refresh_token_payload = {
            "sub": user_entry.user_id,
            "iss": self._issuer,
            "nbf": now,
            "iat": now,
            "exp": refresh_expiration,
            "aud": self._audience,
            "fam": refresh_token_family,
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
            # TODO: check if the user is logged in to begin with.

            claims = jwt.decode(
                req.refresh_token,
                self._jwk,
                algorithms=self._algorithm,
                issuer=self._issuer,
                audience=self._audience,
                options={"require_exp": True},
            )

            if claims["fam"] in self._expired_token_family:
                if int(self._expired_token_family[claims["fam"]]) >= int(claims["exp"]):
                    # TODO: logout the user and force re-login
                    raise Exception("refresh token re-usage")

            # TODO: DANGER - current in-memory-database of repeated refresh tokens is not cleaned-up.
            # This grows indefinetly!
            self._expired_token_family[claims["fam"]] = claims["exp"]

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
                "fam": claims["fam"],
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
            # TODO: named exception to give a nice HTTP code that the front-end can indicate
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
        self._database_client.RegisterUser(
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
