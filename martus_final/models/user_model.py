import sqlite3
from typing import Optional


class UserModel:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def authenticate(self, username: str, password: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM USERS WHERE username=? AND password=?",
            (username, password),
        ).fetchone()

    def get_all(self) -> list:
        return self.conn.execute(
            "SELECT userID, username, role FROM USERS ORDER BY username"
        ).fetchall()

    def add(self, username: str, password: str, role: str) -> None:
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO USERS (username,password,role) VALUES (?,?,?)",
                    (username, password, role),
                )
        except sqlite3.IntegrityError:
            raise ValueError(f"Username '{username}' already exists.")

    def delete(self, uid: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM USERS WHERE userID=?", (uid,))
