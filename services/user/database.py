import sqlite3

import model


class DatabaseClient(object):
    """Database client is the one responsible for the nitty-gritty details of the database SQL."""

    _con: sqlite3.Connection

    def __init__(self, address: str) -> None:
        self._con = sqlite3.connect(address, check_same_thread=False)

    # TODO: docstring with available filters
    def GetUser(self, filters: dict[str, str]) -> model.DbUser:
        cur = self._con.cursor()
        query = "SELECT user_id, user_name, full_name, email, user_disabled, double_hashed_password FROM user"
        params = []
        if len(filters) > 0:
            query += " WHERE"
        for filter_key, filter_value in filters.items():
            query += f" {filter_key}=? AND"
            params.append(filter_value)
        query = query[:-3]  # remove last AND

        res = cur.execute(query, tuple(params))
        user_rows = res.fetchall()

        if len(user_rows) != 1 or len(user_rows[0]) < 6:
            # TODO: named exceptions without leaking info
            raise Exception(
                f"unexpected rows GetUser, filters: {filters}, rows: {user_rows}"
            )

        return model.DbUser(
            user_id=user_rows[0][0],
            user_name=user_rows[0][1],
            full_name=user_rows[0][2],
            email=user_rows[0][3],
            user_disabled=user_rows[0][4],
            double_hashed_password=user_rows[0][5],
        )

    def RegisterUser(self, user: model.DbUser) -> None:
        cur = self._con.cursor()
        query = "INSERT INTO user(user_id, user_name, full_name, email, user_disabled, double_hashed_password) VALUES (?, ?, ?, ?, ?, ?)"
        cur.execute(
            query,
            (
                user.user_id,
                user.user_name,
                user.full_name,
                user.email,
                user.user_disabled,
                user.double_hashed_password,
            ),
        )
