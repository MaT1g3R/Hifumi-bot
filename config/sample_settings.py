"""
A sample settings file, please fill this out and rename it to "settings.py"
"""

# DON'T EDIT THOSE LINES
# -----------------------------------------------
from os.path import join
from sqlite3 import DatabaseError

from core.data_controller import DataController

# -----------------------------------------------

# The bot token
TOKEN = 'INSERT_YOUR_TOKEN'

# A colour in hex, it will be used for embeds
COLOUR = 0xff0000

# The name of the bot
NAME = 'BOT_NAME'

# A list of developers
DEVS = ['FOO']

# A list of bot helpers
HELPERS = ['BAR']

# The bot default prefix
DEFAULT_PREFIX = '~'

# The support server
SUPPORT = 'YOUR_SUPPORT_SERVER'

# The bot twitter
TWITTER = 'YOU_BOT_TWITTER'

# The bot website
WEBSITE = 'YOU_BOT_WEBSITE'

# The bot invite link
INVITE = 'YOU_BOT_INVITE_LINK'

# A list of bot owner's discord ids, as strings. MUST have at least 1 element
OWNER = ['']

# Your Danbooru user name
DANBOORU_USERNAME = 'INSERT_YOUR_DANBOORU_USERNAME'

# Your Danbooru API key
DANBOORU_API = 'INSERT_YOUR_DANBOORU_API'

# A list of bad words to comply with discord TOS, DON'T edit this
BAD_WORD = ['loli', 'l0l1', 'lol1', 'l0li', '7071', 'lolii', 'looli', 'lolli',
            'shota', 'sh07a', 'sh0ta', 'chota', 'ch0ta', 'shot4', 'sh0t4',
            '5hota', '5h0ta', '5h0t4', '7oli', '70li', '707i', 'l071', 'hifumi',
            'takimoto', 'child', 'children', 'cp', 'preteen', 'teen', 'gore',
            'g0r3', 'g0re', 'ch1ld', 'kid', 'k1d', 'kiddo', 'ロリ', 'ロリコン',
            'pico', 'ショタコン', 'ショタ']

# Setting for sharding, defualts to not sharded
SHARDED = False
SHARD_ID = 0
SHARD_COUNT = 1

# The data controller for the sqlite3 database
# Only edit the path variable if you move the database, although is strongly
# recommended to keep it in place
path = join('data', 'hifumi_db')
try:
    DATA_CONTROLLER = DataController(path)
except DatabaseError:
    DATA_CONTROLLER = DataController(join('..', path))
# Toggle this to true if you want to enable console logging
ENABLE_CONSOLE_LOGGING = False
