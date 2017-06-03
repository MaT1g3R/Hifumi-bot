from setuptools import setup, find_packages
from pip.req import parse_requirements
import os

def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_reqs = parse_requirements("./config/requirements.txt")
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='hifumi',
    version='0.0.1',
    packages=find_packages()
    install_requires=reqs,
    include_package_data=True,
    url='http://www.hifumibot.xyz',
    license='GPL-3.0',
    author='Underforest',
    author_email='neovisatoons@gmail.com',
    description='The official module for Hifumi, the Discord bot.',
    long_description=read('README.md')
      )
