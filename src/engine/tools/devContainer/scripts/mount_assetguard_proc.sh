#!/bin/env bash

# Check if ASSETGUARD_HOME is set
if [ -z "$ASSETGUARD_HOME" ]; then
    ASSETGUARD_HOME="/var/assetguard-manager"
fi

if [ ! -d "$ASSETGUARD_HOME" ]; then
    echo "AssetGuard home directory $ASSETGUARD_HOME does not exist."
    exit 1
fi

# Mount proc filesystem if it does not exist (Mounted for development purposes)
if ! mountpoint -q ${ASSETGUARD_HOME}/proc; then
    mkdir -p ${ASSETGUARD_HOME}/proc
    mount -t proc proc ${ASSETGUARD_HOME}/proc
    if [ $? -ne 0 ]; then
        echo "Failed to mount proc filesystem at ${ASSETGUARD_HOME}/proc"
        exit 1
    fi
    echo "Mounted proc filesystem at ${ASSETGUARD_HOME}/proc"
else
    echo "Proc filesystem is already mounted at ${ASSETGUARD_HOME}/proc"
fi
