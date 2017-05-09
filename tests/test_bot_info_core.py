from os.path import join
from time import time
from unittest import TestCase, main

from core.bot_info_core import time_elapsed, generate_shard_info, \
    get_all_shard_info, build_info_embed
from core.helpers import strip_letters, dict_has_empty
from tests.mock_objects import MockBot, MockContext


class TestBotInfoCore(TestCase):
    """
    Unittest for bot_info_core.py
    """

    def setUp(self):
        """
        Setup before each test case
        """
        self.bot = MockBot
        self.ctx = MockContext()

    def test_time_elapsed(self):
        """
        Test case for time_elapsed
        """
        res_str = [
            int(i) for i in strip_letters(time_elapsed(self.bot, self.ctx))
        ]
        time_diff = int(time() - self.bot.start_time)
        result = \
            res_str[0] * 60 * 60 + \
            res_str[1] * 60 + res_str[2] + res_str[3] * 60 * 60 * 24
        self.assertAlmostEqual(
            result, time_diff, delta=10
        )
        print('Expected:{}\nActual:{}'.format(time_diff, result))

    def test_generate_shard_info(self):
        """
        Test case for generate_shard_info
        """
        result = generate_shard_info(self.bot)
        expected = {
            'server_count': 50,
            'user_count': 500,
            'text_channel_count': 100,
            'voice_count': 10,
            'logged_in': True
        }
        ram = result.pop('ram')
        self.assertTrue(isinstance(ram, float))
        self.assertDictEqual(result, expected)

    def test_get_all_shard_info(self):
        """
        Test case for get_all_shard_info
        """
        path = join('test_data', 'test_shard_info')
        res = get_all_shard_info(path)
        expected = {
            "ram": 2 * 64.12,
            "server_count": 100,
            "user_count": 1000,
            "text_channel_count": 200,
            "voice_count": 20
        }
        self.assertDictEqual(res, expected)

    def test_build_info_embed(self):
        res = build_info_embed(
            self.ctx, self.bot, join('test_data', 'test_shard_info')
        ).to_dict()
        self.assertFalse(dict_has_empty(res))


if __name__ == '__main__':
    main()
