from difflib import get_close_matches
from sqlite3 import Connection, Cursor
from typing import List, Optional, Union

from data_controller.data_controller import _get_tags, _write_tags


class TagMatcher:
    """
    A class that holds all the tags and attempt to fuzzy match user inputs
    with exsiting tags in the db.
    """

    def __init__(self, connection: Connection, cursor: Cursor):
        """
        Initialize an instance of this class.
        :param connection: the sqlite3 connection.
        :param cursor: the sqlite3 cursor.
        """
        self.__connection, self.__cursor = connection, cursor
        self.__tags = _get_tags(cursor)

    def add_tags(self, site: str, tags: Union[str, List[str]]):
        """
        Add tag(s) to the db.
        :param site: the site of the tag.
        :param tags: a single tag or a list of tags.
        """
        written = False
        if site not in self.__tags:
            self.__tags[site] = []
        if isinstance(tags, str) and tags not in self.__tags[site]:
            self.__tags[site].append(tags)
            written = True
        elif isinstance(tags, list):
            for tag in tags:
                if tag not in self.__tags[site]:
                    self.__tags[site].append(tag)
                    written = True
        if written:
            _write_tags(
                self.__connection, self.__cursor, site, self.__tags[site])

    def match_tag(self, site: str, tag: str) -> Optional[str]:
        """
        Try to match user input tag with one from the db.
        :param site: the site of the tag.
        :param tag: the user input tag.
        :return: a tag from the db if match was success, else None
        """
        if site not in self.__tags:
            return
        res = get_close_matches(tag, self.__tags[site], 1)
        return res[0] if res else None

    def tag_exist(self, site: str, tag: str) -> bool:
        """
        Check weather if tag exist in the db,
        :param site: the site name.
        :param tag: the tag.
        :return: True if it is in the db.
        """
        return site in self.__tags and tag in self.__tags[site]
