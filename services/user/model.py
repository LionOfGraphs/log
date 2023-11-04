from pydantic import BaseModel


# UserInfo will contain the whole information of the user
class UserInfo(BaseModel):
    user_id: str
    user_name: str | None = None
    full_name: str | None = None
    email: str | None = None
    user_disabled: bool | None = None


# DbUser model contains the row information on the user table
class DbUser(UserInfo):
    double_hashed_password: str


# DbSession model contains the row information on the session table
class DbSession(BaseModel):
    session_id: str
    user_id: str
    lastest_refresh_token_exp: str
    device_context: str | None = None


# AccessTokenReq TODO: docstring
class Access(BaseModel):
    access_token: str


# LoginRequest model will just contain basic information necessary on login
class LoginRequest(BaseModel):
    email: str
    hashed_password: str


# LoginResponse model will just contain basic information returned on login
class LoginResponse(BaseModel):
    identity_token: str
    access_token: str
    refresh_token: str


# RefreshRequest TODO: docstring
class RefreshRequest(BaseModel):
    refresh_token: str


# RefreshResponse TODO: docstring
class RefreshResponse(BaseModel):
    access_token: str
    new_refresh_token: str


# SignupRequest TODO: docstring
class SignupRequest(BaseModel):
    user_name: str
    full_name: str
    email: str
    hashed_password: str


# UpdateUserReq TODO: docstring
class UpdateUserReq(UserInfo):
    access_token: str
