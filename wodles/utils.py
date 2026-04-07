# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import os
import subprocess
from functools import lru_cache
from sys import exit


@lru_cache(maxsize=None)
def find_assetguard_path() -> str:
    """
    Get the AssetGuard installation path.

    Returns
    -------
    str
        Path where AssetGuard is installed or empty string if there is no framework in the environment.
    """
    abs_path = os.path.abspath(os.path.dirname(__file__))
    allparts = []
    while 1:
        parts = os.path.split(abs_path)
        if parts[0] == abs_path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == abs_path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            abs_path = parts[0]
            allparts.insert(0, parts[1])

    assetguard_path = ''
    try:
        for i in range(0, allparts.index('wodles')):
            assetguard_path = os.path.join(assetguard_path, allparts[i])
    except ValueError:
        pass

    return assetguard_path


def call_assetguard_control(option: str) -> str:
    """
    Execute the assetguard-control script with the parameters specified.

    Parameters
    ----------
    option : str
        The option that will be passed to the script.

    Returns
    -------
    str
        The output of the call to assetguard-control.
    """
    assetguard_control = os.path.join(find_assetguard_path(), "bin", "assetguard-control")
    try:
        proc = subprocess.Popen([assetguard_control, option], stdout=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        return stdout.decode()
    except (OSError, ChildProcessError):
        print(f'ERROR: a problem occurred while executing {assetguard_control}')
        exit(1)


def get_assetguard_info(field: str) -> str:
    """
    Execute the assetguard-control script with the 'info' argument, filtering by field if specified.

    Parameters
    ----------
    field : str
        The field of the output that's being requested. Its value can be 'ASSETGUARD_VERSION', 'ASSETGUARD_REVISION' or
        'ASSETGUARD_TYPE'.

    Returns
    -------
    str
        The output of the assetguard-control script.
    """
    assetguard_info = call_assetguard_control("info")
    if not assetguard_info:
        return "ERROR"

    if not field:
        return assetguard_info

    env_variables = assetguard_info.rsplit("\n")
    env_variables.remove("")
    assetguard_env_vars = dict()
    for env_variable in env_variables:
        key, value = env_variable.split("=")
        assetguard_env_vars[key] = value.replace("\"", "")

    return assetguard_env_vars[field]


@lru_cache(maxsize=None)
def get_assetguard_version() -> str:
    """
    Return the version of AssetGuard installed.

    Returns
    -------
    str
        The version of AssetGuard installed.
    """
    return get_assetguard_info("ASSETGUARD_VERSION")


@lru_cache(maxsize=None)
def get_assetguard_revision() -> str:
    """
    Return the revision of the AssetGuard instance installed.

    Returns
    -------
    str
        The revision of the AssetGuard instance installed.
    """
    return get_assetguard_info("ASSETGUARD_REVISION")


@lru_cache(maxsize=None)
def get_assetguard_type() -> str:
    """
    Return the type of AssetGuard instance installed.

    Returns
    -------
    str
        The type of AssetGuard instance installed.
    """
    return get_assetguard_info("ASSETGUARD_TYPE")


ANALYSISD = os.path.join(find_assetguard_path(), 'queue', 'sockets', 'queue')
# Max size of the event that ANALYSISID can handle
MAX_EVENT_SIZE = 65535
