# Output Reference

The output stage is responsible for sending alerts to different destinations. This stage is only supported by
`outputs assets` and can have multiple outputs. Each output can have its own configuration.


## First of

To choose between the different output methods the `first_of` stage can be used.
This acts as an if else block. The first `check` that returns true will execute what's inside the `then` block, this block can be filled with `File` or `Indexer` blocks.

### Signature

```yaml
outputs:
  - first_of:
    - check: A
      then:
        - assetguard-indexer:
            index: "A"

    - check: B
      then:
        - assetguard-indexer:
            index: "B"

    - check: true
      then:
        - assetguard-indexer:
            file: "C"
```

### Parameters

Accepts any array of `check` `then` blocks in each item the order is mandatory and will be respected as an order of execution. Ideally the last option should act as a fallback case.

### Asset example

```yaml
name: output/indexer/0

metadata:
  module: assetguard
  title: Indexer data stream outputs
  description: Output integrations events to assetguard-indexer

outputs:
  - first_of:
    - check: >-
        $assetguard.integration.category != "cloud-services" OR
        (NOT starts_with($assetguard.integration.name, "aws")
        AND NOT starts_with($assetguard.integration.name, "azure")
        AND NOT starts_with($assetguard.integration.name, "gcp"))

      then:
        - assetguard-indexer:
            index: "assetguard-events-v5-${assetguard.integration.category}"

    - check: starts_with($assetguard.integration.name, "gcp")
      then:
        - assetguard-indexer:
            index: "assetguard-events-v5-${assetguard.integration.category}-gcp"

    - check: starts_with($assetguard.integration.name, "azure")
      then:
        - assetguard-indexer:
            index: "assetguard-events-v5-${assetguard.integration.category}-azure"

    - check: starts_with($assetguard.integration.name, "aws")
      then:
        - assetguard-indexer:
            index: "assetguard-events-v5-${assetguard.integration.category}-aws"

```


## File

The `file` output sends alerts to a file. This output supports compression and rotation.

### Signature

```yaml
file: "alerts"
```

### Parameters

Only support "alerts" as a parameter, this writes alerts to `alerts.json` file.

### Asset example

```yaml
name: output/file-output-integrations/0

metadata:
  module: assetguard
  title: file output event
  description: Output integrations events to a file
  compatibility: >
    This decoder has been tested on AssetGuard version 5.x
  versions:
    - 5.x
  author:
    name: AssetGuard, Inc.
    date: 2022/11/08
  references:
    - ""

outputs:
  - file: "alerts"
```

## Indexer

The `indexer` output sends alerts to `assetguard-indexer` for indexing.

### Signature

```yaml
assetguard-indexer:
    index: ${INDEX}
```

### Parameters

| Name | type | required | Description |
|------|------|----------|-------------|
| index | string | yes | Data Stream name where the alerts will be indexed. Should be a valid assetguard-indexer data stream name and start with `assetguard-events-v5-`. |

Index name can be expanded with placeholders like `index-name-${PH1}-${PH2}`. If PHX results in an existing string reference to the event it will be replaced in runtime if not will be fail and the alert will not be sent to the indexer.
The replacement text is not sanitized, so referenced field values must already contain only valid index characters.

### Asset example

```yaml
name: output/indexer/0

metadata:
  module: assetguard
  title: Indexer output event
  description: Output integrations events to assetguard-indexer
  compatibility: >
    This decoder has been tested on AssetGuard version 5.0
  versions:
    - ""
  author:
    name: AssetGuard, Inc.
    date: 2025/12/01
  references:
    - ""

outputs:
  - assetguard-indexer:
      index: "assetguard-events-v5-${assetguard.integration.category}"
```

> [!TIP]
> The `$(DATE)` is special placeholder and replaced by the current date in the format `YYYY.MM.DD` when the alert is indexed.
