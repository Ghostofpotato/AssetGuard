# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

import json
import uuid
from contextvars import ContextVar
from grp import getgrnam
from pwd import getpwnam
from unittest.mock import patch, mock_open

import pytest

from assetguard.core.common import find_assetguard_path, assetguard_uid, assetguard_gid, context_cached, reset_context_cache, \
    get_context_cache, get_installation_uid


@pytest.mark.parametrize('fake_path, expected', [
    ('/var/assetguard-manager/framework/python/lib/python3.7/site-packages/assetguard-3.10.0-py3.7.egg/assetguard', '/var/assetguard-manager'),
    ('/my/custom/path/framework/python/lib/python3.7/site-packages/assetguard-3.10.0-py3.7.egg/assetguard', '/my/custom/path'),
    ('/my/fake/path', '')
])
def test_find_assetguard_path(fake_path, expected):
    with patch('assetguard.core.common.__file__', new=fake_path):
        assert (find_assetguard_path.__wrapped__() == expected)


def test_find_assetguard_path_relative_path():
    with patch('os.path.abspath', return_value='~/framework'):
        assert (find_assetguard_path.__wrapped__() == '~')


def test_assetguard_uid():
    with patch('assetguard.core.common.getpwnam', return_value=getpwnam("root")):
        assetguard_uid()


def test_assetguard_gid():
    with patch('assetguard.core.common.getgrnam', return_value=getgrnam("root")):
        assetguard_gid()


def test_context_cached():
    """Verify that context_cached decorator correctly saves and returns saved value when called again."""

    test_context_cached.calls_to_foo = 0

    @context_cached('foobar')
    def foo(arg='bar', **data):
        test_context_cached.calls_to_foo += 1
        return arg

    # The result of function 'foo' is being cached and it has been called once
    assert foo() == 'bar' and test_context_cached.calls_to_foo == 1, '"bar" should be returned with 1 call to foo.'
    assert foo() == 'bar' and test_context_cached.calls_to_foo == 1, '"bar" should be returned with 1 call to foo.'
    assert isinstance(get_context_cache()[json.dumps({"key": "foobar", "args": [], "kwargs": {}})], ContextVar)

    # foo called with an argument
    assert foo('other_arg') == 'other_arg' and test_context_cached.calls_to_foo == 2, '"other_arg" should be ' \
                                                                                      'returned with 2 calls to foo. '
    assert isinstance(get_context_cache()[json.dumps({"key": "foobar", "args": ['other_arg'], "kwargs": {}})],
                      ContextVar)

    # foo called with the same argument as default, a new context var is created in the cache
    assert foo('bar') == 'bar' and test_context_cached.calls_to_foo == 3, '"bar" should be returned with 3 calls to ' \
                                                                          'foo. '
    assert isinstance(get_context_cache()[json.dumps({"key": "foobar", "args": ['bar'], "kwargs": {}})], ContextVar)

    # Reset cache and calls to foo
    reset_context_cache()
    test_context_cached.calls_to_foo = 0

    # foo called with kwargs, a new context var is created with kwargs not empty
    assert foo(data='bar') == 'bar' and test_context_cached.calls_to_foo == 1, '"bar" should be returned with 1 ' \
                                                                               'calls to foo. '
    assert isinstance(get_context_cache()[json.dumps({"key": "foobar", "args": [], "kwargs": {"data": "bar"}})],
                      ContextVar)


@patch('assetguard.core.stats.assetguard_socket.create_assetguard_socket_message', side_effect=SystemExit)
def test_origin_module_context_var_framework(mock_create_socket_msg):
    """Test that the origin_module context variable is being set to framework."""
    from assetguard.core import stats

    # side_effect used to avoid mocking the rest of functions
    with pytest.raises(SystemExit):
        stats.get_daemons_stats_socket(None)

    assert mock_create_socket_msg.call_args[1]['origin']['module'] == 'framework'


@pytest.mark.asyncio
@patch('assetguard.core.stats.assetguard_socket.create_assetguard_socket_message', side_effect=SystemExit)
@patch('assetguard.core.cluster.dapi.dapi.DistributedAPI.check_assetguard_status', side_effect=None)
async def test_origin_module_context_var_api(mock_check_assetguard_status, mock_create_socket_msg):
    """Test that the origin_module context variable is being set to API."""
    import logging
    from assetguard.core.cluster.dapi import dapi
    from assetguard import stats

    # side_effect used to avoid mocking the rest of functions
    with pytest.raises(SystemExit):
        d = dapi.DistributedAPI(f=stats.get_daemons_stats, logger=logging.getLogger('assetguard'), is_async=True)
        await d.distribute_function()

    assert mock_create_socket_msg.call_args[1]['origin']['module'] == 'API'


@patch('assetguard.core.common.assetguard_uid', return_value=0)
@patch('assetguard.core.common.assetguard_gid', return_value=0)
@patch('assetguard.core.common.os.chmod')
@patch('assetguard.core.common.os.chown')
def test_get_installation_uid_creates_file(chown_mock, chmod_mock, mock_gid, mock_uid, tmp_path):
    """Test get_installation_uid creates the UID file if it doesn't exist."""

    test_path = tmp_path / 'installation_uid'
    with patch('assetguard.core.common.INSTALLATION_UID_PATH', str(test_path)):
        uid = get_installation_uid()

        uuid.UUID(uid)  # should not raise
        with open(test_path, 'r') as f:
            assert f.read().strip() == uid

        chown_mock.assert_called_once()
        chmod_mock.assert_called_once()


@patch('assetguard.core.common.os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='test-uuid')
def test_get_installation_uid_reads_existing(mock_file, mock_exists):
    """Test get_installation_uid reads the UID if the file exists."""
    result = get_installation_uid()
    assert result == 'test-uuid'
