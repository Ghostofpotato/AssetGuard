#!/bin/bash
set -e

# Set correct ownership and permissions for certificates in /etc/assetguard-dashboard/certs/
echo "Setting up certificate permissions..."
mkdir -p /etc/assetguard-dashboard/certs
cp /certs/root-ca.pem /etc/assetguard-dashboard/certs/root-ca.pem
cp /certs/dashboard.pem /etc/assetguard-dashboard/certs/dashboard.pem
cp /certs/dashboard-key.pem /etc/assetguard-dashboard/certs/dashboard-key.pem
chown -R assetguard-dashboard:assetguard-dashboard /etc/assetguard-dashboard/certs
chmod 640 /etc/assetguard-dashboard/certs/*
chmod 750 /etc/assetguard-dashboard/certs/

# Start assetguard-dashboard service
# sudo -u assetguard-dashboard /usr/share/assetguard-dashboard/bin/opensearch-dashboards -c /etc/assetguard-dashboard/opensearch_dashboards.yml
echo "Starting assetguard-dashboard..."

sudo -u assetguard-dashboard /usr/share/assetguard-dashboard/bin/opensearch-dashboards -c /etc/assetguard-dashboard/opensearch_dashboards.yml
