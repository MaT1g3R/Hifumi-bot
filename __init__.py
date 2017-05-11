"""
Hifumi
~~~~~~~~~~~~~~~~~~~

Hifumi, a multifunctional Discord bot.

:copyright: (c) 2017 Hifumi - the Discord Bot Project
:license: GNU, see LICENSE for more details.

"""
from collections import namedtuple
from pathlib import Path

__title__ = 'Hifumi'
__author__ = ['Underforest#1284', 'InternalLight#9391', 'ラブアローシュート#6728']
__author_plain__ = ['Underforest', 'InternalLight', 'MaT1g3R']
__helper__ = ['Wolke#6746']
__helper_plain__ = ['DasWolke']
__license__ = 'GNU General Public License v3.0'
__copyright__ = 'Copyright 2017 Hifumi - the Discord Bot Project'
__version__ = '0.0.1'

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(
    major=0, minor=0, micro=1, releaselevel='alpha', serial=0
)

with open(Path('./config/simple_license')) as f:
    LICENSE = f.read()
    f.close()
