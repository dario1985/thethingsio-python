#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from thethingsio import __version__ as version

setup(
    name='thethingsio',
    version=version,
    description='Python thethings.iO API client',
    long_description='Python thethings.iO API client',
    author='thethings.iO',
    author_email='hello@thethings.io',
    url='http://www.thethings.io',
    download_url='https://github.com/theThings/jailed-node/archive/v' + version +'.tar.gz',
    packages=[
        'thethingsio',
        'thethingsio.tools',
    ],
    install_requires=[
    ],
    extras_require={
    },
)
