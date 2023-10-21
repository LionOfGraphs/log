from pydantic import BaseModel

# UserInfo will contain the whole information of the user
class UserInfo(BaseModel):
    user_id: str
    username: str | None = None
    full_name: str | None = None
    email: str | None = None
    user_disabled: bool | None = None

# DbUser model contains the row information on the user table
class DbUser(UserInfo):
    double_hashed_password: str

# LoginRequest model will just contain basic information necessary on login
class LoginRequest(BaseModel):
    email: str
    hashed_password: str

# LoginResponse model will just contain basic information returned on login
class LoginResponse(BaseModel):
    identity_token: str
    access_token: str
    refresh_token: str
