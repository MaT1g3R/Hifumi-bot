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

    def write_tag(self, site, tag):
        """
        Write a tag entry into the database
        :param site: the site name
        :param tag: the tag entry
        """
        if self.tag_in_db(site, tag):
            return
        else:
            sql = '''INSERT INTO nsfw_tags(site, tag) VALUES (?, ?)'''
            self.cursor.execute(sql, (site, tag))
            self.connection.commit()

    def tag_in_db(self, site, tag):
        """
        Returns if the tag is in the db or not
        :param site: the site name
        :param tag: the tag name
        :return: True if the tag is in the db else false
        """
        sql = '''
    SELECT EXISTS(SELECT 1 FROM nsfw_tags WHERE site=? AND tag=?LIMIT 1)'''
        self.cursor.execute(sql, (site, tag))
        return self.cursor.fetchone() == (1,)

    def fuzzy_match_tag(self, site, tag):
        """
        Try to fuzzy match a tag with one in the db
        :param site: the stie name
        :param tag: the tag name
        :return: a tag in the db if match success else None
        """
        sql = """
        SELECT tag FROM nsfw_tags 
        WHERE (tag LIKE '{0}%' OR tag LIKE '%{0}%' OR tag LIKE '%{0}') 
        AND site=?
        """.format(tag)
        res = self.cursor.execute(sql, [site]).fetchone()
        return res[0] if res is not None else None
