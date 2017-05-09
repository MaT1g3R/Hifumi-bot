"""
A collection of mock objects
"""
from os.path import join
from unittest.mock import MagicMock

from discord import ChannelType

from core.file_io import read_json


def mock_get_language_dict(*args, **kwargs):
    """
    Mock get_language_dict() method for MockBot, always returns the english dict
    """
    path = join('..', 'data', 'language', 'en.json')
    return read_json(open(path))


def mock_get_all_channels(*args, **kwargs):
    """
    Mock get_all_channels() method for MockBot
    """
    return [MockChannel() for _ in range(100)] + \
           [MockTextChannel() for _ in range(100)]


def mock_get_all_members(*args, **kwargs):
    """
    Mock get_all_members() method for MockBot
    """
    return [i for i in range(500)]


# MockUser object
class MockUser(MagicMock):
    name = 'Foo'
    avatar_url = 'https://cdn.awwni.me/xi62.png'


# MockBot object
MockBot = MagicMock()
MockBot.configure_mock(
    # Instance variables
    start_time=1494000000,
    servers=[i for i in range(50)],
    voice_clients=[i for i in range(10)],
    is_logged_in=True,
    user=MockUser(),
    shard_id=0,
    shard_count=3,
    # class methods
    get_language_dict=mock_get_language_dict,
    get_all_members=mock_get_all_members,
    get_all_channels=mock_get_all_channels
)

# MockChannel object
MockChannel = MagicMock()


# MockTextChannel object
class MockTextChannel(MagicMock):
    type = ChannelType.text


# MockMessage object
class MockMessage(MagicMock):
    server = None


# MockContext object
class MockContext(MagicMock):
    message = MockMessage()
