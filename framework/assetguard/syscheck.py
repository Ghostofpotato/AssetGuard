# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

from typing import Union

from assetguard.core import common
from assetguard.core.agent import get_agents_info, get_rbac_filters, AssetGuardDBQueryAgents
from assetguard.core.exception import AssetGuardError, AssetGuardResourceNotFound
from assetguard.core.results import AffectedItemsAssetGuardResult
from assetguard.core.assetguard_queue import AssetGuardQueue
from assetguard.rbac.decorators import expose_resources


@expose_resources(actions=["syscheck:run"], resources=["agent:id:{agent_list}"],
                  post_proc_kwargs={'exclude_codes': [1701, 1707]})
def run(agent_list: Union[str, None] = None) -> AffectedItemsAssetGuardResult:
    """Run a syscheck scan in the specified agents.

    Parameters
    ----------
    agent_list : str or None
        List of the agents IDs to run the scan for.

    Returns
    -------
    AffectedItemsAssetGuardResult
        Confirmation/Error message.
    """
    result = AffectedItemsAssetGuardResult(all_msg='Syscheck scan was restarted on returned agents',
                                      some_msg='Syscheck scan was not restarted on some agents',
                                      none_msg='No syscheck scan was restarted')

    system_agents = get_agents_info()
    rbac_filters = get_rbac_filters(system_resources=system_agents, permitted_resources=agent_list)
    agent_list = set(agent_list)
    not_found_agents = agent_list - system_agents

    # Add non existent agents to failed_items
    [result.add_failed_item(id_=agent, error=AssetGuardResourceNotFound(1701)) for agent in not_found_agents]

    # Add non eligible agents to failed_items
    with AssetGuardDBQueryAgents(limit=None, select=["id", "status"], query='status!=active', **rbac_filters) as db_query:
        non_eligible_agents = db_query.run()['items']

    [result.add_failed_item(
        id_=agent['id'],
        error=AssetGuardError(1707)) for agent in non_eligible_agents]

    with AssetGuardQueue(common.AR_SOCKET) as wq:
        eligible_agents = agent_list - not_found_agents - {d['id'] for d in non_eligible_agents}
        for agent_id in eligible_agents:
            try:
                wq.send_msg_to_agent(AssetGuardQueue.HC_SK_RESTART, agent_id)
                result.affected_items.append(agent_id)
            except AssetGuardError as e:
                result.add_failed_item(id_=agent_id, error=e)

    result.affected_items = sorted(result.affected_items, key=int)
    result.total_affected_items = len(result.affected_items)

    return result
