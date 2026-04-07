#!/bin/bash
set -euo pipefail

# Save current directory
OLD_DIR=$(pwd)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
DEST_DIR="/var/assetguard-manager/etc/certs"
ORIG_DIR="${SCRIPT_DIR}/certs"
ASSETGUARD_USER="assetguard-manager"
ASSETGUARD_GROUP="assetguard-manager"

# Check if user/group exists
if ! id -u "${ASSETGUARD_USER}" >/dev/null 2>&1; then
    echo "User ${ASSETGUARD_USER} does not exist. Exiting."
    exit 1
fi

if ! getent group "${ASSETGUARD_GROUP}" >/dev/null 2>&1; then
    echo "Group ${ASSETGUARD_GROUP} does not exist. Exiting."
    exit 1
fi

# Move to the script directory
cd "${SCRIPT_DIR}"
# Trap to return to the original directory
trap 'cd "$OLD_DIR"' EXIT

# Create destination directory if it doesn't exist
if [ ! -d "${DEST_DIR}" ]; then
    mkdir -p "${DEST_DIR}"
    chown ${ASSETGUARD_USER}:${ASSETGUARD_GROUP} "${DEST_DIR}"
    chmod 750 "${DEST_DIR}"
fi

echo "Copying certificates to ${DEST_DIR}..."

# Copy certificates
# Array of certificate files to copy
CERT_ORG_FILES=("assetguard-1-key.pem" "assetguard-1.pem" "root-ca.pem")
CERT_DST_FILES=("manager-key.pem" "manager.pem" "root-ca.pem")

for i in "${!CERT_ORG_FILES[@]}"; do
    cp "${ORIG_DIR}/${CERT_ORG_FILES[$i]}" "${DEST_DIR}/${CERT_DST_FILES[$i]}"
    chown ${ASSETGUARD_USER}:${ASSETGUARD_GROUP} ${DEST_DIR}/${CERT_DST_FILES[$i]}
    chmod 640 ${DEST_DIR}/${CERT_DST_FILES[$i]}
    echo "Copied and set permissions for ${CERT_DST_FILES[$i]}"
done

echo "Done copying certificates."
