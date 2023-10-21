import model
import database

class UserService(object):
    """UserService is the service logic responsible for the user management"""
    
    _database_client : database.DatabaseClient

    def __init__(self, db : database.DatabaseClient) -> None:
        self._database_client = db
    
    def Login(self, req : model.LoginRequest) -> model.LoginResponse:
        # TODO: pick up the username/password, hash it, compare it, and generate tokens
        double_hashed_password = self._database_client.GetLoginUser(req.email)


        return model.LoginResponse(
            identity_token="foo",
            access_token="bar",
            refresh_token="foo-bar"
        )
