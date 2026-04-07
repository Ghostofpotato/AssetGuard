#!/usr/bin/env bash

set -e

ASSETGUARD_CERTS_DIR="/var/assetguard-manager/etc/certs"
ROLE="$3"
NODE_CERT="${ASSETGUARD_CERTS_DIR}/${NODE_NAME}.pem"
NODE_CERT_KEY="${ASSETGUARD_CERTS_DIR}/${NODE_NAME}-key.pem"
SERVER_CERT="${ASSETGUARD_CERTS_DIR}/manager.pem"
SERVER_CERT_KEY="${ASSETGUARD_CERTS_DIR}/manager-key.pem"

echo "Waiting for certificates..."
while [ ! -f "${ASSETGUARD_CERTS_DIR}/root-ca.pem" ]; do
  sleep 2
done
echo "Certificates found."

# Set indexer credentials (default: admin/admin)
echo 'admin' | /var/assetguard-manager/bin/assetguard-manager-keystore -f indexer -k username
echo 'admin' | /var/assetguard-manager/bin/assetguard-manager-keystore -f indexer -k password

# Configure assetguard configuration file and api.yaml based on the Master role
if [ "$ROLE" == "master" ]; then
    python3 /scripts/xml_parser.py /var/assetguard-manager/etc/assetguard-manager.conf /scripts/master_assetguard-manager_conf.xml
    sed -i "s:# access:access:g" /var/assetguard-manager/api/configuration/api.yaml
    sed -i "s:#  max_request_per_minute\: 300:  max_request_per_minute\: 99999:g" /var/assetguard-manager/api/configuration/api.yaml
else
    python3 /scripts/xml_parser.py /var/assetguard-manager/etc/assetguard-manager.conf /scripts/worker_assetguard-manager_conf.xml
fi

sed -i "s:assetguard_db.debug=0:assetguard_db.debug=2:g" /var/assetguard-manager/etc/internal_options.conf
sed -i "s:authd.debug=0:authd.debug=2:g" /var/assetguard-manager/etc/internal_options.conf
sed -i "s:remoted.debug=0:remoted.debug=2:g" /var/assetguard-manager/etc/internal_options.conf

# Set proper permissions
chmod 500 /var/assetguard-manager/etc/certs
chmod 400 /var/assetguard-manager/etc/certs/*
chown -R assetguard-manager:assetguard-manager /var/assetguard-manager/etc/certs

echo "Starting AssetGuard..."
/var/assetguard-manager/bin/assetguard-manager-control start

# Keep the container running
while true; do
    sleep 10
done
