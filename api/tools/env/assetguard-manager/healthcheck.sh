#!/bin/bash

[ "$(/var/assetguard-manager/bin/assetguard-manager-control status | grep -E 'clusterd is running|apid is running' | wc -l)" == 2 ] || exit 1
exit 0
