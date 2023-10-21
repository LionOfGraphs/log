from jose import jwt
from datetime import datetime, timedelta
import hashlib

import model
import database

class UserService(object):
    """UserService is the service logic responsible for the user management"""
    
    _database_client : database.DatabaseClient
    _jwk : str
    _issuer : str
    _algorithm : str
    _audience : str

    def __init__(
            self, db : database.DatabaseClient,
            jwk : str,
            issuer : str = "logusersvc",
            algorithm : str = "HS256",
            audience : str = "logsvcs",
        ) -> None:
        self._database_client = db
        self._jwk = jwk
        self._issuer = issuer
        self._algorithm  = algorithm
        self._audience = audience
    
    def Login(self, req : model.LoginRequest) -> model.LoginResponse:
        user_entry = self._database_client.GetLoginUser(req.email)

        double_hashed_password = hashlib.sha256(req.hashed_password.encode('utf-8'))
        if double_hashed_password.hexdigest() != user_entry.double_hashed_password:
            # TODO: don't expose info and make it custom exception
            raise Exception(f"password hash missmatch {double_hashed_password.hexdigest()} != {user_entry.double_hashed_password}")
    
        if user_entry.user_disabled:
            # TODO: don't expose info and make it custom exception
            raise Exception(f"user {user_entry.username} is disabled")

        now = datetime.utcnow()

        access_expiration_delta = timedelta(seconds=3600)
        access_expiration = now + access_expiration_delta
        access_token_payload = {
            'sub': user_entry.user_id,
            'iss': self._issuer,
            'nbf': now,
            'iat': now,
            'exp': access_expiration,
            'aud': self._audience,
        }
        access_token = jwt.encode(access_token_payload, self._jwk, algorithm=self._algorithm)

        id_expiration = access_expiration
        id_token_payload = {
            'sub': user_entry.user_id,
            'iss': self._issuer,
            'nbf': now,
            'iat': now,
            'exp': id_expiration,
            'aud': self._audience,
            'username': user_entry.username,
            'full_name': user_entry.full_name,
            'email': user_entry.email,
        }
        id_token = jwt.encode(id_token_payload, self._jwk, algorithm=self._algorithm)

        # TODO: logic to ensure only once usage of refresh token
        refresh_expiration_delta = timedelta(days=1)
        refresh_expiration = now + refresh_expiration_delta
        refresh_token_payload = {
            'sub': user_entry.user_id,
            'iss': self._issuer,
            'nbf': now,
            'iat': now,
            'exp': refresh_expiration,
            'aud': self._audience,
        }
        refresh_token = jwt.encode(refresh_token_payload, self._jwk, algorithm=self._algorithm)

        return model.LoginResponse(
            identity_token=id_token,
            access_token=access_token,
            refresh_token=refresh_token,
        )
