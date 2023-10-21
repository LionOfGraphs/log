import sqlite3

import model

class DatabaseClient(object):
    """Database client is the one responsible for the nitty-gritty details of the database SQL."""
    
    _con : sqlite3.Connection

    def __init__(self, address : str) -> None:
        self._con = sqlite3.connect(address, check_same_thread=False)
    
    def GetLoginUser(self, email : str) -> model.DbUser:
        cur = self._con.cursor()
        res = cur.execute("SELECT hashed_password FROM user WHERE email=?", email)
        double_hashed_passwords = res.fetchall()

        if double_hashed_passwords.__len__ != 1 or double_hashed_passwords[0].__len__ != 1:
            # TODO: named exceptions
            raise Exception("expected the login to be there")

        double_hashed_password = double_hashed_passwords[0][0]
        return model.DbUser(
            double_hashed_password=double_hashed_password
        )
