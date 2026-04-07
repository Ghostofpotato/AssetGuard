"""
Copyright (C) 2015-2024, AssetGuard Inc.
Created by AssetGuard, Inc. <info@assetguard.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""
import pytest

from assetguard_testing.constants.paths.logs import ASSETGUARD_API_LOG_FILE_PATH, ASSETGUARD_API_JSON_LOG_FILE_PATH
from assetguard_testing.utils.callbacks import generate_callback
from assetguard_testing.tools.monitors import file_monitor
from assetguard_testing.constants.api import ASSETGUARD_API_PORT
from assetguard_testing.modules.api.patterns import API_STARTED_MSG


@pytest.fixture(scope='module')
def wait_for_api_startup_module():
    """Monitor the API log file to detect whether it has been started or not.

    Raises:
        RuntimeError: When the log was not found.
    """
    # Set the default values
    logs_format = 'plain'
    host = ['0.0.0.0', '::']
    port = ASSETGUARD_API_PORT

    # Check if specific values were set or set the defaults
    file_to_monitor = ASSETGUARD_API_JSON_LOG_FILE_PATH if logs_format == 'json' else ASSETGUARD_API_LOG_FILE_PATH
    monitor_start_message = file_monitor.FileMonitor(file_to_monitor)
    monitor_start_message.start(
        callback=generate_callback(API_STARTED_MSG, {
            'host': str(host),
            'port': str(port)
        })
    )

    if monitor_start_message.callback_result is None:
        raise RuntimeError('The API was not started as expected.')
