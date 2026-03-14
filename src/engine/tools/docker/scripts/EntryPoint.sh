#!/usr/bin/env bash

/usr/sbin/sshd
ASSETGUARD_CONFIG_SKIP_API=true /usr/share/assetguard-server/bin/assetguard-engine
