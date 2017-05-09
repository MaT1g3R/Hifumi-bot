"""
A sqlite3 database handler
"""
import sqlite3


class DataController:
    __slots__ = ['connection', 'cursor']

    def __init__(self, path):
        """
        Initialize a instance of DataController
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

    def write_tag_list(self, site, tags):
        """
        Writes a list of tags into the db
        :param site: the site name
        :param tags: the list of tags
        """
        for tag in tags:
            self.write_tag(site, tag)

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

    def get_language(self, server_id: str):
        """
        Get the server language from databse
        :param server_id: the server id
        :return: the server language if found else none
        """
        sql = '''SELECT lan FROM language WHERE server=?'''
        res = self.cursor.execute(sql, [server_id]).fetchone()
        return res[0] if res is not None else None

    def set_language(self, server_id: str, language: str):
        """
        Set the language for a server
        :param server_id: the server id
        :param language: the language
        """
        sql = '''REPLACE INTO language VALUES(?, ?)'''
        self.cursor.execute(sql, (server_id, language))
        self.connection.commit()

    def add_role(self, server_id: str, role: str):
        """
        Add a role to the db
        :param server_id: the server id
        :param role: the role name
        """
        if role not in self.get_role_list(server_id):
            sql = '''
            REPLACE INTO roles VALUES (?, ?)
            '''
            self.cursor.execute(sql, [server_id, role])
            self.connection.commit()

    def remove_role(self, server_id: str, role: str):
        """
        Remove a role from the db
        :param server_id: the server id 
        :param role: the role name
        """
        sql = '''
        DELETE FROM roles WHERE server=? AND role=?
        '''
        self.cursor.execute(sql, [server_id, role])
        self.connection.commit()

    def get_role_list(self, server_id: str):
        """
        Get the list of roles under the server with id == server_id
        :param server_id: the server 
        :return: a list of roles under the server with id == server_id
        """
        sql = '''
        SELECT role FROM roles WHERE server=?
        '''
        self.cursor.execute(sql, [server_id])
        return [i[0] for i in self.cursor.fetchall()]
