<!---
Copyright (C) 2015, AssetGuard Inc.
Created by AssetGuard, Inc. <info@assetguard.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
-->

# Metrics

## Index

- [Metrics](#metrics)
  - [Index](#index)
  - [Purpose](#purpose)
  - [Sequence diagram](#sequence-diagram)

## Purpose

AssetGuard includes some metrics to understand the behavior of its components, which allow to investigate errors and detect problems with some configurations. This feature has multiple actors: `assetguard-manager-remoted` for agent interaction messages, `assetguard-manager-analysisd` for processed events.

## Sequence diagram

The sequence diagram shows the basic flow of metric counters. These are the main flows:

1. Messages received by `assetguard-manager-remoted` from agents.
2. Messages that `assetguard-manager-remoted` sends to agents.
3. Events received by `assetguard-manager-analysisd`.
4. Events processed by `assetguard-manager-analysisd`.
