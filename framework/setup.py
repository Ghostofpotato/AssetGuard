#!/usr/bin/env python

# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

from assetguard import __version__

from setuptools import setup, find_namespace_packages

setup(name='assetguard',
      version=__version__,
      description='AssetGuard control with Python',
      url='https://github.com/assetguard',
      author='AssetGuard',
      author_email='hello@assetguard.com',
      license='GPLv2',
      packages=find_namespace_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      package_data={'assetguard': ['core/assetguard.json',
                              'core/cluster/cluster.json', 'rbac/default/*.yaml']},
      include_package_data=True,
      install_requires=[],
      zip_safe=False,
      )
