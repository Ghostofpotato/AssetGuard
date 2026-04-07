FROM ubuntu:24.04

# Update and install dependencies
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG=en_US.utf8

# Copy all files to a temporary location for installation
WORKDIR /tmp/assetguard-install
COPY . .

# Install assetguard-indexer
RUN apt install -y /tmp/assetguard-install/assetguard-indexer_5.0.0-latest_amd64.deb

# Configure knn memory circuit breaker limit
RUN echo "knn.memory.circuit_breaker.limit: 4096mb" >> /etc/assetguard-indexer/opensearch.yml

# Add Java security policy permissions for cgroup access
RUN cat <<'EOF' >> /etc/assetguard-indexer/jvm.options
-Djava.security.policy=all.policy
-Dpermission.java.io.FilePermission=/sys/fs/cgroup/-,read
EOF

# Create certs directory (will be populated by volume mount at runtime)
RUN mkdir -p /etc/assetguard-indexer/certs/

# Clean up installation files
RUN rm -rf /tmp/assetguard-install

# Set working directory
WORKDIR /root

# Wait for interactive debugging
#CMD [ "sleep", "infinity" ]
