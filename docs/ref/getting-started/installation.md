# Installation

This guide provides instructions for installing AssetGuard server and agent components. Before proceeding, verify that your system meets the requirements listed in the [Packages](packages.md) page.

## Server

This section covers single-node and multi-node server installation.

### Installation

Install the AssetGuard manager package for your platform:

**Debian-based platforms:**

```bash
sudo dpkg -i assetguard-manager_*.deb
```

**Red Hat-based platforms:**

```bash
sudo rpm -ivh assetguard-manager-*.rpm
```

### Configuration

#### Deploy certificates

Deploy the SSL certificates for secure communication between the AssetGuard server and indexer. These certificates should be extracted from the `assetguard-certificates.tar` file generated during the certificate creation process.

```bash
NODE_NAME=node-1

# Create certificates directory
sudo mkdir -p /var/assetguard-manager/etc/certs

# Extract and deploy certificates
sudo tar -xf assetguard-certificates.tar -C /var/assetguard-manager/etc/certs/ ./$NODE_NAME.pem ./$NODE_NAME-key.pem ./root-ca.pem
sudo mv /var/assetguard-manager/etc/certs/$NODE_NAME.pem /var/assetguard-manager/etc/certs/manager.pem
sudo mv /var/assetguard-manager/etc/certs/$NODE_NAME-key.pem /var/assetguard-manager/etc/certs/manager-key.pem

# Set proper permissions
sudo chmod 500 /var/assetguard-manager/etc/certs
sudo chmod 400 /var/assetguard-manager/etc/certs/*
sudo chown -R assetguard-manager:assetguard-manager /var/assetguard-manager/etc/certs
```

**Note:** Replace `node-1` with the name you used when generating the certificates.

#### Configure indexer connection

Configure the AssetGuard server to connect to the AssetGuard indexer using the secure keystore:

```bash
# Set indexer credentials (default: admin/admin)
sudo /var/assetguard-manager/bin/assetguard-manager-keystore -f indexer -k username -v admin
sudo /var/assetguard-manager/bin/assetguard-manager-keystore -f indexer -k password -v admin
```

Update the indexer configuration in `/var/assetguard-manager/etc/assetguard-manager.conf` to specify the indexer IP address:

```xml
<indexer>
  <hosts>
    <host>https://127.0.0.1:9200</host>
  </hosts>
  <ssl>
    <certificate_authorities>
      <ca>/var/assetguard-manager/etc/certs/root-ca.pem</ca>
    </certificate_authorities>
    <certificate>/var/assetguard-manager/etc/certs/manager.pem</certificate>
    <key>/var/assetguard-manager/etc/certs/manager-key.pem</key>
  </ssl>
</indexer>
```

Replace `127.0.0.1` with your indexer IP address if it's running on a different host.

### Start the manager

Start and enable the server service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable assetguard-manager
sudo systemctl start assetguard-manager
```

Verify the server is running:

```bash
sudo systemctl status assetguard-manager
```

### Cluster configuration

The AssetGuard server cluster allows you to scale horizontally by distributing the load across multiple nodes. The cluster comes enabled by default with the following configuration in `/var/assetguard-manager/etc/assetguard-manager.conf`:

```xml
<cluster>
  <name>assetguard</name>
  <node_name>node01</node_name>
  <node_type>master</node_type>
  <key>fd3350b86d239654e34866ab3c4988a8</key>
  <port>1516</port>
  <bind_addr>127.0.0.1</bind_addr>
  <nodes>
      <node>127.0.0.1</node>
  </nodes>
  <hidden>no</hidden>
</cluster>
```

#### Multi-node deployment

For a multi-node cluster deployment, you need to configure one master node and one or more worker nodes. Follow these steps on each node:

1. **On the master node**, edit `/var/assetguard-manager/etc/assetguard-manager.conf`:

```xml
<cluster>
  <name>assetguard</name>
  <node_name>master-node</node_name>
  <node_type>master</node_type>
  <key>fd3350b86d239654e34866ab3c4988a8</key>
  <port>1516</port>
  <bind_addr>0.0.0.0</bind_addr>
  <nodes>
      <node>MASTER_NODE_IP</node>
  </nodes>
  <hidden>no</hidden>
</cluster>
```

Replace `MASTER_NODE_IP` with the actual IP address of the master node.

2. **On each worker node**, edit `/var/assetguard-manager/etc/assetguard-manager.conf`:

```xml
<cluster>
  <name>assetguard</name>
  <node_name>worker-node-01</node_name>
  <node_type>worker</node_type>
  <key>fd3350b86d239654e34866ab3c4988a8</key>
  <port>1516</port>
  <bind_addr>0.0.0.0</bind_addr>
  <nodes>
      <node>MASTER_NODE_IP</node>
  </nodes>
  <hidden>no</hidden>
</cluster>
```

Replace `MASTER_NODE_IP` with the actual IP address of the master node, and use a unique `node_name` for each worker.

3. **Restart the AssetGuard manager service** on all nodes after making configuration changes:

```bash
sudo systemctl restart assetguard-manager
```

4. **Verify the cluster status** from any node:

```bash
sudo /var/assetguard-manager/bin/cluster_control -l
```

### Configuration parameters

**`name`**\
Name of the cluster. All nodes must use the same cluster name.

**`node_name`**\
Unique name for each node in the cluster.

**`node_type`**\
Node role, either `master` or `worker`. Only one master node is allowed per cluster.

**`key`**\
Pre-shared key for cluster authentication. All nodes must use the same key.

**`port`**\
Port for cluster communication. Default: `1516`.

**`bind_addr`**\
IP address to bind the cluster listener. Use `0.0.0.0` to listen on all interfaces.

**`nodes`**\
List of master node IP addresses for worker nodes to connect to.

**`hidden`**\
Whether the node is hidden from the cluster. Default: `no`.

## Agent

### Linux

#### Debian-based platforms

```bash
sudo dpkg -i assetguard-agent_*.deb
```

You can optionally specify configuration parameters:

```bash
sudo ASSETGUARD_MANAGER='10.0.0.2' ASSETGUARD_AGENT_NAME='web-server-01' dpkg -i assetguard-agent_*.deb
```

#### Red Hat-based platforms

```bash
sudo rpm -ivh assetguard-agent-*.rpm
```

You can optionally specify configuration parameters:

```bash
sudo ASSETGUARD_MANAGER='10.0.0.2' ASSETGUARD_AGENT_NAME='web-server-01' rpm -ivh assetguard-agent-*.rpm
```

#### SUSE-based platforms

```bash
sudo rpm -ivh assetguard-agent-*.rpm
```

You can optionally specify configuration parameters:

```bash
sudo ASSETGUARD_MANAGER='10.0.0.2' ASSETGUARD_AGENT_NAME='web-server-01' rpm -ivh assetguard-agent-*.rpm
```

#### Starting the agent

After installation, start and enable the agent service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable assetguard-agent
sudo systemctl start assetguard-agent
```

Verify the agent is running:

```bash
sudo systemctl status assetguard-agent
```

### macOS

Install the agent:

```bash
sudo installer -pkg assetguard-agent-*.pkg -target /
```

You can optionally specify configuration parameters by writing them to `/tmp/assetguard_envs` before running the installer:

```bash
echo "ASSETGUARD_MANAGER='10.0.0.2'" > /tmp/assetguard_envs && echo "ASSETGUARD_AGENT_NAME='macbook-01'" >> /tmp/assetguard_envs && sudo installer -pkg assetguard-agent-*.pkg -target /
```

Start the agent service:

```bash
sudo launchctl bootstrap system /Library/LaunchDaemons/com.assetguard.agent.plist
```

Verify the agent is running:

```bash
sudo /Library/Ossec/bin/assetguard-control status
```

### Windows

Install the agent silently:

```powershell
assetguard-agent-*.msi /q
```

You can optionally specify configuration parameters:

```powershell
assetguard-agent-*.msi /q ASSETGUARD_MANAGER="10.0.0.2" ASSETGUARD_AGENT_NAME="windows-server-01"
```

For interactive installation, double-click the MSI file and follow the installation wizard.

Start the AssetGuard Agent service:

```powershell
Start-Service -Name assetguard
```

Verify the agent is running:

```powershell
Get-Service -Name assetguard
```

### Options

#### Server connection

**`ASSETGUARD_MANAGER`**\
Specifies the IP address or hostname of the AssetGuard server. The agent uses this to establish communication with the server.

**`ASSETGUARD_MANAGER_PORT`**\
Defines the port used to communicate with the AssetGuard server. Default: `1514`.

#### Enrollment configuration

**`ASSETGUARD_REGISTRATION_SERVER`**\
Specifies the IP address or hostname of the enrollment server. When not specified, the value of `ASSETGUARD_MANAGER` is used.

**`ASSETGUARD_REGISTRATION_PORT`**\
Defines the port used for agent enrollment. Default: `1515`.

**`ASSETGUARD_REGISTRATION_PASSWORD`**\
Sets the password required for agent enrollment. This password must match the one configured on the server.

**`ASSETGUARD_REGISTRATION_CA`**\
Specifies the path to the CA certificate used to verify the manager's identity during enrollment.

**`ASSETGUARD_REGISTRATION_CERTIFICATE`**\
Specifies the path to the agent's certificate for enrollment authentication.

**`ASSETGUARD_REGISTRATION_KEY`**\
Specifies the path to the agent's private key for enrollment authentication.

#### Agent identity

**`ASSETGUARD_AGENT_NAME`**\
Sets the agent's name for identification in the AssetGuard server. Default: system hostname.

**`ASSETGUARD_AGENT_GROUP`**\
Assigns the agent to a specific group upon enrollment. Default: `default`.

#### Advanced options

**`ASSETGUARD_KEEP_ALIVE_INTERVAL`**\
Defines the interval in seconds between keep-alive messages sent to the server. When not specified, system defaults apply.

**`ASSETGUARD_TIME_RECONNECT`**\
Forces the agent to reconnect to the server every N seconds. Default: disabled.

**`ENROLLMENT_DELAY`**\
Sets a delay in seconds between agent enrollment and the first connection attempt. When not specified, system defaults apply.
