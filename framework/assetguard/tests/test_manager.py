#!/usr/bin/env python
# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import json
import operator
import os
import socket
import sys
from unittest.mock import patch, MagicMock, mock_open

import pytest

with patch('assetguard.core.common.assetguard_uid'):
    with patch('assetguard.core.common.assetguard_gid'):
        sys.modules['assetguard.rbac.orm'] = MagicMock()
        import assetguard.rbac.decorators
        from assetguard.tests.util import RBAC_bypasser

        del sys.modules['assetguard.rbac.orm']
        assetguard.rbac.decorators.expose_resources = RBAC_bypasser

        from assetguard.manager import *
        from assetguard.core.manager import LoggingFormat
        from assetguard.core.tests.test_manager import get_logs
        from assetguard import AssetGuardInternalError, AssetGuardError

test_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


@pytest.fixture(scope='module', autouse=True)
def mock_assetguard_path():
    with patch('assetguard.core.common.ASSETGUARD_PATH', new=test_data_path):
        yield


class InitManager:
    def __init__(self):
        """Sets up necessary environment to test manager functions"""
        # path for temporary API files
        self.api_tmp_path = os.path.join(test_data_path, 'tmp')


@pytest.fixture(scope='module')
def test_manager():
    # Set up
    test_manager = InitManager()
    return test_manager


manager_status = {'assetguard-manager-analysisd': 'running', 'assetguard-manager-authd': 'running',
 'assetguard-manager-monitord': 'running', 'assetguard-manager-remoted': 'running',
 'assetguard-manager-clusterd': 'running', 'assetguard-manager-modulesd': 'running',
 'assetguard-manager-db': 'running', 'assetguard-manager-apid': 'running'}

@patch('assetguard.core.manager.status', return_value=manager_status)
def test_get_status(mock_status):
    """Tests get_status() function works"""
    result = get_status()

    # Assert there are no errors and type returned
    assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
    assert result.render()['data']['total_failed_items'] == 0


@pytest.mark.parametrize('tag, level, total_items, sort_by, sort_ascending', [
    (None, None, 7, None, None),
    ('assetguard-manager-modulesd:database', None, 2, None, None),
    ('assetguard-manager-modulesd:aws-s3', None, 5, None, None),
    ('random', None, 0, ['timestamp'], True),
    (None, 'info', 2, ['timestamp'], False),
    (None, 'error', 1, ['level'], True),
    (None, 'debug', 2, ['level'], False),
    (None, None, 7, ['tag'], True),
    (None, 'random', 0, None, True),
    (None, 'warning', 2, None, False)
])
@patch("assetguard.core.manager.get_assetguard_active_logging_format", return_value=LoggingFormat.plain)
@patch("assetguard.core.manager.exists", return_value=True)
def test_assetguard_log(mock_exists, mock_active_logging_format, tag, level, total_items, sort_by, sort_ascending):
    """Test reading assetguard-manager.log file contents.

    Parameters
    ----------
    level : str
        Filters by log type: all, error or info.
    tag : str
        Filters by log category (i.e. assetguard-manager-remoted).
    total_items : int
        Expected items to be returned after calling assetguard_log.
    sort_by : list
        Fields to sort the items by.
    sort_ascending : boolean
        Sort in ascending (true) or descending (false) order.
    """
    with patch('assetguard.core.manager.tail') as tail_patch:
        # Return assetguard_log_file when calling tail() method
        assetguard_log_file = get_logs()
        tail_patch.return_value = assetguard_log_file.splitlines()

        result = assetguard_log(level=level, tag=tag, sort_by=sort_by, sort_ascending=sort_ascending)

        # Assert type, number of items and presence of trailing characters
        assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
        assert result.render()['data']['total_affected_items'] == total_items
        assert all(log['description'][-1] != '\n' for log in result.render()['data']['affected_items'])
        if tag is not None:
            assert all('\n' not in log['description'] for log in result.render()['data']['affected_items'])
        if sort_by:
            reversed_result = assetguard_log(level=level, tag=tag, sort_by=sort_by, sort_ascending=not sort_ascending)
            for i in range(total_items):
                assert result.render()['data']['affected_items'][i][sort_by[0]] == \
                       reversed_result.render()['data']['affected_items'][total_items - 1 - i][sort_by[0]]


@pytest.mark.parametrize('q, field, operation, values', [
    ('level=debug,level=error', 'level', 'OR', 'debug, error'),
    ('timestamp=2019/03/26 19:49:15', 'timestamp', '=', '2019/03/26T19:49:15Z'),
    ('timestamp<2019/03/26 19:49:14', 'timestamp', '<', '2019/03/26T19:49:15Z'),
])
@patch("assetguard.core.manager.get_assetguard_active_logging_format", return_value=LoggingFormat.plain)
@patch("assetguard.core.manager.exists", return_value=True)
def test_assetguard_log_q(mock_exists, mock_active_logging_format, q, field, operation, values):
    """Check that the 'q' parameter is working correctly.

    Parameters
    ----------
    q : str
        Query to execute.
    field : str
        Field affected by the query.
    operation : str
        Operation type to be performed in the query.
    values : str
        Values used for the comparison.
    """
    with patch('assetguard.core.manager.tail') as tail_patch:
        assetguard_log_file = get_logs()
        tail_patch.return_value = assetguard_log_file.splitlines()

        result = assetguard_log(q=q)

        if operation != 'OR':
            operators = {'=': operator.eq, '!=': operator.ne, '<': operator.lt, '>': operator.gt}
            assert all(operators[operation](log[field], values) for log in result.render()['data']['affected_items'])
        else:
            assert all(log[field] in values for log in result.render()['data']['affected_items'])


@patch("assetguard.core.manager.get_assetguard_active_logging_format", return_value=LoggingFormat.plain)
@patch("assetguard.core.manager.exists", return_value=True)
def test_assetguard_log_summary(mock_exists, mock_active_logging_format):
    """Tests assetguard_log_summary function works and returned data match with expected"""
    expected_result = {
        'assetguard-manager-modulesd:aws-s3': {'all': 5, 'info': 2, 'error': 1, 'critical': 0, 'warning': 2, 'debug': 0},
        'assetguard-manager-modulesd:database': {'all': 2, 'info': 0, 'error': 0, 'critical': 0, 'warning': 0, 'debug': 2}
    }

    logs = get_logs().splitlines()
    with patch('assetguard.core.manager.tail', return_value=logs):
        result = assetguard_log_summary()

        # Assert data match what was expected and type of the result.
        assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
        assert result.render()['data']['total_affected_items'] == len(expected_result.keys())
        assert all(all(value == expected_result[key] for key, value in item.items())
                   for item in result.render()['data']['affected_items'])


def test_get_api_config():
    """Checks that get_api_config method is returning current api_conf dict."""
    result = get_api_config().render()

    assert 'node_api_config' in result['data']['affected_items'][0]
    assert result['data']['affected_items'][0]['node_name'] == 'node01'


@patch('socket.socket')
@patch('assetguard.core.cluster.utils.fcntl')
@patch('assetguard.core.cluster.utils.open')
@patch('os.path.exists', return_value=True)
def test_restart_ok(mock_exists, mock_path, mock_fcntl, mock_socket):
    """Tests restarting a manager"""
    result = restart()

    # Assert there are no errors and type of the result.
    assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
    assert result.render()['data']['total_failed_items'] == 0


@patch('assetguard.core.cluster.utils.open')
@patch('assetguard.core.cluster.utils.fcntl')
@patch('os.path.exists', return_value=False)
def test_restart_ko_socket(mock_exists, mock_fcntl, mock_open):
    """Tests restarting a manager exceptions"""

    # Socket path not exists
    with pytest.raises(AssetGuardInternalError, match='.* 1901 .*'):
        restart()

    # Socket error
    with patch("os.path.exists", return_value=True):
        with patch('socket.socket', side_effect=socket.error):
            with pytest.raises(AssetGuardInternalError, match='.* 1902 .*'):
                restart()

        with patch('socket.socket.connect'):
            with patch('socket.socket.send', side_effect=socket.error):
                with pytest.raises(AssetGuardInternalError, match='.* 1014 .*'):
                    restart()


@pytest.mark.parametrize('error_flag, error_msg', [
    (0, ""),
    (1, "2019/02/27 11:30:07 assetguard-manager-clusterd: ERROR: [Cluster] [Main] Error 3004 - Error in cluster configuration: "
        "Unspecified key"),
    (1, "2019/02/27 11:30:24 assetguard-manager-authd: ERROR: (1230): Invalid element in the configuration: "
        "'use_source_i'.\n2019/02/27 11:30:24 assetguard-manager-authd: ERROR: (1202): Configuration error at "
        "'/var/assetguard-manage/etc/assetguard-manager.conf'.")
])
@patch('assetguard.manager.validate_assetguard_conf')
def test_validation(mock_validate_assetguard_conf, error_flag, error_msg):
    """Test validation() method works as expected

    Tests configuration validation function with multiple scenarios:
        * No errors found in configuration
        * Error found in cluster configuration
        * Error found in any other configuration

    Parameters
    ----------
    error_flag : int
        Error flag (0 = success, 1 = error).
    error_msg : str
        Error message if validation fails.
    """
    if error_flag == 0:
        # Success case - validation passes
        mock_validate_assetguard_conf.return_value = {'status': 'OK'}
    else:
        # Error case - validation fails
        mock_validate_assetguard_conf.side_effect = AssetGuardError(1908, extra_message=error_msg)

    result = validation()

    # Assert if error was returned
    assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
    assert result.render()['data']['total_failed_items'] == error_flag


@pytest.mark.parametrize('exception', [
    AssetGuardInternalError(1020),  # File not found
    AssetGuardError(1113),  # XML validation error
    AssetGuardError(1908)  # General validation error
])
@patch('assetguard.manager.validate_assetguard_conf')
def test_validation_ko(mock_validate, exception):
    mock_validate.side_effect = exception

    if isinstance(exception, AssetGuardInternalError):
        with pytest.raises(AssetGuardInternalError, match='.* 1020 .*'):
            validation()
    else:
        result = validation()
        assert not result.affected_items
        assert result.total_failed_items == 1


@patch('assetguard.core.configuration.get_active_configuration')
def test_get_config(mock_act_conf):
    """Tests get_config() method works as expected"""
    get_config('component', 'config')

    # Assert whether get_active_configuration() method receives the expected parameters.
    mock_act_conf.assert_called_once_with(component='component', configuration='config')


def test_get_config_ko():
    """Tests get_config() function returns an error"""
    result = get_config()

    assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1307


@pytest.mark.parametrize('raw', [True, False])
def test_read_assetguard_conf(raw):
    """Tests read_assetguard_conf() function works as expected"""
    result = read_assetguard_conf(raw=raw)

    if raw:
        assert isinstance(result, str), 'No expected result type'
    else:
        assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
        assert result.render()['data']['total_failed_items'] == 0


def test_read_assetguard_con_ko():
    """Tests read_assetguard_conf() function returns an error"""
    result = read_assetguard_conf(section='test')

    assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1102


@patch('assetguard.core.common.os.chown')
@patch('assetguard.core.common.os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='test-uuid')
@patch('assetguard.core.common.assetguard_gid', return_value=0)
@patch('assetguard.core.common.assetguard_uid', return_value=0)
def test_get_basic_info(mock_uid, mock_gid, mock_open_file, mock_exists, mock_chown):
    """Tests get_basic_info() function works as expected"""
    result = get_basic_info()

    assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
    assert result.render()['data']['total_failed_items'] == 0


@patch('assetguard.manager.safe_move')
@patch('assetguard.manager.remove')
@patch('assetguard.manager.exists', return_value=True)
@patch('assetguard.manager.full_copy')
@patch('assetguard.manager.validate_assetguard_xml')
@patch('assetguard.manager.write_assetguard_conf')
@patch('assetguard.manager.validate_assetguard_conf', return_value={'status': 'OK'})
def test_update_assetguard_conf(validate_conf_mock, write_mock, validate_xml_mock, full_copy_mock, exists_mock,
                           remove_mock, move_mock):
    """Test update_assetguard_conf works as expected."""
    result = update_assetguard_conf(new_conf="placeholder config")
    write_mock.assert_called_once()
    validate_conf_mock.assert_called_once()
    assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
    assert result.render()['data']['total_failed_items'] == 0
    remove_mock.assert_called_once()


@pytest.mark.parametrize('new_conf', [
    None,
    "invalid configuration"
])
@patch('assetguard.manager.safe_move')
@patch('assetguard.manager.remove')
@patch('assetguard.manager.exists', return_value=True)
@patch('assetguard.manager.full_copy')
@patch('assetguard.manager.validate_assetguard_xml')
@patch('assetguard.manager.write_assetguard_conf')
@patch('assetguard.manager.validate_assetguard_conf')
def test_update_assetguard_conf_ko(validate_conf_mock, write_mock, validate_xml_mock, full_copy_mock, exists_mock,
                              remove_mock, move_mock, new_conf):
    """Test update_assetguard_conf() function return an error and restore the configuration if the provided configuration
    is not valid."""
    # For invalid configuration case, make validate_assetguard_conf return invalid status
    if new_conf == "invalid configuration":
        validate_conf_mock.return_value = {'status': 'ERROR'}

    result = update_assetguard_conf(new_conf=new_conf)
    assert isinstance(result, AffectedItemsAssetGuardResult), 'No expected result type'
    assert result.render()['data']['failed_items'][0]['error']['code'] == 1125
    move_mock.assert_called_once()
