#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='spur',
    version='0.2.0',
    description='Run commands and manipulate files locally or over SSH using the same interface',
    long_description=read("README"),
    author='Michael Williamson',
    url='http://github.com/mwilliamson/spur.py',
    packages=['spur'],
    install_requires=["paramiko>=1.9.0,<2"],
)
