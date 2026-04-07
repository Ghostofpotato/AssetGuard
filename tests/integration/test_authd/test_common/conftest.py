"""
Copyright (C) 2015-2024, AssetGuard Inc.
Created by AssetGuard, Inc. <info@assetguard.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""
import pytest

from assetguard_testing.constants.paths.configurations import ASSETGUARD_CLIENT_KEYS_PATH
from assetguard_testing.utils import file
from . import utils


@pytest.fixture()
def clean_agents_ctx(stop_authd):
    """
    Clean agents files.
    """
    file.truncate_file(ASSETGUARD_CLIENT_KEYS_PATH)
    utils.clean_rids()
    utils.clean_agents_timestamp()
    utils.clean_diff()

    yield

    file.truncate_file(ASSETGUARD_CLIENT_KEYS_PATH)
    utils.clean_rids()
    utils.clean_agents_timestamp()
    utils.clean_diff()
