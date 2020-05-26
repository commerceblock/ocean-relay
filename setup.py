#!/usr/bin/env python
from setuptools import setup, find_packages
import os

setup(name='relay',
      version='0.1',
      description='Ocean Relay daemon',
      author='CommerceBlock',
      author_email='tom@commerceblock.com',
      url='http://github.com/commerceblock/ocean-relay',
      packages=find_packages(),
      scripts=[],
      include_package_data=True,
      data_files=[],
)
