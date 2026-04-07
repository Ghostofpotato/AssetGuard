"""
 Copyright (C) 2015-2024, AssetGuard Inc.
 Created by AssetGuard, Inc. <info@assetguard.com>.
 This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""
import pytest
import sys

from assetguard_testing.tools.monitors import file_monitor
from assetguard_testing.modules.modulesd.sca import patterns
from assetguard_testing.constants.paths.logs import ASSETGUARD_LOG_PATH
from assetguard_testing.utils import callbacks
from assetguard_testing.constants.platforms import WINDOWS

# Fixtures
@pytest.fixture()
def wait_for_sca_enabled():
    '''
    Wait for the sca module to start.
    '''
    log_monitor = file_monitor.FileMonitor(ASSETGUARD_LOG_PATH)
    log_monitor.start(callback=callbacks.generate_callback(patterns.SCA_ENABLED), timeout=60)
    assert log_monitor.callback_result
