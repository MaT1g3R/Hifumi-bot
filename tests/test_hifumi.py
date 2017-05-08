from time import time
from unittest import TestCase, main

from config.settings import DEFAULT_PREFIX
from core.discord_functions import get_prefix
from shell.hifumi import Hifumi


class TestHifumi(TestCase):
    """
    Unittests for :class: Hifumi
    """

    def setUp(self):
        self.default_lan = 'en'
        self.bot = Hifumi(
            get_prefix, working_dir='..', default_language=self.default_lan
        )

    def test_init(self):
        self.assertEqual(DEFAULT_PREFIX, self.bot.default_prefix)
        self.assertEqual(0, self.bot.shard_id)
        self.assertEqual(1, self.bot.shard_count)
        self.assertAlmostEqual(time(), self.bot.start_time, delta=1)


if __name__ == '__main__':
    main()
