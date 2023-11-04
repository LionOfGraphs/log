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
        query = """
SELECT user_id, user_name, full_name, email, user_disabled, double_hashed_password
FROM user"""
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

    def UpsertUser(self, user: model.DbUser) -> None:
        cur = self._con.cursor()
        query = """
INSERT INTO user(user_id, user_name, full_name, email, user_disabled, double_hashed_password) 
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT(user_id) DO UPDATE SET
user_name=?, full_name=?, email=?, user_disabled=?, double_hashed_password=?"""
        cur.execute(
            query,
            (
                user.user_id,
                user.user_name,
                user.full_name,
                user.email,
                user.user_disabled,
                user.double_hashed_password,
                user.user_name,
                user.full_name,
                user.email,
                user.user_disabled,
                user.double_hashed_password,
            ),
        )
        self._con.commit()

    def DeleteUser(self, user_id: str) -> None:
        cur = self._con.cursor()
        query = """
DELETE FROM user
WHERE user_id=?"""
        cur.execute(
            query,
            (user_id,),
        )
        self._con.commit()

    def GetSession(self, filters: dict[str, str]) -> model.DbSession:
        cur = self._con.cursor()
        query = """
SELECT session_id, user_id, lastest_refresh_token_exp, device_context
FROM session"""
        params = []
        if len(filters) > 0:
            query += " WHERE"
        for filter_key, filter_value in filters.items():
            query += f" {filter_key}=? AND"
            params.append(filter_value)
        query = query[:-3]  # remove last AND
        res = cur.execute(query, tuple(params))
        session_rows = res.fetchall()

        if len(session_rows) != 1 or len(session_rows[0]) < 4:
            # TODO: named exceptions without leaking info
            raise Exception(
                f"unexpected rows GetSession, filters: {filters}, rows: {session_rows}"
            )

        return model.DbSession(
            session_id=session_rows[0][0],
            user_id=session_rows[0][1],
            lastest_refresh_token_exp=session_rows[0][2],
            device_context=session_rows[0][3],
        )

    def UpsertSession(self, session: model.DbSession) -> None:
        cur = self._con.cursor()
        # NOTE: assumption for the DB, the session ID and user ID cannot be updated
        query = """
INSERT INTO session(session_id, user_id, lastest_refresh_token_exp, device_context)
VALUES (?, ?, ?, ?)
ON CONFLICT(session_id) DO UPDATE SET
lastest_refresh_token_exp=?, device_context=?"""
        cur.execute(
            query,
            (
                session.session_id,
                session.user_id,
                session.lastest_refresh_token_exp,
                session.device_context,
                session.lastest_refresh_token_exp,
                session.device_context,
            ),
        )
        self._con.commit()

    def DeleteSession(self, session_id: str) -> None:
        cur = self._con.cursor()
        query = """
DELETE FROM session
WHERE session_id=?"""
        cur.execute(
            query,
            (session_id,),
        )
        self._con.commit()
