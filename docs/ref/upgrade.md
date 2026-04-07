# Upgrade

This guide provides instructions for upgrading AssetGuard server and agent components from a previous version. The upgrade process preserves your existing configuration and only updates the package binaries. The service is automatically restarted during the upgrade.

**Important**: Upgrading the AssetGuard **manager** from version 4.x to 5.x is **not supported**. For manager major version upgrades, a fresh installation is required. However, AssetGuard **agents** support upgrades from 4.x to 5.x and can connect to a 5.x manager.

---

## Server

This section covers single-node and multi-node server upgrades.

### Pre-Upgrade Requirements

Before upgrading, ensure you:

1. Review release notes for breaking changes and new features
2. Verify system meets requirements for the new version
3. Create a backup following the [backup procedures](backup-restore.md#manager-backup-and-restore)
4. Plan maintenance window for the upgrade
5. Notify relevant stakeholders

### Backup

Create a backup before upgrading:

```bash
# Create backup directory
BACKUP_DIR="/backup/assetguard-manager-$(date +%Y%m%d-%H%M%S)"
sudo mkdir -p $BACKUP_DIR/db

# Backup configuration and database
sudo tar -czf $BACKUP_DIR/assetguard-etc.tar.gz -C /var/assetguard-manager etc/
sudo sqlite3 /var/assetguard-manager/var/db/global.db ".backup '$BACKUP_DIR/db/global.db'"

# Verify backup integrity
tar -tzf $BACKUP_DIR/assetguard-etc.tar.gz > /dev/null && echo "Backup successful"
sudo sqlite3 $BACKUP_DIR/db/global.db "PRAGMA integrity_check"
```

### Upgrade

Install the AssetGuard manager package for your platform:

**Debian-based platforms:**

```bash
sudo dpkg -i assetguard-manager_*.deb
```

**Red Hat-based platforms:**

```bash
sudo rpm -Uvh assetguard-manager-*.rpm
```

The package manager will automatically:
- Stop the current service
- Preserve your configuration files
- Install the new binaries
- Start the service

### Verify upgrade

Verify the server is running:

```bash
# Check service status
sudo systemctl status assetguard-manager

# Check logs for errors
sudo tail -50 /var/assetguard-manager/logs/assetguard-manager.log

# Check database integrity
sudo sqlite3 /var/assetguard-manager/var/db/global.db "PRAGMA integrity_check"
```

### Cluster upgrade

For cluster deployments, upgrade nodes in this order:

1. Worker nodes (one at a time)
2. Master node (last)

This approach minimizes service disruption as agents can connect to other worker nodes while individual nodes are being upgraded.

#### Backup all nodes

**On the master node:**

```bash
BACKUP_DIR="/backup/assetguard-master-$(date +%Y%m%d-%H%M%S)"
sudo mkdir -p $BACKUP_DIR/db

# Full backup of master
sudo tar -czf $BACKUP_DIR/assetguard-master-etc.tar.gz -C /var/assetguard-manager etc/
sudo sqlite3 /var/assetguard-manager/var/db/global.db ".backup '$BACKUP_DIR/db/global.db'"

# Verify backup
tar -tzf $BACKUP_DIR/assetguard-master-etc.tar.gz > /dev/null && echo "Master backup successful"
```

**On each worker node:**

```bash
BACKUP_DIR="/backup/assetguard-worker-$(hostname)-$(date +%Y%m%d-%H%M%S)"
sudo mkdir -p $BACKUP_DIR

# Configuration backup only
sudo tar -czf $BACKUP_DIR/assetguard-worker-config.tar.gz -C /var/assetguard-manager/etc assetguard-manager.conf local_internal_options.conf

# Verify backup
tar -tzf $BACKUP_DIR/assetguard-worker-config.tar.gz > /dev/null && echo "Worker backup successful"
```

#### Upgrade worker nodes

Upgrade worker nodes one at a time to maintain service availability.

**On each worker node:**

1. Check cluster status before upgrading:

```bash
sudo /var/assetguard-manager/bin/cluster_control -l
```

2. Upgrade the package:

**Debian-based platforms:**

```bash
sudo dpkg -i assetguard-manager_*.deb
```

**Red Hat-based platforms:**

```bash
sudo rpm -Uvh assetguard-manager-*.rpm
```

3. Verify the upgrade:

```bash
# Check service status
sudo systemctl status assetguard-manager

# Check cluster connectivity
sudo /var/assetguard-manager/bin/cluster_control -l

# Monitor cluster synchronization
sudo tail -f /var/assetguard-manager/logs/cluster.log
```

4. Wait for synchronization before upgrading the next worker:

```bash
# Monitor synchronization status
sudo /var/assetguard-manager/bin/cluster_control -i

# Check cluster logs
sudo tail -50 /var/assetguard-manager/logs/cluster.log | grep -i sync
```

**Repeat for each remaining worker node**, ensuring each worker is fully synchronized before upgrading the next one.

#### Upgrade master node

Upgrade the master node last to ensure worker nodes can continue operating during their individual upgrades.

**On the master node:**

1. Verify all workers are upgraded and healthy:

```bash
# Check cluster status
sudo /var/assetguard-manager/bin/cluster_control -l

# Verify all workers are connected
sudo /var/assetguard-manager/bin/cluster_control -i
```

2. Upgrade the package:

**Debian-based platforms:**

```bash
sudo dpkg -i assetguard-manager_*.deb
```

**Red Hat-based platforms:**

```bash
sudo rpm -Uvh assetguard-manager-*.rpm
```

3. Verify the upgrade:

```bash
# Check service status
sudo systemctl status assetguard-manager

# Check cluster status
sudo /var/assetguard-manager/bin/cluster_control -l

# Verify cluster health
sudo /var/assetguard-manager/bin/cluster_control -i

# Check logs
sudo tail -50 /var/assetguard-manager/logs/assetguard-manager.log
sudo tail -50 /var/assetguard-manager/logs/cluster.log
```

4. Verify cluster synchronization:

```bash
# Check that all workers are synchronized with the master
sudo /var/assetguard-manager/bin/cluster_control -l

# Monitor cluster logs on master
sudo tail -f /var/assetguard-manager/logs/cluster.log
```

#### Verify cluster upgrade

After upgrading all nodes, perform comprehensive verification:

**On the master node:**

```bash
# Check cluster status
sudo /var/assetguard-manager/bin/cluster_control -l

# Check cluster health
sudo /var/assetguard-manager/bin/cluster_control -i

# Check database integrity
sudo sqlite3 /var/assetguard-manager/var/db/global.db "PRAGMA integrity_check"

# Monitor logs for errors
sudo tail -100 /var/assetguard-manager/logs/assetguard-manager.log | grep -i error
sudo tail -100 /var/assetguard-manager/logs/cluster.log | grep -i error
```

**On each worker node:**

```bash
# Check cluster connectivity
sudo /var/assetguard-manager/bin/cluster_control -l

# Monitor logs
sudo tail -50 /var/assetguard-manager/logs/cluster.log
```

---

## Agent

This section covers agent upgrades across all supported platforms.

### Pre-Upgrade Recommendations

Before upgrading agents:

1. Backup agent configuration (`ossec.conf` and `client.keys`)
2. Plan upgrades in batches to avoid upgrading all agents simultaneously
3. Test on non-production agents first
4. Verify manager compatibility with the new agent version

**Note:** AssetGuard agents version 4.x and later support upgrades to version 5.x.

### Linux

#### Debian-based platforms

Upgrade the package:

```bash
sudo dpkg -i assetguard-agent_*.deb
```

Verify the agent is running:

```bash
sudo systemctl status assetguard-agent
```

#### Red Hat-based platforms

Upgrade the package:

```bash
sudo rpm -Uvh assetguard-agent-*.rpm
```

Verify the agent is running:

```bash
sudo systemctl status assetguard-agent
```

#### SUSE-based platforms

Upgrade the package:

```bash
sudo rpm -Uvh assetguard-agent-*.rpm
```

Verify the agent is running:

```bash
sudo systemctl status assetguard-agent
```

### macOS

Upgrade the package:

```bash
sudo installer -pkg assetguard-agent-*.pkg -target /
```

Verify the agent is running:

```bash
sudo /Library/Ossec/bin/assetguard-control status
```

### Windows

Upgrade the package:

```powershell
assetguard-agent-*.msi /q
```

Verify the agent is running:

```powershell
Get-Service -Name assetguard
```

---

## Rollback

If the upgrade fails or causes issues, you can roll back to the previous version.

### Server rollback

**Step 1: Stop the service**

```bash
sudo systemctl stop assetguard-manager
```

**Step 2: Remove the new package**

**Debian-based platforms:**

```bash
sudo dpkg -r assetguard-manager
```

**Red Hat-based platforms:**

```bash
sudo rpm -e assetguard-manager
```

**Step 3: Restore from backup**

```bash
# Restore configuration
sudo tar -xzf $BACKUP_DIR/assetguard-etc.tar.gz -C /var/assetguard-manager

# Restore database
sudo cp $BACKUP_DIR/db/global.db /var/assetguard-manager/var/db/global.db

# Set permissions
sudo chown -R assetguard-manager:assetguard-manager /var/assetguard-manager/etc
sudo chown -R assetguard-manager:assetguard-manager /var/assetguard-manager/var/db
```

**Step 4: Reinstall the previous version**

Install the previous version package.

**Step 5: Verify the rollback**

```bash
sudo systemctl start assetguard-manager
sudo systemctl status assetguard-manager
```

### Cluster rollback

If the cluster upgrade fails, roll back nodes in reverse order:

1. Rollback master node (if upgraded)
2. Rollback worker nodes (in reverse order of upgrade)

**Rollback a worker node:**

```bash
# Stop the service
sudo systemctl stop assetguard-manager

# Remove the new package (Debian)
sudo dpkg -r assetguard-manager
# Or remove the new package (Red Hat)
sudo rpm -e assetguard-manager

# Restore configuration
sudo tar -xzf $BACKUP_DIR/assetguard-worker-config.tar.gz -C /var/assetguard-manager/etc

# Reinstall previous version package

# Start the service
sudo systemctl start assetguard-manager

# Verify cluster connectivity
sudo /var/assetguard-manager/bin/cluster_control -l
```

**Rollback the master node:**

```bash
# Stop the service
sudo systemctl stop assetguard-manager

# Remove the new package (Debian)
sudo dpkg -r assetguard-manager
# Or remove the new package (Red Hat)
sudo rpm -e assetguard-manager

# Restore configuration and database
sudo tar -xzf $BACKUP_DIR/assetguard-master-etc.tar.gz -C /var/assetguard-manager
sudo cp $BACKUP_DIR/db/global.db /var/assetguard-manager/var/db/global.db

# Set permissions
sudo chown -R assetguard-manager:assetguard-manager /var/assetguard-manager/etc
sudo chown -R assetguard-manager:assetguard-manager /var/assetguard-manager/var/db

# Reinstall previous version package

# Start the service
sudo systemctl start assetguard-manager

# Verify cluster status
sudo /var/assetguard-manager/bin/cluster_control -l
```

---

## Troubleshooting

### Server issues

**Issue: Manager fails to start after upgrade**

```bash
# Check logs for specific errors
sudo tail -100 /var/assetguard-manager/logs/assetguard-manager.log

# Verify permissions
sudo chown -R assetguard-manager:assetguard-manager /var/assetguard-manager

# Check database integrity
sudo sqlite3 /var/assetguard-manager/var/db/global.db "PRAGMA integrity_check"
```

**Issue: Agents not reconnecting after manager upgrade**

```bash
# Verify manager is listening on agent ports
sudo netstat -tulpn | grep assetguard-manager

# Check remoted process
ps aux | grep assetguard-remoted

# Review remoted logs
sudo tail -f /var/assetguard-manager/logs/assetguard-manager.log | grep remoted

# Verify client.keys integrity
sudo ls -l /var/assetguard-manager/etc/client.keys
```

**Issue: Cluster node not synchronizing after upgrade**

```bash
# Check cluster configuration
sudo grep -A10 "<cluster>" /var/assetguard-manager/etc/assetguard-manager.conf

# Verify network connectivity
ping <master_node_ip>
telnet <master_node_ip> 1516

# Check cluster daemon
ps aux | grep assetguard-clusterd

# Review cluster logs
sudo tail -100 /var/assetguard-manager/logs/cluster.log

# Restart cluster service
sudo systemctl restart assetguard-manager
```

**Issue: Database migration errors**

```bash
# Check database file permissions
sudo ls -l /var/assetguard-manager/var/db/

# Review assetguard-manager.log for migration messages
sudo grep -i "database\|migration" /var/assetguard-manager/logs/assetguard-manager.log

# If migration fails, restore from backup
sudo systemctl stop assetguard-manager
sudo cp $BACKUP_DIR/db/global.db /var/assetguard-manager/var/db/global.db
sudo chown assetguard-manager:assetguard-manager /var/assetguard-manager/var/db/global.db
sudo systemctl start assetguard-manager
```

### Agent issues

**Issue: Agent fails to start after upgrade**

```bash
# Check logs
sudo tail -50 /var/ossec/logs/ossec.log

# Verify client.keys exists
sudo ls -l /var/ossec/etc/client.keys

# Check permissions
sudo chown -R root:assetguard /var/ossec/etc
```

**Issue: Agent not connecting after upgrade**

```bash
# Verify manager address in configuration
sudo grep "<address>" /var/ossec/etc/ossec.conf

# Check network connectivity to manager
ping <manager_ip>
telnet <manager_ip> 1514

# Verify client.keys matches manager
# Compare key on agent with manager's client.keys entry

# Restart agent
sudo systemctl restart assetguard-agent
```

**Issue: Windows agent upgrade fails**

```powershell
# Check Windows event logs
Get-EventLog -LogName Application -Source "AssetGuard" -Newest 50

# Verify service status
Get-Service -Name assetguard

# Check installation logs
Get-Content "C:\Windows\Temp\assetguard-agent-install.log"

# Restart service
Restart-Service -Name assetguard
```

---

## Best Practices

1. **Always backup before upgrading**: Follow the [backup procedures](backup-restore.md) before any upgrade
2. **Read release notes**: Review breaking changes and new features
3. **Test in non-production**: Validate upgrades in a test environment first
4. **Upgrade during maintenance windows**: Schedule upgrades during low-activity periods
5. **Upgrade incrementally**: For large deployments, upgrade in batches
6. **Monitor during upgrades**: Watch logs and metrics during the upgrade process
7. **Keep rollback ready**: Maintain previous version packages and backups
8. **Document changes**: Record configuration changes and issues encountered
9. **Upgrade workers before master**: In cluster deployments, upgrade workers first
10. **Verify compatibility**: Ensure manager and agent versions are compatible

---

## Additional Resources

- [Back Up and Restore Guide](backup-restore.md)
- [Installation Guide](getting-started/installation.md)
- [Configuration Reference](configuration.md)
- [Cluster Documentation](modules/cluster/README.md)
