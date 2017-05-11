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
        sql = '''REPLACE INTO nsfw_tags(site, tag) VALUES (?, ?)'''
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
        SELECT EXISTS(SELECT 1 FROM nsfw_tags WHERE site=? AND tag=?LIMIT 1)
        '''
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

    def set_mod_log(self, server_id: str, channel_id: str):
        """
        Set the mod log channel id for a given server
        :param server_id: the server id
        :param channel_id: the channel id
        """
        sql = '''
        REPLACE INTO mod_log VALUES (?, ?)
        '''
        self.cursor.execute(sql, [server_id, channel_id])
        self.connection.commit()

    def get_mod_log(self, server_id: str):
        """
        Get a list of all mod logs from a given server
        :param server_id: the server id
        :return: a list of all mod log channel ids
        """
        sql = '''
        SELECT channel FROM mod_log WHERE server=?
        '''
        self.cursor.execute(sql, [server_id])
        return [i[0] for i in self.cursor.fetchall()]

    def remove_mod_log(self, server_id: str, channel_id: str):
        """
        Delete a modlog from the db
        :param server_id: the server id
        :param channel_id: the channel id
        """
        sql = '''
        DELETE FROM mod_log WHERE server=? AND channel=?
        '''
        self.cursor.execute(sql, [server_id, channel_id])
        self.connection.commit()

    def __create_warn_entry(self, server_id, user_id):
        """
        Helper method to create a warn entry if it doesnt exist
        :param server_id: the server id
        :param user_id: the user id
        """
        sql_insert = '''
        INSERT OR IGNORE INTO warns VALUES(?,?,0)
        '''
        self.cursor.execute(sql_insert, [server_id, user_id])

    def add_warn(self, server_id: str, user_id: str):
        """
        Add 1 to the warning count of the user
        :param server_id: the server id
        :param user_id: the user id
        """
        self.__create_warn_entry(server_id, user_id)
        sql = '''
        UPDATE warns SET number = number + 1 WHERE server = ? AND user = ?
        '''
        self.cursor.execute(sql, [server_id, user_id])
        self.connection.commit()

    def remove_warn(self, server_id: str, user_id: str):
        """
        Subtract 1 from the warning count of the user
        :param server_id: the server id
        :param user_id: the user id
        """
        sql = '''
        UPDATE warns SET number = number - 1 
        WHERE server = ? AND user = ? AND number > 0
        '''
        self.cursor.execute(sql, [server_id, user_id])
        self.connection.commit()

    def get_warn(self, server_id: str, user_id: str):
        """
        Get the warning count of a user
        :param server_id: the server id
        :param user_id: the user id
        :return: the warning count of the user
        """
        sql = '''
        SELECT number FROM warns WHERE server = ? AND user = ?
        '''
        self.cursor.execute(sql, [server_id, user_id])
        result = self.cursor.fetchone()
        return result[0]


if __name__ == '__main__':
    d = DataController('../tests/test_data/mock_db')
