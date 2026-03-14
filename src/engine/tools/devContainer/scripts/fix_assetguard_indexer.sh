#!/bin/bash
CERT_ORG_DIR="/workspaces/assetguard-5.x/scripts_public/certs"

# Check if assetguard-indexer user exists
if ! id -u assetguard-indexer >/dev/null 2>&1; then
    echo "User 'assetguard-indexer' does not exist. Please install assetguard-indexer before running this script."
    exit 1
fi

cp ${CERT_ORG_DIR}/node-1-key.pem /etc/assetguard-indexer/certs/indexer-key.pem
cp ${CERT_ORG_DIR}/node-1.pem /etc/assetguard-indexer/certs/indexer.pem
cp ${CERT_ORG_DIR}/root-ca.pem /etc/assetguard-indexer/certs
cp ${CERT_ORG_DIR}/admin.pem /etc/assetguard-indexer/certs
cp ${CERT_ORG_DIR}/admin-key.pem /etc/assetguard-indexer/certs
chown assetguard-indexer:assetguard-indexer /etc/assetguard-indexer/certs/*
chmod 640 /etc/assetguard-indexer/certs/*

# Create or modify the opensearch configuration to set an explicit memory value instead of percentage
echo "knn.memory.circuit_breaker.limit: 4096mb" >> /etc/assetguard-indexer/opensearch.yml
# Add Java security policy permissions for cgroup access
cat >> /etc/assetguard-indexer/jvm.options << 'EOF'

-Djava.security.policy=all.policy

-Dpermission.java.io.FilePermission=/sys/fs/cgroup/-,read

EOF
# Restart the assetguard-indexer service
service assetguard-indexer restart
sleep 10
/usr/share/assetguard-indexer/bin/indexer-security-init.sh

exit 0


# <indexer>
#   <hosts>
#     <host>https://127.0.0.1:9200</host>
#   </hosts>
#   <ssl>
#     <certificate_authorities>
#       <ca>/workspaces/assetguard-5.x/assetguard/src/engine/tools/devContainer/e2e/certs/root-ca.pem</ca>
#     </certificate_authorities>
#     <certificate>/workspaces/assetguard-5.x/assetguard/src/engine/tools/devContainer/e2e/certs/admin.pem</certificate>
#     <key>/workspaces/assetguard-5.x/assetguard/src/engine/tools/devContainer/e2e/certs/admin-key.pem</key>
#   </ssl>
# </indexer>
