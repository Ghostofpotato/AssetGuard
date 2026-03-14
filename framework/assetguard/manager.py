# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

from os import remove
from os.path import exists

from assetguard import AssetGuard
from assetguard.core import common, configuration
from assetguard.core.cluster.cluster import get_node
from assetguard.core.cluster.utils import manager_restart, running_in_master_node
from assetguard.core.configuration import get_ossec_conf, write_ossec_conf
from assetguard.core.exception import AssetGuardError, AssetGuardInternalError
from assetguard.core.manager import status, get_api_conf, get_update_information_template, get_ossec_logs, \
    get_logs_summary, validate_ossec_conf, OSSEC_LOG_FIELDS
from assetguard.core.results import AffectedItemsAssetGuardResult, AssetGuardResult
from assetguard.core.utils import process_array, safe_move, validate_assetguard_xml, full_copy
from assetguard.rbac.decorators import expose_resources, mask_sensitive_config

node_id = get_node().get('node')


@expose_resources(actions=['cluster:read'], resources=[f'node:id:{node_id}'])
def get_status() -> AffectedItemsAssetGuardResult:
    """Wrapper for status().

    Returns
    -------
    AffectedItemsAssetGuardResult
        Affected items.
    """
    result = AffectedItemsAssetGuardResult(all_msg=f"Processes status was successfully read"
                                              f"{' in specified node' if node_id != 'manager' else ''}",
                                      some_msg='Could not read basic information in some nodes',
                                      none_msg=f"Could not read processes status"
                                               f"{' in specified node' if node_id != 'manager' else ''}"
                                      )

    result.affected_items.append(status())
    result.total_affected_items = len(result.affected_items)

    return result


@expose_resources(actions=['cluster:read'], resources=[f'node:id:{node_id}'])
def ossec_log(level: str = None, tag: str = None, offset: int = 0, limit: int = common.DATABASE_LIMIT,
              sort_by: dict = None, sort_ascending: bool = True, search_text: str = None,
              complementary_search: bool = False, search_in_fields: list = None,
              q: str = '', select: str = None, distinct: bool = False) -> AffectedItemsAssetGuardResult:
    """Get logs from assetguard-manager.log.

    Parameters
    ----------
    offset : int
        First element to return in the collection.
    limit : int
        Maximum number of elements to return.
    tag : str
        Filters by category/tag of log.
    level : str
        Filters by log level.
    sort_by : dict
        Fields to sort the items by. Format: {"fields":["field1","field2"],"order":"asc|desc"}
    sort_ascending : bool
        Sort in ascending (true) or descending (false) order.
    search_text : str
        Text to search.
    complementary_search : bool
        Find items without the text to search.
    search_in_fields : list
        Fields to search in.
    q : str
        Query to filter results by.
    select : str
        Select which fields to return (separated by comma).
    distinct : bool
        Look for distinct values.

    Returns
    -------
    AffectedItemsAssetGuardResult
        Affected items.
    """
    result = AffectedItemsAssetGuardResult(all_msg=f"Logs were successfully read"
                                              f"{' in specified node' if node_id != 'manager' else ''}",
                                      some_msg='Could not read logs in some nodes',
                                      none_msg=f"Could not read logs"
                                               f"{' in specified node' if node_id != 'manager' else ''}"
                                      )
    logs = get_ossec_logs()

    query = []
    level and query.append(f'level={level}')
    tag and query.append(f'tag={tag}')
    q and query.append(q)
    query = ';'.join(query)

    data = process_array(logs, search_text=search_text, search_in_fields=search_in_fields,
                         complementary_search=complementary_search, sort_by=sort_by,
                         sort_ascending=sort_ascending, offset=offset, limit=limit, q=query,
                         select=select, allowed_select_fields=OSSEC_LOG_FIELDS, distinct=distinct)
    result.affected_items.extend(data['items'])
    result.total_affected_items = data['totalItems']

    return result


@expose_resources(actions=['cluster:read'], resources=[f'node:id:{node_id}'])
def ossec_log_summary() -> AffectedItemsAssetGuardResult:
    """Summary of assetguard-manager.log.

    Returns
    -------
    AffectedItemsAssetGuardResult
        Affected items.
    """
    result = AffectedItemsAssetGuardResult(all_msg=f"Log was successfully summarized"
                                              f"{' in specified node' if node_id != 'manager' else ''}",
                                      some_msg='Could not summarize the log in some nodes',
                                      none_msg=f"Could not summarize the log"
                                               f"{' in specified node' if node_id != 'manager' else ''}"
                                      )

    logs_summary = get_logs_summary()

    for k, v in logs_summary.items():
        result.affected_items.append({k: v})
    result.affected_items = sorted(result.affected_items, key=lambda i: list(i.keys())[0])
    result.total_affected_items = len(result.affected_items)

    return result


_get_config_default_result_kwargs = {
    'all_msg': f"API configuration was successfully read{' in all specified nodes' if node_id != 'manager' else ''}",
    'some_msg': 'Not all API configurations could be read',
    'none_msg': f"Could not read API configuration{' in any node' if node_id != 'manager' else ''}",
    'sort_casting': ['str']
}


@expose_resources(actions=['cluster:read_api_config'],
                  resources=[f'node:id:{node_id}'],
                  post_proc_kwargs={'default_result_kwargs': _get_config_default_result_kwargs})
def get_api_config() -> AffectedItemsAssetGuardResult:
    """Return current API configuration.

    Returns
    -------
    AffectedItemsAssetGuardResult
        Current API configuration of the manager.
    """
    result = AffectedItemsAssetGuardResult(**_get_config_default_result_kwargs)

    try:
        api_config = {'node_name': node_id,
                      'node_api_config': get_api_conf()}
        result.affected_items.append(api_config)
    except AssetGuardError as e:
        result.add_failed_item(id_=node_id, error=e)
    result.total_affected_items = len(result.affected_items)

    return result


_restart_default_result_kwargs = {
    'all_msg': f"Restart request sent to {'all specified nodes' if node_id != 'manager' else ''}",
    'some_msg': "Could not send restart request to some specified nodes",
    'none_msg': "Could not send restart request to any node",
    'sort_casting': ['str']
}


@expose_resources(actions=['cluster:read'], resources=[f'node:id:{node_id}'])
@expose_resources(actions=['cluster:restart'], resources=[f'node:id:{node_id}'],
                  post_proc_kwargs={'default_result_kwargs': _restart_default_result_kwargs})
def restart() -> AffectedItemsAssetGuardResult:
    """Wrapper for 'restart_manager' function due to interdependence with cluster module and permission access.

    Returns
    -------
    AffectedItemsAssetGuardResult
        Affected items.
    """
    result = AffectedItemsAssetGuardResult(**_restart_default_result_kwargs)
    try:
        manager_restart()
        result.affected_items.append(node_id)
    except AssetGuardError as e:
        result.add_failed_item(id_=node_id, error=e)
    result.total_affected_items = len(result.affected_items)

    return result


_validation_default_result_kwargs = {
    'all_msg': f"Validation was successfully checked{' in all nodes' if node_id != 'manager' else ''}",
    'some_msg': 'Could not check validation in some nodes',
    'none_msg': f"Could not check validation{' in any node' if node_id != 'manager' else ''}",
    'sort_fields': ['name'],
    'sort_casting': ['str'],
}


@expose_resources(actions=['cluster:read'],
                  resources=[f'node:id:{node_id}'],
                  post_proc_kwargs={'default_result_kwargs': _validation_default_result_kwargs})
def validation() -> AffectedItemsAssetGuardResult:
    """Check if AssetGuard configuration is OK.

    Returns
    -------
    AffectedItemsAssetGuardResult
        Affected items.
    """
    result = AffectedItemsAssetGuardResult(**_validation_default_result_kwargs)

    try:
        response = validate_ossec_conf()
        result.affected_items.append({'name': node_id, **response})
        result.total_affected_items += 1
    except AssetGuardError as e:
        result.add_failed_item(id_=node_id, error=e)

    return result


@expose_resources(actions=['cluster:read'], resources=[f'node:id:{node_id}'])
@mask_sensitive_config()
def get_config(component: str = None, config: str = None) -> AffectedItemsAssetGuardResult:
    """Wrapper for get_active_configuration.

    Parameters
    ----------
    component : str
        Selected component.
    config : str
        Configuration to get, written on disk.


    Returns
    -------
    AffectedItemsAssetGuardResult
        Affected items.
    """
    result = AffectedItemsAssetGuardResult(all_msg=f"Active configuration was successfully read"
                                              f"{' in specified node' if node_id != 'manager' else ''}",
                                      some_msg='Could not read active configuration in some nodes',
                                      none_msg=f"Could not read active configuration"
                                               f"{' in specified node' if node_id != 'manager' else ''}"
                                      )

    try:
        data = configuration.get_active_configuration(component=component, configuration=config)
        len(data.keys()) > 0 and result.affected_items.append(data)
    except AssetGuardError as e:
        result.add_failed_item(id_=node_id, error=e)
    result.total_affected_items = len(result.affected_items)

    return result


@expose_resources(actions=['cluster:read'], resources=[f'node:id:{node_id}'])
@mask_sensitive_config()
def read_ossec_conf(section: str = None, field: str = None, raw: bool = False,
                    distinct: bool = False) -> AffectedItemsAssetGuardResult:
    """Wrapper for get_ossec_conf.

    Parameters
    ----------
    section : str
        Filters by section
    field : str
        Filters by field in section (i.e. included).
    raw : bool
        Whether to return the file content in raw or JSON format.
    distinct : bool
        Look for distinct values.

    Returns
    -------
    AffectedItemsAssetGuardResult
        Affected items.
    """
    result = AffectedItemsAssetGuardResult(all_msg=f"Configuration was successfully read"
                                              f"{' in specified node' if node_id != 'manager' else ''}",
                                      some_msg='Could not read configuration in some nodes',
                                      none_msg=f"Could not read configuration"
                                               f"{' in specified node' if node_id != 'manager' else ''}"
                                      )

    try:
        if raw:
            with open(common.OSSEC_CONF) as f:
                return f.read()
        result.affected_items.append(get_ossec_conf(section=section, field=field, distinct=distinct))
    except AssetGuardError as e:
        result.add_failed_item(id_=node_id, error=e)
    result.total_affected_items = len(result.affected_items)

    return result


@expose_resources(actions=['cluster:read'], resources=[f'node:id:{node_id}'])
def get_basic_info() -> AffectedItemsAssetGuardResult:
    """Wrapper for AssetGuard().to_dict

    Returns
    -------
    AffectedItemsAssetGuardResult
        Affected items.
    """
    result = AffectedItemsAssetGuardResult(all_msg=f"Basic information was successfully read"
                                              f"{' in specified node' if node_id != 'manager' else ''}",
                                      some_msg='Could not read basic information in some nodes',
                                      none_msg=f"Could not read basic information"
                                               f"{' in specified node' if node_id != 'manager' else ''}"
                                      )

    try:
        result.affected_items.append(AssetGuard().to_dict())
        if running_in_master_node():
            result.affected_items[0]['uuid'] = common.get_installation_uid()
        else:
            result.affected_items[0]['uuid'] = None
    except AssetGuardError as e:
        result.add_failed_item(id_=node_id, error=e)
    result.total_affected_items = len(result.affected_items)

    return result


@expose_resources(actions=['cluster:update_config'], resources=[f'node:id:{node_id}'])
def update_ossec_conf(new_conf: str = None) -> AffectedItemsAssetGuardResult:
    """Replace assetguard configuration (assetguard-manager.conf) with the provided configuration.

    Parameters
    ----------
    new_conf: str
        The new configuration to be applied.

    Returns
    -------
    AffectedItemsAssetGuardResult
        Affected items.
    """
    result = AffectedItemsAssetGuardResult(all_msg=f"Configuration was successfully updated"
                                              f"{' in specified node' if node_id != 'manager' else ''}",
                                      some_msg='Could not update configuration in some nodes',
                                      none_msg=f"Could not update configuration"
                                               f"{' in specified node' if node_id != 'manager' else ''}"
                                      )
    backup_file = f'{common.OSSEC_CONF}.backup'
    try:
        # Check a configuration has been provided
        if not new_conf:
            raise AssetGuardError(1125)

        # Check if the configuration is valid
        validate_assetguard_xml(new_conf)

        # Create a backup of the current configuration before attempting to replace it
        try:
            full_copy(common.OSSEC_CONF, backup_file)
        except IOError:
            raise AssetGuardError(1019)

        # Write the new configuration and validate it
        write_ossec_conf(new_conf)
        is_valid = validate_ossec_conf()

        if not isinstance(is_valid, dict) or ('status' in is_valid and is_valid['status'] != 'OK'):
            raise AssetGuardError(1125)
        else:
            result.affected_items.append(node_id)
        exists(backup_file) and remove(backup_file)
    except AssetGuardError as e:
        result.add_failed_item(id_=node_id, error=e)
    finally:
        exists(backup_file) and safe_move(backup_file, common.OSSEC_CONF)

    result.total_affected_items = len(result.affected_items)
    return result


def get_update_information(installation_uid: str, update_information: dict) -> AssetGuardResult:
    """Process update information into a assetguard result.

    Parameters
    ----------
    installation_uid : str
        AssetGuard UID to include in the result.
    update_information : dict
        Data to process.

    Returns
    -------
    AssetGuardResult
        Result with update information.
    """

    if not update_information:
        # Return a response with minimal data because the update_check is disabled
        return AssetGuardResult({'data': get_update_information_template(uuid=installation_uid, update_check=False)})
    status_code = update_information.pop('status_code')
    uuid = update_information.get('uuid')
    tag = update_information.get('current_version')

    if status_code != 200:
        extra_message = f"{uuid}, {tag}" if status_code == 401 else update_information['message']
        raise AssetGuardInternalError(2100, extra_message=extra_message)

    update_information.pop('message', None)

    return AssetGuardResult({'data': update_information})
