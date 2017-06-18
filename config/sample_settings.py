"""
A sample settings file, please fill this out and rename it to "settings.py"
"""

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

# Your Edamam Recipe Search API key,
# can be aquired here: https://developer.edamam.com/
# The first element is the application ID,
# the second element is the application Key
EDAMAM_API = ['INSERT_YOUR_EDAMAM_API_ID', 'INSERT_YOUR_EDAMAM_API_KEY']

# A list of bad words to comply with discord TOS, DON'T edit this
BAD_WORD = ['loli', 'l0l1', 'lol1', 'l0li', '7071', 'lolii', 'looli', 'lolli',
            'shota', 'sh07a', 'sh0ta', 'chota', 'ch0ta', 'shot4', 'sh0t4',
            '5hota', '5h0ta', '5h0t4', '7oli', '70li', '707i', 'l071', 'hifumi',
            'takimoto', 'child', 'children', 'cp', 'preteen', 'teen', 'gore',
            'g0r3', 'g0re', 'ch1ld', 'kid', 'k1d', 'kiddo', 'ロリ', 'ロリコン',
            'pico', 'ショタコン', 'ショタ']

# If your bot has a character illustrating her/him, write him/her name here
# If the character comes from a series/movie/any audiovisual media, you may
# type the series name here too. For example:
# pacman -> pacman and the ghostly adventures pacman | or this one:
# sonoda umi -> love live sonoda umi
WAIFU_NAME = 'BOT_CHARACTER_NAME_HERE'

# Setting for sharding, set the count to greater than 1 for sharded bot.
SHARD_COUNT = 1
assert SHARD_COUNT >= 1

# Toggle this to true if you want to enable console logging
ENABLE_CONSOLE_LOGGING = False

# If True, Hifumi will not run until it's toggled to False
# Useful if the bot is running into PM2 and need to fix high priority bugs or
# test something
SAFE_SHUTDOWN = False
