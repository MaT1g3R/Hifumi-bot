import sqlite3
from pathlib import Path
from unittest import TestCase, main

from discord.ext.commands import CommandOnCooldown, MissingRequiredArgument

from config.settings import COLOUR
from scripts.discord_functions import command_error_handler, get_prefix, \
    build_embed, clense_prefix
from scripts.helpers import dict_has_empty
from tests.mock_objects import MockBot, MockContext, MockExpection, MockMessage, \
    MockServer


class TestDiscordFunctons(TestCase):
    """
    Unittests for discord_functions.py
    """

    def setUp(self):
        """
        Setup before each test case
        """
        self.bot = MockBot
        self.ctx = MockContext()
        self.msg = MockMessage(
            content='? <@!12312> foo bar baz'
        )
        self.msg_bad_server = MockMessage(
            server=MockServer(id_='aaaaaaaaaaaaaa')
        )
        self.msg_none_server = MockMessage(
            server=None
        )
        self.body = [
            ('foo', 'bar'),
            ('baz', 'qux', False),
            ('I\'m out of names', 'some value', True)
        ]
        self.footer = 'footer'

    def test_command_error_handler_common(self):
        """
        Test case for command_error_handler, with a common error
        """
        ex = CommandOnCooldown(1, 1)
        try:
            command_error_handler(self.bot.get_language_dict(self.ctx), ex)
        except Exception as e:
            self.fail(str(e))

    def test_command_error_handler_member_not_found(self):
        """
        Test case for command_error_handler, where the error raised
        is member not found
        """
        ex = Exception('Member "asdasd" not found')
        try:
            command_error_handler(self.bot.get_language_dict(self.ctx), ex)
        except Exception as e:
            self.fail(str(e))

    def test_command_error_handler_missing_member_arg(self):
        """
        Test case for command_error_handler, where the error raised
        is missing member argument
        """
        ex = MissingRequiredArgument('member asdasdsad')
        try:
            command_error_handler(self.bot.get_language_dict(self.ctx), ex)
        except Exception as e:
            self.fail(str(e))

    def test_command_error_handler_unexpected(self):
        """
        Test case for command_error_handler where the error raised is
        unexpected
        """
        ex = MockExpection()
        self.assertRaises(
            MockExpection, command_error_handler,
            self.bot.get_language_dict(self.ctx), ex
        )

    def test_get_prefix(self):
        """
        Test get_prefix_ when the server is in the db
        """
        db = sqlite3.connect(str(Path('test_data/mock_db')))
        cursor = db.cursor()
        sql_del = '''
                DELETE FROM main.prefix WHERE server = ?
                '''
        sql_insert = '''
        INSERT INTO main.prefix VALUES (?, ?)
        '''
        server = self.msg.server.id
        prefix = 'bar'
        cursor.execute(sql_del, [server])
        db.commit()
        cursor.execute(sql_insert, (server, prefix))
        db.commit()
        self.assertEqual(
            prefix, get_prefix(cursor, self.msg.server, self.bot.default_prefix)
        )
        cursor.execute(sql_del, [server])
        db.commit()
        db.close()

    def test_get_prefix_not_found(self):
        """
        Test for get_prefix_ when the server is not found in the db
        """
        db = sqlite3.connect(str(Path('test_data/mock_db')))
        cursor = db.cursor()
        self.assertEqual(
            self.bot.default_prefix,
            get_prefix(
                cursor, self.msg_bad_server.server, self.bot.default_prefix
            )
        )
        db.close()

    def test_get_prefix_none(self):
        """
        Test for get_prefix_ when server is None
        """
        self.assertEqual(
            self.bot.default_prefix,
            get_prefix('', self.msg_none_server.server, self.bot.default_prefix)

        )

    def embed_correct(self, res, with_footer=True):
        """
        Helper method to assert some general things about embeds
        :param res: the result
        :param with_footer: assert footer equal if it's True
        """
        self.assertFalse(dict_has_empty(res))
        self.assertTrue(body_correct(self.body, res['fields']))
        self.assertEqual(COLOUR, res['color'])
        if with_footer:
            self.assertEqual(self.footer, res['footer']['text'])

    def test_build_embed_no_author(self):
        """
        Test build_embed when there's no author
        """
        res = build_embed(self.body, COLOUR, footer=self.footer).to_dict()
        self.embed_correct(res)
        self.assertTrue('author' not in res)

    def test_build_embed_no_author_url(self):
        """
        Test build_embed when there's an author but no icon_url
        """
        author = {
            'name': 'some name',
        }
        res = build_embed(self.body, COLOUR, footer=self.footer,
                          author=author).to_dict()
        self.embed_correct(res)
        self.assertDictEqual(author, res['author'])

    def test_build_embed_no_footer(self):
        """
        Test build_embed when there's no footer
        """
        author = {
            'name': 'some name',
            'icon_url': 'www.google.com'
        }
        res = build_embed(self.body, COLOUR, author=author).to_dict()
        self.embed_correct(res, False)
        self.assertTrue('footer' not in res)
        self.assertDictEqual(author, res['author'])

    def test_build_embed(self):
        """
        Test build_embed in general
        """
        author = {
            'name': 'some name',
            'icon_url': 'www.google.com'
        }
        res = build_embed(self.body, COLOUR, footer=self.footer,
                          author=author).to_dict()
        self.embed_correct(res)
        self.assertDictEqual(author, res['author'])

    def test_build_embed_bad_kwarg(self):
        """
        Test build_embed when there's a bad kwarg
        """
        author = {
            'name': 'some name',
            'icon_url': 'www.google.com'
        }
        res = build_embed(self.body, COLOUR, footer=self.footer,
                          author=author, foo='bar').to_dict()
        self.embed_correct(res)
        self.assertDictEqual(author, res['author'])
        self.assertTrue('foo' not in res)

    def test_clense_prefix(self):
        """
        Test case for clense_prefix funtion
        """
        res = clense_prefix(self.msg, '?')
        self.assertEqual('<@!12312> foo bar baz', res)

    def test_clense_prefix_fail(self):
        """
        Test case for clense_prefux funtion when the messages doesn't start
        with the prefix
        """
        res = clense_prefix(self.msg, '1')
        self.assertEqual(res, self.msg.content)


def body_correct(body, result):
    """
    Helper function to make sure the embed content is correct based on the
    input body
    :param body: the input body
    :param result: the embed result
    :return: True if the body is correct
    """
    res_lst = []
    _body = []
    for field in result:
        res_lst.append((field['name'], field['value'], field['inline']))
    for t in body:
        name, value = t[:2]
        inline = True
        if len(t) == 3:
            inline = t[2]
        _body.append((name, value, inline))
    return set(res_lst) == set(_body)


if __name__ == '__main__':
    main()
