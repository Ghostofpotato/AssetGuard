#!/usr/bin/env python
# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import os
import sys
from unittest.mock import patch, MagicMock

import pytest

with patch('assetguard.common.assetguard_uid'):
    with patch('assetguard.common.assetguard_gid'):
        sys.modules['assetguard.rbac.orm'] = MagicMock()
        import assetguard.rbac.decorators

        del sys.modules['assetguard.rbac.orm']

        from assetguard.tests.util import RBAC_bypasser

        assetguard.rbac.decorators.expose_resources = RBAC_bypasser
        from assetguard import rootcheck

test_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
test_agent_path = os.path.join(test_data_path, 'agent')
callable_list = list()


# Retrieve used parameters in mocked method
def set_callable_list(*params, **kwargs):
    callable_list.append((params, kwargs))


test_result = [
    {'affected_items': ['001', '002'], 'total_affected_items': 2, 'failed_items': {}, 'total_failed_items': 0},
    {'affected_items': ['003', '008'], 'total_affected_items': 2, 'failed_items': {'001'}, 'total_failed_items': 1},
    {'affected_items': ['001'], 'total_affected_items': 1, 'failed_items': {'002', '003'},
     'total_failed_items': 2},
    # This result is used for exceptions
    {'affected_items': [], 'total_affected_items': 0, 'failed_items': {'001'}, 'total_failed_items': 1},
]


@pytest.mark.parametrize('agent_list, failed_items, status_list, expected_result', [
    (['002', '001'], [{'items': []}], ['active', 'active'], test_result[0]),
    (['003', '001', '008'], [{'items': [{'id': '001', 'status': ['disconnected']}]}],
     ['active', 'disconnected', 'active'], test_result[1]),
    (['001', '002', '003'], [{'items': [{'id': '002', 'status': ['disconnected']},
                                        {'id': '003', 'status': ['disconnected']}]}],
     ['active', 'disconnected', 'disconnected'], test_result[2]),
])
@patch('assetguard.core.common.CLIENT_KEYS', new=os.path.join(test_agent_path, 'client.keys'))
@patch('assetguard.rootcheck.AssetGuardDBQueryAgents.__exit__')
@patch('assetguard.rootcheck.AssetGuardDBQueryAgents.__init__', return_value=None)
@patch('assetguard.syscheck.AssetGuardQueue._connect')
@patch('assetguard.syscheck.AssetGuardQueue.send_msg_to_agent', side_effect=set_callable_list)
@patch('assetguard.syscheck.AssetGuardQueue.close')
def test_rootcheck_run(close_mock, send_mock, connect_mock, agent_init__mock, agent_exit__mock,
                       agent_list, failed_items, status_list, expected_result):
    """Test function `run` from rootcheck module.

    Parameters
    ----------
    agent_list : list
        List of agent IDs.
    failed_items : list
        List with the AssetGuardDBQueryAgents response.
    status_list : list
        List of agent statuses.
    expected_result : list
        List of dicts with expected results for every test.
    """
    with patch('assetguard.rootcheck.AssetGuardDBQueryAgents.run', return_value=failed_items[0]):
        result = rootcheck.run(agent_list=agent_list)
        for args, kwargs in callable_list:
            assert (isinstance(a, str) for a in args)
            assert (isinstance(k, str) for k in kwargs)
        assert isinstance(result, rootcheck.AffectedItemsAssetGuardResult)
        assert result.affected_items == expected_result['affected_items']
        assert result.total_affected_items == expected_result['total_affected_items']
        if result.failed_items:
            assert next(iter(result.failed_items.values())) == expected_result['failed_items']
        else:
            assert result.failed_items == expected_result['failed_items']
        assert result.total_failed_items == expected_result['total_failed_items']
