"""
Copyright (C) 2015-2024, AssetGuard Inc.
Created by AssetGuard, Inc. <info@assetguard.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""
import pytest
import time

from assetguard_testing.utils import database
from assetguard_testing.utils.db_queries.global_db import delete_agent


@pytest.fixture(scope='module')
def clean_databases():
    yield
    database.delete_dbs()


@pytest.fixture(scope='module')
def clean_registered_agents():
    delete_agent()
    time.sleep(5)
