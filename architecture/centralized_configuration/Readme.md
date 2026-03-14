<!---
Copyright (C) 2015, AssetGuard Inc.
Created by AssetGuard, Inc. <info@assetguard.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
-->

# Centralized Configuration
## Index
- [Centralized Configuration](#centralized-configuration)
  - [Index](#index)
  - [Purpose](#purpose)
  - [Sequence diagram](#sequence-diagram)

## Purpose

One of the key features of AssetGuard as a EDR is the Centralized Configuration, allowing to deploy configurations, policies, rootcheck descriptions or any other file from AssetGuard Manager to any AssetGuard Agent based on their grouping configuration. This feature has multiples actors: AssetGuard Cluster (Master and Worker nodes), with `assetguard-manager-remoted` as the main responsible from the managment side, and AssetGuard Agent with `assetguard-agentd` as resposible from the client side.


## Sequence diagram
Sequence diagram shows the basic flow of Centralized Configuration based on the configuration provided. There are mainly three stages:
1. AssetGuard Manager Master Node (`assetguard-manager-remoted`) creates every `remoted.shared_reload` (internal) seconds the files that need to be synchronized with the agents.
2. AssetGuard Cluster as a whole (via `assetguard-manager-clusterd`) continuously synchronize files between AssetGuard Manager Master Node and AssetGuard Manager Worker Nodes
3. AssetGuard Agent `assetguard-agentd` (via ) sends every `notify_time` (ossec.conf) their status, being `merged.mg` hash part of it. AssetGuard Manager Worker Node (`assetguard-manager-remoted`) will check if agent's `merged.mg` is out-of-date, and in case this is true, the new `merged.mg` will be pushed to AssetGuard Agent.
