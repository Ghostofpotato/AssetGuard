'''
copyright: Copyright (C) 2015-2024, AssetGuard Inc.

           Created by AssetGuard, Inc. <info@assetguard.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: The 'assetguard-manager-analysisd' daemon receives the log messages and compares them to the rules.
       It then creates an alert when a log message matches an applicable rule.
       Specifically, these tests will check if the 'assetguard-manager-analysisd' daemon correctly handles
       incoming events related to file modification.

components:
    - analysisd

suite: event_messages

targets:
    - manager

daemons:
    - assetguard-manager-analysisd
    - assetguard-manager-db

os_platform:
    - linux

os_version:
    - Arch Linux
    - Amazon Linux 2
    - Amazon Linux 1
    - CentOS 8
    - CentOS 7
    - Debian Buster
    - Red Hat 8
    - Ubuntu Focal
    - Ubuntu Bionic

references:
    - https://documentation.assetguard.com/current/user-manual/reference/daemons/assetguard-manager-analysisd.html

tags:
    - events
    - fim
'''
import pytest

from pathlib import Path

from assetguard_testing import session_parameters
from assetguard_testing.constants.daemons import ASSETGUARD_DB_DAEMON, ANALYSISD_DAEMON
from assetguard_testing.constants.paths.sockets import ASSETGUARD_DB_SOCKET_PATH, ANALYSISD_QUEUE_SOCKET_PATH
from assetguard_testing.modules.analysisd import patterns, configuration as analysisd_config
from assetguard_testing.modules.monitord import configuration as monitord_config
from assetguard_testing.tools import mitm
from assetguard_testing.utils import configuration, callbacks

from . import TEST_CASES_PATH

pytestmark = [pytest.mark.server, pytest.mark.tier(level=0)]

# Configuration and cases data.
test_cases_path = Path(TEST_CASES_PATH, 'cases_event_messages.yaml')

# Test configurations.
_, test_metadata, test_cases_ids = configuration.get_test_cases_data(test_cases_path)

# Test internal options.
local_internal_options = {analysisd_config.ANALYSISD_DEBUG: '2', monitord_config.MONITORD_ROTATE_LOG: '0'}

# Test variables.
receiver_sockets_params = [(ANALYSISD_QUEUE_SOCKET_PATH, 'AF_UNIX', 'UDP')]

mitm_wdb = mitm.ManInTheMiddle(address=ASSETGUARD_DB_SOCKET_PATH, family='AF_UNIX', connection_protocol='TCP')
mitm_analysisd = mitm.ManInTheMiddle(address=ANALYSISD_QUEUE_SOCKET_PATH, family='AF_UNIX', connection_protocol='UDP')
monitored_sockets_params = [(ASSETGUARD_DB_DAEMON, mitm_wdb, True), (ANALYSISD_DAEMON, mitm_analysisd, True)]

receiver_sockets, monitored_sockets = None, None  # Set in the fixtures


# Test function.
@pytest.mark.parametrize('test_metadata', test_metadata, ids=test_cases_ids)
def test_event_messages(test_metadata, configure_local_internal_options, configure_sockets_environment_module,
                       connect_to_sockets_module, wait_for_analysisd_startup):
    '''
    description: Check if when the 'assetguard-manager-analysisd' daemon socket receives a message with
                 a file modification-related event, it generates the corresponding alert
                 that sends to the 'assetguard-manager-db' daemon socket.
                 The 'validate_analysis_alert' function checks if an 'analysisd' event
                 is properly formatted.

    assetguard_min_version: 4.2.0

    tier: 0

    parameters:
        - test_metadata:
            type: dict
            brief: Test case metadata.
        - configure_local_internal_options:
            type: fixture
            brief: Configure the AssetGuard local internal options.
        - configure_sockets_environment_module:
            type: fixture
            brief: Configure environment for sockets and MITM.
        - connect_to_sockets_module:
            type: fixture
            brief: Connect to a given list of sockets.
        - wait_for_analysisd_startup:
            type: fixture
            brief: Wait until the 'assetguard-manager-analysisd' has begun and the 'alerts.json' file is created.

    assertions:
        - Verify that the alerts generated are consistent with the events received.

    input_description: Different test cases that are contained in an external YAML file (event_messages.yaml)
                       that includes 'syscheck' events data and the expected output.

    expected_output:
        - Multiple messages (alert logs) corresponding to each test case,
          located in the external input data file.

    tags:
        - alerts
        - man_in_the_middle
        - wdb_socket
    '''
    callback = callbacks.generate_callback(patterns.ANALYSISD_QUEUE_DB_MESSSAGE)

    # Start monitor
    receiver_sockets[0].send(test_metadata['input'])
    monitored_sockets[0].start(callback=callback, timeout=session_parameters.default_timeout)

    # Check that expected message appears
    expected = callback(test_metadata['output'])
    assert monitored_sockets[0].callback_result == expected, 'Failed test case stage: {}'.format(test_metadata['stage'])
