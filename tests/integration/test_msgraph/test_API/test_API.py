'''
copyright: Copyright (C) 2015-2024, AssetGuard Inc.

           Created by AssetGuard, Inc. <info@assetguard.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: The AssetGuard 'ms-graph' module is capable of communicating with Microsoft Graph & parsing its various
       logging sources, with an emphasis on the security resource. This includes a full set of rules for
       categorizing these logs, alongside a standardized suite of configuration options that mirror other
       modules, such as Azure, GCP, and Office365.

components:
    - ms-graph

suite: configuration

targets:
    - agent

daemons:
    - assetguard-modulesd

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

tags:
    - ms-graph_configuration
'''
import pytest
from pathlib import Path

from assetguard_testing.constants.paths.logs import ASSETGUARD_LOG_PATH
from assetguard_testing.modules.modulesd.configuration import MODULESD_DEBUG
from assetguard_testing.modules.modulesd import patterns
from assetguard_testing.tools.monitors.file_monitor import FileMonitor
from assetguard_testing.utils.configuration import get_test_cases_data
from assetguard_testing.utils.configuration import load_configuration_template
from assetguard_testing.utils import callbacks
from assetguard_testing.utils.services import control_service
from assetguard_testing.utils.file import truncate_file
from . import CONFIGS_PATH, TEST_CASES_PATH

# Marks
pytestmark = [pytest.mark.linux, pytest.mark.tier(level=0)]

# Configuration and cases data.
configs_path = Path(CONFIGS_PATH, 'config_API.yaml')

# ---------------------------------------------------- TEST_FUTURE_EVENTS ---------------------------------------------
# Test configurations
t1_cases_path = Path(TEST_CASES_PATH, 'cases_future_yes.yaml')
t1_configuration_parameters, t1_configuration_metadata, t1_case_ids = get_test_cases_data(t1_cases_path)
t1_configurations = load_configuration_template(configs_path, t1_configuration_parameters,
                                                t1_configuration_metadata)

# Test configurations
t2_cases_path = Path(TEST_CASES_PATH, 'cases_future_no.yaml')
t2_configuration_parameters, t2_configuration_metadata, t2_case_ids = get_test_cases_data(t2_cases_path)
t2_configurations = load_configuration_template(configs_path, t2_configuration_parameters,
                                                t2_configuration_metadata)

# ---------------------------------------------------- TEST_CURL_SIZE ---------------------------------------------------
# Test configurations
t3_cases_path = Path(TEST_CASES_PATH, 'cases_curl_size.yaml')
t3_configuration_parameters, t3_configuration_metadata, t3_case_ids = get_test_cases_data(t3_cases_path)
t3_configurations = load_configuration_template(configs_path, t3_configuration_parameters,
                                                t3_configuration_metadata)

# ---------------------------------------------------- TEST_RESOURCES ---------------------------------------------------
# Test configurations
t4_cases_path = Path(TEST_CASES_PATH, 'cases_valid_resource.yaml')
t4_configuration_parameters, t4_configuration_metadata, t4_case_ids = get_test_cases_data(t4_cases_path)
t4_configurations = load_configuration_template(configs_path, t4_configuration_parameters,
                                                t4_configuration_metadata)

# Test configurations
t5_cases_path = Path(TEST_CASES_PATH, 'cases_invalid_resource.yaml')
t5_configuration_parameters, t5_configuration_metadata, t5_case_ids = get_test_cases_data(t5_cases_path)
t5_configurations = load_configuration_template(configs_path, t5_configuration_parameters,
                                                t5_configuration_metadata)

# ---------------------------------------------------- TEST_AUTH_TOKEN ---------------------------------------------------
# Test configurations
t6_cases_path = Path(TEST_CASES_PATH, 'cases_valid_auth.yaml')
t6_configuration_parameters, t6_configuration_metadata, t6_case_ids = get_test_cases_data(t6_cases_path)
t6_configurations = load_configuration_template(configs_path, t6_configuration_parameters,
                                                t6_configuration_metadata)

# Test configurations
t7_cases_path = Path(TEST_CASES_PATH, 'cases_invalid_auth.yaml')
t7_configuration_parameters, t7_configuration_metadata, t7_case_ids = get_test_cases_data(t7_cases_path)
t7_configurations = load_configuration_template(configs_path, t7_configuration_parameters,
                                                t7_configuration_metadata)

# Test configurations.
daemons_handler_configuration = {'all_daemons': True, 'ignore_errors': True}
local_internal_options = {MODULESD_DEBUG: '2'}


# Tests
@pytest.mark.parametrize('test_configuration, test_metadata', zip(t1_configurations, t1_configuration_metadata), ids=t1_case_ids)
def test_future_events_yes(test_configuration, test_metadata, set_assetguard_configuration, configure_local_internal_options,
                 truncate_monitored_files, daemons_handler, wait_for_msgraph_start, proxy_setup):
    '''
    description: Check 'ms-graph' behavior when `only_future_events` tag is set to yes.
    assetguard_min_version: 4.6.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - set_assetguard_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'assetguard.log' file and start a new monitor.
        - daemons_handler:
            type: fixture
            brief: Manages daemons to reset AssetGuard.
        - wait_for_msgraph_start:
            type: fixture
            brief: Checks integration start message does not appear.
        - proxy_setup:
            type: fixture
            brief: Setups the API proxy application.

    assertions:
        - Verify that when the `only_future_events` option is set to `yes`, the ms-graph module saves a bookmark,
        and after a restart, it waits for a first scan.

    input_description: A configuration template is contained in an external YAML file
                       (config_API.yaml). That template is combined with different test cases defined in
                       the module. Those include configuration settings for the 'ms-graph' module.

    expected_output:
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*Bookmark updated'
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*seconds to run first scan'
    '''

    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)

    assetguard_log_monitor.start(callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*Bookmark updated"), timeout=70)

    if(assetguard_log_monitor.callback_result != None):
        control_service('stop')
        truncate_file(ASSETGUARD_LOG_PATH)
        control_service('start')
        assetguard_log_monitor.start(callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*seconds to run first scan"), timeout=70)
        assert (assetguard_log_monitor.callback_result != None), f'Error, `first scan` not found in log'
    else:
        assert (False), f'Error `Bookmark updated` not found in log'


@pytest.mark.skip(reason="Unstable, the testing tool is not returning the expected values. This needs to be investigated.")
@pytest.mark.parametrize('test_configuration, test_metadata', zip(t2_configurations, t2_configuration_metadata), ids=t2_case_ids)
def test_future_events_no(test_configuration, test_metadata, set_assetguard_configuration, configure_local_internal_options,
                 truncate_monitored_files, daemons_handler, wait_for_msgraph_start, proxy_setup):
    '''
    description: Check 'ms-graph' behavior when `only_future_events` tag is set to no.
    assetguard_min_version: 4.6.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - set_assetguard_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'assetguard.log' file and start a new monitor.
        - daemons_handler:
            type: fixture
            brief: Manages daemons to reset AssetGuard.
        - wait_for_msgraph_start:
            type: fixture
            brief: Checks integration start message does not appear.
        - proxy_setup:
            type: fixture
            brief: Setups the API proxy application.

    assertions:
        - Verify that when the `only_future_events` option is set to `no`, the ms-graph module saves a bookmark,
        and after a restart, it does not wait for a first scan.

    input_description: A configuration template is contained in an external YAML file
                       (config_API.yaml). That template is combined with different test cases defined in
                       the module. Those include configuration settings for the 'ms-graph' module.

    expected_output:
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*Bookmark updated'
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*seconds to run next scan'
    '''

    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)

    assetguard_log_monitor.start(callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*Bookmark updated"))

    if(assetguard_log_monitor.callback_result != None):
        control_service('stop')
        truncate_file(ASSETGUARD_LOG_PATH)
        control_service('start')

        assetguard_log_monitor.start(callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*seconds to run next scan"))
        assert (assetguard_log_monitor.callback_result != None), f'Error, `next scan` not found in log'

        assetguard_log_monitor.start(callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*seconds to run first scan"), timeout=10)
        assert (assetguard_log_monitor.callback_result == None), f'Error, `first scan` not found in log'
    else:
        assert (False), f'Error `Bookmark updated` not found in log'


@pytest.mark.parametrize('test_configuration, test_metadata', zip(t3_configurations, t3_configuration_metadata), ids=t3_case_ids)
def test_curl_max_size(test_configuration, test_metadata, set_assetguard_configuration, configure_local_internal_options,
                 truncate_monitored_files, daemons_handler, wait_for_msgraph_start, proxy_setup):
    '''
    description: Check 'ms-graph' behavior when `curl_max_size` is reached.
    assetguard_min_version: 4.6.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - set_assetguard_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'assetguard.log' file and start a new monitor.
        - daemons_handler:
            type: fixture
            brief: Manages daemons to reset AssetGuard.
        - wait_for_msgraph_start:
            type: fixture
            brief: Checks integration start message does not appear.
        - proxy_setup:
            type: fixture
            brief: Setups the API proxy application.

    assertions:
        - Verify that when the `curl_max_size` is less than the request size, the ms-graph module shows a warning.

    input_description: A configuration template is contained in an external YAML file
                       (config_API.yaml). That template is combined with different test cases defined in
                       the module. Those include configuration settings for the 'ms-graph' module.

    expected_output:
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*Reached maximum CURL size'
    '''

    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)

    assetguard_log_monitor.start(callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*Reached maximum CURL size"))
    assert (assetguard_log_monitor.callback_result != None), f'Error, `maximum CURL size` not found in log'


@pytest.mark.parametrize('test_configuration, test_metadata', zip(t4_configurations, t4_configuration_metadata), ids=t4_case_ids)
def test_valid_resource(test_configuration, test_metadata, set_assetguard_configuration, configure_local_internal_options,
                 truncate_monitored_files, daemons_handler, wait_for_msgraph_start, proxy_setup):
    '''
    description: Check 'ms-graph' behavior when `resource` tags `name` and `relationship` are valid.
    assetguard_min_version: 4.6.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - set_assetguard_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'assetguard.log' file and start a new monitor.
        - daemons_handler:
            type: fixture
            brief: Manages daemons to reset AssetGuard.
        - wait_for_msgraph_start:
            type: fixture
            brief: Checks integration start message does not appear.
        - proxy_setup:
            type: fixture
            brief: Setups the API proxy application.

    assertions:
        - Verify that when the `resource` `name` equals `security` and has `relationship` as `alerts_v2` and `incidents`
          it gets the correct responses.

    input_description: A configuration template is contained in an external YAML file
                       (config_API.yaml). That template is combined with different test cases defined in
                       the module. Those include configuration settings for the 'ms-graph' module.

    expected_output:
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*microsoft.graph.security.alert'
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*microsoft.graph.security.incident'
    '''

    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)

    assetguard_log_monitor.start(callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*microsoft.graph.security.alert"))
    assert (assetguard_log_monitor.callback_result != None), f'Error, `security.alert` not found in log'

    assetguard_log_monitor.start(callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*microsoft.graph.security.incident"))
    assert (assetguard_log_monitor.callback_result != None), f'Error, `security.incident` not found in log'


@pytest.mark.parametrize('test_configuration, test_metadata', zip(t5_configurations, t5_configuration_metadata), ids=t5_case_ids)
def test_invalid_resource(test_configuration, test_metadata, set_assetguard_configuration, configure_local_internal_options,
                 truncate_monitored_files, daemons_handler, wait_for_msgraph_start, proxy_setup):
    '''
    description: Check 'ms-graph' behavior when `resource` tags `name` and `relationship` are invalid.
    assetguard_min_version: 4.6.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - set_assetguard_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'assetguard.log' file and start a new monitor.
        - daemons_handler:
            type: fixture
            brief: Manages daemons to reset AssetGuard.
        - wait_for_msgraph_start:
            type: fixture
            brief: Checks integration start message does not appear.
        - proxy_setup:
            type: fixture
            brief: Setups the API proxy application.

    assertions:
        - Verify that when the `resource` values `name` and `relationship` are invalid for the API
          it gets the correct error.

    input_description: A configuration template is contained in an external YAML file
                       (config_API.yaml). That template is combined with different test cases defined in
                       the module. Those include configuration settings for the 'ms-graph' module.

    expected_output:
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*Received unsuccessful status
            code when attempting to get relationship \'invalid\'
    '''

    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)

    assetguard_log_monitor.start(
        callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*Received unsuccessful "\
                                             r"status code when attempting to get relationship \'invalid\'"))
    assert (assetguard_log_monitor.callback_result != None), f'Error, `unsuccessful status code` not found in log'


@pytest.mark.parametrize('test_configuration, test_metadata', zip(t6_configurations, t6_configuration_metadata), ids=t6_case_ids)
def test_valid_auth(test_configuration, test_metadata, set_assetguard_configuration, configure_local_internal_options,
                 truncate_monitored_files, daemons_handler, wait_for_msgraph_start, proxy_setup):
    '''
    description: Check 'ms-graph' behavior when `tenant_id` tag is valid.
    assetguard_min_version: 4.6.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - set_assetguard_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'assetguard.log' file and start a new monitor.
        - daemons_handler:
            type: fixture
            brief: Manages daemons to reset AssetGuard.
        - wait_for_msgraph_start:
            type: fixture
            brief: Checks integration start message does not appear.
        - proxy_setup:
            type: fixture
            brief: Setups the API proxy application.

    assertions:
        - Verify that when the `tenant_id` is valid it does not get an error.

    input_description: A configuration template is contained in an external YAML file
                       (config_API.yaml). That template is combined with different test cases defined in
                       the module. Those include configuration settings for the 'ms-graph' module.

    expected_output:
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*INFO: Scanning tenant'
    '''

    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)

    assetguard_log_monitor.start(callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*INFO: Scanning tenant"))
    assert (assetguard_log_monitor.callback_result != None), f'Error, `Scanning tenant` not found in log'


@pytest.mark.parametrize('test_configuration, test_metadata', zip(t7_configurations, t7_configuration_metadata), ids=t7_case_ids)
def test_invalid_auth(test_configuration, test_metadata, set_assetguard_configuration, configure_local_internal_options,
                 truncate_monitored_files, daemons_handler, wait_for_msgraph_start, proxy_setup):
    '''
    description: Check 'ms-graph' behavior when `resource` tags `name` and `relationship` are invalid.
    assetguard_min_version: 4.6.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - set_assetguard_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'assetguard.log' file and start a new monitor.
        - daemons_handler:
            type: fixture
            brief: Manages daemons to reset AssetGuard.
        - wait_for_msgraph_start:
            type: fixture
            brief: Checks integration start message does not appear.
        - proxy_setup:
            type: fixture
            brief: Setups the API proxy application.

    assertions:
        - Verify that when the `tenant_id` is invalid it gets an error.

    input_description: A configuration template is contained in an external YAML file
                       (config_API.yaml). That template is combined with different test cases defined in
                       the module. Those include configuration settings for the 'ms-graph' module.

    expected_output:
        - r'.*assetguard-(?:manager-)?modulesd:ms-graph.*WARNING: Recieved unsuccessful
            status code when attempting to obtain access token'
    '''

    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)

    assetguard_log_monitor.start(
        callback=callbacks.generate_callback(r".*assetguard-(?:manager-)?modulesd:ms-graph.*WARNING: Received unsuccessful "\
                                             r"status code when attempting to obtain access token"))
    assert (assetguard_log_monitor.callback_result != None), f'Error, `unsuccessful status code` not found in log'
