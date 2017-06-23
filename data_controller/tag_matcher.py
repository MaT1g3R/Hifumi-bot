from difflib import get_close_matches
from typing import List, Optional, Union

from data_controller.postgres import Postgres


class TagMatcher:
    """
    A class that holds all the tags and attempt to fuzzy match user inputs
    with exsiting tags in the db.
    """

    def __init__(self, postgres: Postgres, tags: dict):
        """
        Initialize an instance of this class.
        :param postgres: the postgres controller.
        :param tags: the list of tags in the db on startup.
        """
        self.__postgres = postgres
        self.__tags = tags

    async def add_tags(self, site: str, tags: Union[str, List[str]]):
        """
        Add tag(s) to the db.
        :param site: the site of the tag.
        :param tags: a single tag or a list of tags.
        """
        written = False
        if site not in self.__tags:
            self.__tags[site] = []
        if isinstance(tags, str) and tags not in self.__tags[site] and tags:
            self.__tags[site].append(tags)
            written = True
        elif isinstance(tags, list):
            for tag in tags:
                if tag not in self.__tags[site] and tag:
                    self.__tags[site].append(tag)
                    written = True
        if written:
            await self.__postgres.set_tags(site, self.__tags[site])

    def match_tag(self, site: str, tag: str) -> Optional[str]:
        """
        Try to match user input tag with one from the db.
        :param site: the site of the tag.
        :param tag: the user input tag.
        :return: a tag from the db if match was success, else None
        """
        if site not in self.__tags:
            return
        if self.tag_exist(site, tag):
            return tag
        res = get_close_matches(tag, self.__tags[site], 1, cutoff=0.5)
        return res[0] if res else None

    def tag_exist(self, site: str, tag: str) -> bool:
        """
        Check weather if tag exist in the db,
        :param site: the site name.
        :param tag: the tag.
        :return: True if it is in the db.
        """
        return site in self.__tags and tag in self.__tags[site]
