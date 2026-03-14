#!/bin/bash
set -e

# Wait for certificates to be mounted
echo "Checking for certificates..."

# Set correct ownership and permissions for certificates in /etc/assetguard-indexer/certs/
if [ -d "/etc/assetguard-indexer/certs" ]; then
    echo "Setting up certificate permissions..."
    cp /certs/node-1-key.pem /etc/assetguard-indexer/certs/indexer-key.pem
    cp /certs/node-1.pem /etc/assetguard-indexer/certs/indexer.pem
    cp /certs/root-ca.pem /etc/assetguard-indexer/certs/root-ca.pem
    cp /certs/admin.pem /etc/assetguard-indexer/certs/admin.pem
    cp /certs/admin-key.pem /etc/assetguard-indexer/certs/admin-key.pem
    chown -R assetguard-indexer:assetguard-indexer /etc/assetguard-indexer/certs/
    chmod 640 /etc/assetguard-indexer/certs/*
fi

# Start assetguard-indexer service
echo "Starting assetguard-indexer..."
service assetguard-indexer start

# Wait for service to be ready
echo "Waiting for assetguard-indexer to be ready..."
sleep 3

# Check if server is up 'service assetguard-indexer status'
service assetguard-indexer status

if [ $? -ne 0 ]; then
    echo "AssetGuard-indexer service failed to start."
    service assetguard-indexer restart
    sleep 3
    service assetguard-indexer status
    if [ $? -ne 0 ]; then
        echo "AssetGuard-indexer service failed to start after restart. Exiting."
        exit 1
    fi
fi


# Initialize security only if not already done
INIT_FLAG="/etc/assetguard-indexer-init/.security_initialized"
if [ ! -f "$INIT_FLAG" ]; then
    echo "Initializing indexer security for the first time..."
    sleep 20
    /usr/share/assetguard-indexer/bin/indexer-security-init.sh

    # Create flag to indicate security has been initialized
    mkdir -p /etc/assetguard-indexer-init
    touch "$INIT_FLAG"
    echo "Security initialization completed and flag created."
else
    echo "Security already initialized, skipping initialization."
fi




echo "AssetGuard-indexer is ready!"


# Keep container running - if CMD was provided, execute it, otherwise keep alive
if [ "$#" -gt 0 ] && [ "$1" != "/bin/bash" ]; then
    exec "$@"
else
    tail -f /dev/null
fi
