#!/bin/bash

CERT_ORG="/workspaces/assetguard-5.x/scripts_public/certs"

# Check if assetguard-dashboard user exists
if ! id -u assetguard-dashboard >/dev/null 2>&1; then
    echo "User 'assetguard-dashboard' does not exist. Please install assetguard-dashboard before running this script."
    exit 1
fi

# Copy certificates to assetguard-dashboard certs folder

mkdir /etc/assetguard-dashboard/certs/                                                                                                                         2 ↵
cp ${CERT_ORG}/dashboard-key.pem /etc/assetguard-dashboard/certs/
cp ${CERT_ORG}/dashboard.pem /etc/assetguard-dashboard/certs/
cp ${CERT_ORG}/root-ca.pem /etc/assetguard-dashboard/certs/
chmod 750  /etc/assetguard-dashboard/certs/
chmod 640  /etc/assetguard-dashboard/certs/*
chown -R assetguard-dashboard:assetguard-dashboard  /etc/assetguard-dashboard/certs


# /usr/share/assetguard-dashboard/bin/opensearch-dashboards -c /etc/assetguard-dashboard/opensearch_dashboards.yml --allow-root
cp -a /etc/assetguard-dashboard/opensearch_dashboards.yml /etc/assetguard-dashboard/opensearch_dashboards_custom.yml

# Replace localhost with 127.0.0.1
sed -i 's/localhost/127.0.0.1/g' /etc/assetguard-dashboard/opensearch_dashboards_custom.yml

# Restart assetguard-dashboard service
echo "Run: "
echo 'sudo -u assetguard-dashboard /usr/share/assetguard-dashboard/bin/opensearch-dashboards -c /etc/assetguard-dashboard/custom_opensearch_dashboards.yml'
