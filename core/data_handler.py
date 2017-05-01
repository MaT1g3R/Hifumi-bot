"""
A sqlite3 database handler
"""
import sqlite3


class DataHandler:
    def __init__(self, path):
        """
        Initialize a instance of DataHandler
        :param path: the path to the database
        """
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def get_prefix(self, server_id: str):
        """
        Get the server prefix from databse
        :param server_id: the server id
        :return: the server prefix if found else none
        """
        sql = '''SELECT prefix FROM prefix WHERE server=?'''
        res = self.cursor.execute(sql, [server_id]).fetchone()
        return res[0] if res is not None else None

    def set_prefix(self, server_id: str, prefix: str):
        """
        Set the prefix for a server
        :param server_id: the server id
        :param prefix: the command prefix
        """
        sql = '''REPLACE INTO prefix VALUES(?, ?)'''
        self.cursor.execute(sql, (server_id, prefix))
        self.connection.commit()
