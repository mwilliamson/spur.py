#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='spur.local',
    version='0.3.7',
    description='Run commands and manipulate files locally',
    long_description=read("README"),
    author='Michael Williamson',
    url='http://github.com/mwilliamson/spur.py',
    keywords="shell subprocess process",
    packages=['spur'],
)
