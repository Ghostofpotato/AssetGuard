# Copyright (C) 2015-2024, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import pytest

from assetguard_testing.constants.paths.logs import ASSETGUARD_LOG_PATH
from assetguard_testing.modules.modulesd import patterns
from assetguard_testing.tools.monitors.file_monitor import FileMonitor
from assetguard_testing.utils import callbacks


@pytest.fixture()
def wait_for_office365_start():
    # Wait for module office365 starts
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(callback=callbacks.generate_callback(patterns.MODULESD_STARTED, {
                              'integration': 'Office365'
                          }))
    assert (assetguard_log_monitor.callback_result == None), f'Error invalid configuration event not detected'
