#!/usr/bin/env bash

mkdir -p /var/assetguard-manager/stats/totals/2019/Aug/
cp -rf /tmp_volume/configuration_files/ossec-totals-27.log /var/assetguard-manager/stats/totals/2019/Aug/ossec-totals-27.log
chown -R assetguard-manager:assetguard-manager /var/assetguard-manager/stats/totals/2019/Aug/ossec-totals-27.log
