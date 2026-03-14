#!/bin/env bash
# Script to remove AssetGuard manager and agent from the system

if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root or with sudo."
    exit 1
fi

# Check if apt-get is available
if command -v apt-get >/dev/null 2>&1; then
    apt-get remove --purge -y assetguard-manager assetguard-agent || true
else
    echo "Apt package manager not found. Skipping removal of AssetGuard packages."
fi

# If using yum, remove AssetGuard manager and agent
if command -v yum >/dev/null 2>&1; then
    yum remove -y assetguard-manager assetguard-agent || true
else
    echo "Yum package manager not found. Skipping removal of AssetGuard packages."
fi

# Check if ASSETGUARD_HOME is set
if [ -z "$ASSETGUARD_HOME" ]; then
    ASSETGUARD_HOME="/var/assetguard-manager"
fi

if [ ! -d "$ASSETGUARD_HOME" ]; then
    echo "AssetGuard home directory $ASSETGUARD_HOME does not exist."
    exit 1
fi

# Umount proc filesystem if it exists (Mounted for development purposes)
if mountpoint -q ${ASSETGUARD_HOME/proc}; then
    umount /var/assetguard-manager/proc
fi


# Stop and remove AssetGuard services
if [ -f /etc/init.d/assetguard-manager ]; then
    service assetguard-manager stop
    update-rc.d -f assetguard-manager remove
    rm -f /etc/init.d/assetguard-manager
fi

if [ -f /etc/init.d/assetguard-agent ]; then
    service assetguard-agent stop
    update-rc.d -f assetguard-agent remove
    rm -f /etc/init.d/assetguard-agent
fi

# Stop and remove AssetGuard systemd services
if [ -f /etc/systemd/system/assetguard-manager.service ]; then
    systemctl stop assetguard-manager
    systemctl disable assetguard-manager
    rm -f /etc/systemd/system/assetguard-manager.service
fi

if [ -f /etc/systemd/system/assetguard-agent.service ]; then
    systemctl stop assetguard-agent
    systemctl disable assetguard-agent
    rm -f /etc/systemd/system/assetguard-agent.service
fi

# Just in case, stop AssetGuard control script
$ASSETGUARD_HOME/bin/assetguard-manager-control stop

# Remove AssetGuard directories and files
rm -rf $ASSETGUARD_HOME
find /etc/systemd/system -name "assetguard*" | xargs rm -f
systemctl daemon-reload

# Remove AssetGuard user and group
if id -u assetguard >/dev/null 2>&1; then
    userdel -r assetguard
else
    echo "User 'assetguard' does not exist."
fi
if getent group assetguard >/dev/null 2>&1; then
    groupdel assetguard
else
    echo "Group 'assetguard' does not exist."
fi

# Remove AssetGuard user and group
if id -u assetguard-manager >/dev/null 2>&1; then
    userdel -r assetguard-manager
else
    echo "User 'assetguard-manager' does not exist."
fi
if getent group assetguard-manager >/dev/null 2>&1; then
    groupdel assetguard-manager
else
    echo "Group 'assetguard-manager' does not exist."
fi
