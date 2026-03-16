# Architecture

This page provides a high-level view of AssetGuard's architecture and how the main components interact. It is intended for developers who need to understand the overall system before diving into individual modules.

---

## 🧱 Core Components

### 1) AssetGuard Agent (Endpoint)

The agent runs on monitored hosts (Linux, Windows, containers) and is responsible for:

- File integrity monitoring (FIM)
- Log collection and forwarding
- Configuration assessment (SCA)
- Vulnerability scanning
- System inventory collection
- Active response (block, quarantine, etc.)
- Communicating with the manager over a secure agent sync protocol

Key code locations:
- `src/client-agent/` – main agent implementation
- `src/syscheckd/` – FIM subsystem
- `src/logcollector/` – log collection subsystem
- `src/sca/` – configuration assessment subsystem
- `src/vulnerability-scanner/` – vulnerability detection
- `src/remoted/` – remote command execution / active response

### 2) AssetGuard Manager (Server)

The manager centralizes events and data from agents, applies rules, and exposes data through APIs and dashboards.

Responsibilities:
- Accept agent connections and store metadata
- Process and match incoming events against rules
- Generate alerts and notify operators
- Provide REST API for UI and integrations
- Manage agent configuration/deployment and upgrades

Key code locations:
- `src/monitord/` – manager daemon and core services
- `src/api/` – API server and HTTP endpoint logic
- `api/` – Python server and API implementation
- `framework/` – shared Python libraries used by manager services

### 3) Data Storage & Search

AssetGuard integrates with Elasticsearch for long-term storage and search of events and alerts.
It also uses internal databases (e.g., RocksDB) for local metadata and caching.

- Elastic integration is configured via `etc/assetguard-manager.conf`.
- Local caches and metadata are stored under the manager data directory.

### 4) Dashboard & UI

The AssetGuard Web UI (Dashboard) is maintained in a separate repository (`assetguard-dashboard-plugins`).
It communicates with the manager via the REST API and provides visualization, filtering, and management tools.

---

## 🔗 How Components Communicate

### Agent ⇄ Manager (Sync Protocol)

Agents communicate with the manager using a binary sync protocol. It supports:

- Agent registration and heartbeats
- Inventory sync (host metadata, packages, processes, etc.)
- Event dispatch (alerts, system events)
- Remote commands (active response)

Relevant docs:
- [Agent Sync Protocol](ref/modules/utils/sync-protocol/README.md)

### Manager ⇄ Elasticsearch

The manager writes JSON events into Elasticsearch indices. It also reads and aggregates data for query and reporting.

### Manager ⇄ Dashboard UI

The dashboard consumes the manager API for:
- Alerts and event queries
- Agent status and inventory views
- Configuration management

---

## ✅ Module Breakdown (Reference)

The project is organized in modules, each with its own architecture and APIs.
See the Reference Manual for detailed module documentation:

- [Engine](ref/modules/engine/README.md)
- [FIM](ref/modules/fim/README.md)
- [Logcollector](ref/modules/logcollector/README.md)
- [Rootcheck](ref/modules/rootcheck/README.md)
- [SCA](ref/modules/sca/README.md)
- [Syscollector](ref/modules/syscollector/README.md)
- [VulnerabilityScanner](ref/modules/vulnerability-scanner/README.md)
- [Inventory Sync](ref/modules/inventory-sync/README.md)
- [Remoted](ref/modules/remoted/README.md)
- [Server API](ref/modules/server-api/README.md)

---

## 🧭 Additional architecture references

- [High-level API / events](ref/modules/server-api/api-reference.md)
- [Cluster / load balancing](ref/modules/cluster/README.md)
- [RBAC model](ref/modules/rbac/README.md)

---

*This page is intended to help developers rapidly grasp the major pieces of AssetGuard. For implementation details, follow the module-specific documentation linked above.*
