# Copyright (C) 2015-2024, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

from assetguard_testing.constants.paths.logs import ASSETGUARD_LOG_PATH
from assetguard_testing.modules.agentd.patterns import *
from assetguard_testing.tools.monitors.file_monitor import FileMonitor
from assetguard_testing.utils import callbacks


def wait_keepalive():
    """
        Watch assetguard.log until "Sending keep alive" message is found
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_SENDING_KEEP_ALIVE), timeout = 100)
    assert (assetguard_log_monitor.callback_result != None), f'Sending keep alive not found'


def wait_connect():
    """
        Watch assetguard.log until received "Connected to the server" message is found
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_CONNECTED_TO_SERVER), timeout = 150)
    assert (assetguard_log_monitor.callback_result != None), f'Connected to the server message not found'


def wait_ack():
    """
        Watch assetguard.log until "Received ack message" is found
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_RECEIVED_ACK))
    assert (assetguard_log_monitor.callback_result != None), f'Received ack message not found'


def wait_state_update():
    """
        Watch assetguard.log until "Updating state file" message is found
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_UPDATING_STATE_FILE))
    assert (assetguard_log_monitor.callback_result != None), f'State file update not found'


def wait_enrollment():
    """
        Watch assetguard.log until "Valid key received" message is found
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_RECEIVED_VALID_KEY), timeout = 150)
    assert (assetguard_log_monitor.callback_result != None), 'Agent never enrolled'


def wait_enrollment_try():
    """
        Watch assetguard.log until "Requesting a key" message is found
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_REQUESTING_KEY,{'IP':''}), timeout = 150)
    assert (assetguard_log_monitor.callback_result != None), f'Enrollment retry was not sent'


def wait_agent_notification(current_value):
    """
        Watch assetguard.log until "Sending agent notification" message is found current_value times
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_SENDING_AGENT_NOTIFICATION), accumulations = int(current_value))
    assert (assetguard_log_monitor.callback_result != None), f'Sending agent notification message not found'


def wait_server_rollback():
    """
        Watch assetguard.log until "Unable to connect to any server" message is found'
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(callback=callbacks.generate_callback(AGENTD_UNABLE_TO_CONNECT_TO_ANY), timeout = 120)
    assert (assetguard_log_monitor.callback_result != None), f'Unable to connect to any server message not found'


def check_module_stop():
    """
        Watch assetguard.log until "Unable to access queue" message is not found
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    assetguard_log_monitor.start(callback=callbacks.generate_callback(AGENTD_MODULE_STOPPED))
    assert (assetguard_log_monitor.callback_result == None), f'Unable to access queue message found'


def check_connection_try():
    """
        Watch assetguard.log until "Trying to connect to server" message is found
    """
    assetguard_log_monitor = FileMonitor(ASSETGUARD_LOG_PATH)
    matched_line = assetguard_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_TRYING_CONNECT,{'IP':'','PORT':''}), return_matched_line = True)
    assert (assetguard_log_monitor.callback_result != None), f'Trying to connect to server message not found'
    return matched_line
