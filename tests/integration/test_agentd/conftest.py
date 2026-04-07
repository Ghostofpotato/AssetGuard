# Copyright (C) 2015-2024, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import os
import pytest
import time

from assetguard_testing.constants.paths.variables import AGENTD_STATE
from assetguard_testing.constants.paths.configurations import ASSETGUARD_CLIENT_KEYS_PATH
from assetguard_testing.utils.client_keys import add_client_keys_entry


@pytest.fixture()
def remove_state_file() -> None:
    # Remove state file to check if agent behavior is as expected
    os.remove(AGENTD_STATE) if os.path.exists(AGENTD_STATE) else None


@pytest.fixture()
def clean_keys() -> None:
    # Cleans content of client.keys file
    with open(ASSETGUARD_CLIENT_KEYS_PATH, 'w'):
        pass
    time.sleep(1)


@pytest.fixture()
def add_keys() -> None:
    # Add content of client.keys file
    add_client_keys_entry("001", "ubuntu-agent", "any", "SuperSecretKey")


@pytest.fixture()
def remove_keys_file(test_metadata) -> None:
    # Remove keys file if needed
    if(test_metadata['DELETE_KEYS_FILE']):
        os.remove(ASSETGUARD_CLIENT_KEYS_PATH) if os.path.exists(ASSETGUARD_CLIENT_KEYS_PATH) else None


@pytest.fixture(autouse=True)
def autostart_simulators() -> None:
    yield
