from sqlite3 import connect


class TransferError(ValueError):
    pass


class DataManager:
    """
    A class that layer between the bot and the sqlite db. The bot should
    read/write to this class and the class will write to the db.
    """

    def __init__(self, path: str):
        """
        Initialize an instance of this class.
        :param path: the path that points to the db
        """
        self.connection = connect(path)
        self.cursor = self.connection.cursor()
        self.user_info = {}
        self.guild_info = {}
        self.member_info = {}
        self.nsfw_tags = {}

    def get_prefix(self, guild_id: int) -> str:
        pass

