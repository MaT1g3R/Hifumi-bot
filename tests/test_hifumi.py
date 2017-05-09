from os.path import join
from time import time
from unittest import TestCase
from unittest import main

from config.settings import DEFAULT_PREFIX
from core.discord_functions import get_prefix
from core.language_support import read_language
from shell.hifumi import Hifumi


class TestHifumi(TestCase):
    """
    Unittests for :class: Hifumi
    """

    def setUp(self):
        """
        setUp before each test case
        """
        self.default_lan = 'en'
        self.working_dir = '..'
        self.bot = Hifumi(
            get_prefix,
            working_dir=self.working_dir, default_language=self.default_lan
        )

    def test_init(self):
        """
        Test the Hifumi constructor
        """
        self.assertEqual(DEFAULT_PREFIX, self.bot.default_prefix)
        self.assertEqual(0, self.bot.shard_id)
        self.assertEqual(1, self.bot.shard_count)
        self.assertAlmostEqual(time(), self.bot.start_time, delta=1)
        self.assertDictEqual(
            self.bot.language, read_language(join('..', 'data', 'language'))
        )
        self.assertEqual(self.bot.default_language, self.default_lan)
        self.assertIsNotNone(self.bot.logger)
        self.assertEqual(self.working_dir, self.bot.working_dir)


if __name__ == '__main__':
    main()
