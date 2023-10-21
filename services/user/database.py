import sqlite3

import model

class DatabaseClient(object):
    """Database client is the one responsible for the nitty-gritty details of the database SQL."""
    
    _con : sqlite3.Connection

    def __init__(self, address : str) -> None:
        self._con = sqlite3.connect(address, check_same_thread=False)
    
    def GetLoginUser(self, email : str) -> model.DbUser:
        cur = self._con.cursor()
        res = cur.execute("SELECT user_id, username, full_name, email, user_disabled, double_hashed_password FROM user WHERE email=?", (email,))
        user_rows = res.fetchall()

        if len(user_rows) != 1 or len(user_rows[0]) < 6:
            # TODO: named exceptions without leaking info
            raise Exception(f"unexpected rows for the email: {email}, rows: {user_rows}")

        return model.DbUser(
            user_id=user_rows[0][0],
            username=user_rows[0][1],
            full_name=user_rows[0][2],
            email=user_rows[0][3],
            user_disabled=user_rows[0][4],
            double_hashed_password= user_rows[0][5],
        )
