# Developer Onboarding

Welcome to AssetGuard! This document is intended to help new developers get up to speed quickly by providing a broad overview of the project, its architecture, development workflows, and key locations in the repository.

> **Note:** AssetGuard uses a mix of C/C++ (core), Python (API and tooling), and web technologies (UI dashboards). This guide points to deeper reference docs where full details exist.

---

## 🔎 What is AssetGuard?

AssetGuard is an open-source security platform for threat prevention, detection, and response. It consists of two main pieces:

1. **AssetGuard Agent** (endpoint component)
   - Runs on monitored hosts (Linux, Windows, containers)
   - Collects system telemetry, performs file integrity monitoring, log collection, vulnerability detection, configuration assessment, etc.
   - Reports events and inventory to the manager.

2. **AssetGuard Manager** (server component)
   - Receives, analyzes, correlates, and stores events from agents.
   - Provides rule-based alerting, reporting, and a web UI (Dashboard) for operators.
   - Integrates with Elastic Stack for storage/search/visualization.

The project also includes **cloud connectors** (AWS/Azure/GCP/GitHub/Office365) and **orchestration tools** (Docker, Kubernetes, Ansible, etc.).

---

## 📁 Repository Layout (Key Folders)

### Root-level
- `docs/` – mdBook documentation source (this site)
- `src/` – core C/C++ source for the agent and manager
- `framework/` – Python libraries for manager and agent tooling
- `api/` – Python API server, REST endpoints, and management logic
- `ruleset/` – detection rules, decoders, and predefined alerts
- `tests/` – integration & functional tests
- `packages/` – packaging scripts (RPM/DEB/WPK/etc.)

### Important subtrees
- `src/client-agent/` – agent client implementation
- `src/monitord/` – manager daemon
- `src/agent-upgrade/` – automated agent upgrade logic
- `src/shared/` – shared libraries and utilities
- `docs/dev/` – developer-focused build & test guides
- `docs/ref/` – reference documentation for modules and configuration

---

## 🧠 High-level Architecture (where to read more)

### Core components
- **Manager (server)**: `src/monitord/`, `src/api/`, `api/` (Python)
- **Agent**: `src/client-agent/`, `src/agent-upgrade/`, `src/win32/` (Windows support)
- **Rules & decoders**: `ruleset/`
- **Storage**: Elasticsearch / RocksDB (used for local caching / metadata)

### Key documentation pages
- Architecture overview: [docs/ref/architecture.md](ref/architecture.md)
- Module reference: [docs/ref/modules/README.md](ref/modules/README.md)
- Configuration: [docs/ref/configuration.md](ref/configuration.md)
- Glossary: [docs/ref/glossary.md](ref/glossary.md)

---

## 🛠️ Development Environment (quick start)

### 1) Set up your machine
- Recommended: **Ubuntu 24.04** (Linux is the primary development platform)
- Follow: [docs/dev/setup.md](dev/setup.md)

### 2) Build from source
- Build manager/agent: [docs/dev/build-sources.md](dev/build-sources.md)
- Run locally: [docs/dev/run-sources.md](dev/run-sources.md)

### 3) Run tests
- Unit & integration tests: [docs/dev/test-execution.md](dev/test-execution.md)

---

## 🧩 Typical Developer Workflows

### Adding a new feature / module
1. Pick the right layer: Agent (<code>src/client-agent/</code>) vs Manager (<code>src/monitord/</code> + <code>api/</code>)
2. Add configuration options under `etc/agent.conf` or `etc/assetguard-manager.conf`
3. Update rules in `ruleset/` if applicable
4. Add/extend tests (`tests/` + `src/unit_tests/`)
5. Update documentation under `docs/ref/` (preferred) and add a SUMMARY entry

### Debugging / tracing
- Use `gdb` or `lldb` for native C/C++ debugging (see `.vscode/launch.json` in docs/dev/setup)
- Use `strace` / `perf` / `valgrind` as needed for low-level debugging

### Working with the Dashboard
- The web UI is a separate repository (AssetGuard Dashboard Plugins) but integrates tightly with the manager API. Look for API endpoints under `src/api/` and `api/`.

---

## ✅ Key resources for new developers

- **Documentation site**: `docs/` (built via mdBook)
- **Code style / conventions**: follow existing patterns (C style, indentation, error handling)
- **Issue tracker**: Use GitHub Issues for bugs/features
- **Communication**: Slack (`assetguard.com/community`), mailing list

---

## 📌 Quick Start Checklist (first day)

- [ ] Clone the repo and open it in VS Code
- [ ] Run `docs/build.sh` and open `docs/book/index.html`
- [ ] Build the agent and manager locally (`make TARGET=agent`, `make TARGET=server`)
- [ ] Run the full test suite (`make test` / `docs/dev/test-execution.md`)
- [ ] Pick a small issue or documentation task and submit a PR

---

## 📚 Further Reading (next steps)
- [Setup environment](dev/setup.md)
- [Build from sources](dev/build-sources.md)
- [Deployment & packaging](dev/package-generation.md)
- [Reference modules](ref/modules/README.md)
- [Security considerations](ref/security.md)

---

*This onboarding guide is designed to be a starting point. As you explore the codebase, update this document to reflect changes and make it easier for the next developer.*
