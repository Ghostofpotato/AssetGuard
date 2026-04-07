# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

import os
import sys
from unittest.mock import MagicMock, patch
from assetguard.core.exception import AssetGuardError


import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))

with patch('assetguard.core.common.assetguard_uid'):
    with patch('assetguard.core.common.assetguard_gid'):
        sys.modules['assetguard.rbac.orm'] = MagicMock()
        import assetguard.rbac.decorators
        from assetguard.tests.util import RBAC_bypasser

        del sys.modules['assetguard.rbac.orm']
        assetguard.rbac.decorators.expose_resources = RBAC_bypasser

        from assetguard.event import MSG_HEADER, send_event_to_analysisd


@pytest.mark.parametrize('events,side_effects,message', [
    (['{"foo": 1}'], (None,), 'All events were forwarded to analisysd'),
    (['{"foo": 1}', '{"bar": 2}'], (None, None), 'All events were forwarded to analisysd'),
    (['{"foo": 1}', '{"bar": 2}'], (AssetGuardError(1014), None), 'Some events were forwarded to analisysd'),
    (['{"foo": 1}', '{"bar": 2}'], (AssetGuardError(1014), AssetGuardError(1014)), 'No events were forwarded to analisysd'),
])
@patch('assetguard.event.AssetGuardAnalysisdQueue.send_msg')
@patch('socket.socket.connect')
def test_send_event_to_analysisd(socket_mock, send_msg_mock, events, side_effects, message):
    send_msg_mock.side_effect = side_effects
    ret_val = send_event_to_analysisd(events=events)

    assert send_msg_mock.call_count == len(events)
    for i, event in enumerate(events):
        assert send_msg_mock.call_args_list[i].kwargs['msg_header'] == MSG_HEADER
        assert send_msg_mock.call_args_list[i].kwargs['msg'] == event

    assert ret_val.affected_items == [events[i] for i, v in enumerate(side_effects) if v is None]
    assert ret_val.message == message
