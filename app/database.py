"""
DATABASE QUERY FOR READ AND WRITE
"""

import secrets
import sqlite3
from datetime import datetime
from sqlite3 import Connection


class DataBase:
    """
    used to connect, write to and read from a local sqlite3 database
    """

    def __init__(self, file, table):
        """
        try to connect to file and create cursor
        """
        self.file = file
        self.table = table

        with sqlite3.connect(self.file) as conn:
            self._create_table(conn)

    def _create_table(self, conn: Connection):
        """
        create new database table if one doesn't exist
        :return: None
        """
        query = f"""CREATE TABLE IF NOT EXISTS {self.table} (id TEXT PRIMARY KEY,
                    publicKey TEXT, last_activity DATE)"""
        conn.cursor().execute(query)
        conn.commit()

    def get_public_key(self, identity):
        """
        Gets a publicKey of user by identity
        :param identity: str
        :return: publicKey
        """
        query = f"SELECT publicKey FROM {self.table} WHERE ID = ?"

        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (identity,))
            result = cursor.fetchall()

        public_key = result[0][0] if result else None
        return public_key

    def update_last_activity(self, identity):
        """
        updates the last_activity of a user
        :param identity: str
        :return: None
        """
        query = f"UPDATE {self.table} SET last_activity = ? WHERE ID = ?"

        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (datetime.now(), identity))
            conn.commit()

    def is_exist(self, identity):
        """
        check if the user exists
        :param identity: str
        :return: bool
        """
        query = f"SELECT * FROM {self.table} WHERE ID = ?"

        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (identity,))
            result = cursor.fetchall()

        return bool(result)

    def save_user(self, public_key):
        """
        saves the given public_key in the table
        :param public_key: str
        :return: identity
        """
        identity = secrets.token_hex(5)

        query = f"INSERT INTO {self.table} VALUES (?, ?, ?)"

        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (identity, public_key, datetime.now()))
            conn.commit()

        return identity
