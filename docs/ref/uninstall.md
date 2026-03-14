# Uninstall

This guide provides instructions for uninstalling AssetGuard server and agent components. The uninstallation process automatically stops the service before removing the package.

## Server

### Debian-based platforms

Remove the package:

```bash
sudo dpkg --purge assetguard-manager
```

To remove the package but keep configuration files:

```bash
sudo dpkg --remove assetguard-manager
```

### Red Hat-based platforms

Remove the package:

```bash
sudo rpm -e assetguard-manager
```

## Agent

### Linux

#### Debian-based platforms

Remove the package:

```bash
sudo dpkg --purge assetguard-agent
```

To remove the package but keep configuration files:

```bash
sudo dpkg --remove assetguard-agent
```

#### Red Hat-based platforms

Remove the package:

```bash
sudo rpm -e assetguard-agent
```

#### SUSE-based platforms

Remove the package:

```bash
sudo rpm -e assetguard-agent
```

### macOS

Stop the agent service:

```bash
sudo launchctl bootout system /Library/LaunchDaemons/com.assetguard.agent.plist
```

Remove the package:

```bash
sudo rm -rf /Library/Ossec
sudo rm -f /Library/LaunchDaemons/com.assetguard.agent.plist
sudo rm -rf /Library/StartupItems/ASSETGUARD
```

Remove the AssetGuard user and group:

```bash
sudo dscl . -delete "/Users/assetguard"
sudo dscl . -delete "/Groups/assetguard"
```

Remove from pkgutil:

```bash
sudo pkgutil --forget com.assetguard.pkg.assetguard-agent
```

### Windows

Uninstall the package:

```powershell
msiexec.exe /x assetguard-agent-*.msi /qn
```

For interactive uninstallation, use the Windows "Add or Remove Programs" feature.
