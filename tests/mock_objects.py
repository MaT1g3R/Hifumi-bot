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
    return [MockPrivateChannel() for _ in range(100)] + \
           [MockTextChannel() for _ in range(100)]


def mock_get_all_members(*args, **kwargs):
    """
    Mock get_all_members() method for MockBot
    """
    return [i for i in range(500)]


def mock_get_member(id_):
    return MockMemberAllRoles() if id_ == 'y' else MockMemberNoRoles()


def mock_send_message(channel, msg, *args, **kwargs):
    """
    Mock function for bot.send_message
    """
    print('Channel: ' + channel + '\nMessage: ' + msg)
    for k, v in kwargs.items():
        print('Keyword: {} Value: {}'.format(k, v))


class MockUser(MagicMock):
    name = 'Foo'
    avatar_url = 'https://cdn.awwni.me/xi62.png'


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
    default_prefix='?',
    # class methods
    get_language_dict=mock_get_language_dict,
    get_all_members=mock_get_all_members,
    get_all_channels=mock_get_all_channels,
    send_message=mock_send_message
)

MockChannel = MagicMock()


class MockTextChannel(MagicMock):
    type = ChannelType.text
    name = 'foo'


class MockPrivateChannel(MagicMock):
    name = 'foo'
    type = ChannelType.private


class MockNsfwChannel(MagicMock):
    def __init__(self):
        super().__init__()
        self.name = 'nSfwasdasdasdsad'
        self.type = ChannelType.text


class MockServerPermissions(MagicMock):
    def __init__(self, has_role):
        super().__init__()
        self.manage_roles = has_role
        self.administrator = has_role
        self.manage_messages = has_role


class MockServer(MagicMock):
    def __init__(self, id_='foo'):
        super().__init__()
        self.id = id_
        self.get_member = mock_get_member


class MockMemberAllRoles(MagicMock):
    id = 'y'
    server_permissions = MockServerPermissions(True)


class MockMemberNoRoles(MagicMock):
    id = 'n'
    server_permissions = MockServerPermissions(False)


class MockMessage(MagicMock):
    def __init__(
            self, server=MockServer(), channel=MockChannel(), content='',
            author=None
    ):
        super().__init__()
        self.server = server
        self.channel = channel
        self.content = content
        self.author = author


class MockContext(MagicMock):
    def __init__(self, message=MockMessage()):
        super().__init__()
        self.message = message


class MockExpection(Exception):
    pass
