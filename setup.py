from pip.req import parse_requirements
from setuptools import find_packages, setup

from __init__ import *


def read(fname):
    with open(fname) as f:
        res = f.read()
        f.close()
        return res


setup(
    name=__title__.lower(),
    version=__version__,
    packages=find_packages(),
    install_requires=[
        str(ir.req) for ir in parse_requirements('requirements.txt')],
    include_package_data=True,
    url='http://www.hifumibot.xyz',
    license=__license__,
    author=__author__,
    author_email='neovisatoons@gmail.com',
    description='Hifumi, a multifunctional Discord bot.',
    long_description=read('README.md')
)
