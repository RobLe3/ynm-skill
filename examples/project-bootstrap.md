# Project Bootstrap Example

## Before YNM

```text
sample-service/
├── README.md
├── src/
└── tests/
```

Read-only discovery maps `README.md` to project entry and adoption guidance. It finds no persistent YNM state and does not infer architecture, ownership, or validation commands from the directory names.

```text
python3 /path/to/ynm/scripts/project_integration.py sample-service
```

The user then explicitly authorizes persistent initialization:

```text
python3 /path/to/ynm/scripts/project_integration.py sample-service --initialize --apply
```

## After authorized initialization

```text
sample-service/
├── README.md
├── src/
├── tests/
└── .ynm/
    ├── README.md
    ├── project.yaml
    ├── config.yaml
    └── state/
        ├── findings.yaml
        ├── events.jsonl
        └── receipts/
            └── YNM-BOOT-….yaml
```

The first review remains read-only. With separate permission to persist review state, its findings update the current projection, append lifecycle events, and add a Run Receipt. No source, test, or README content changes. Running initialization again reuses the same files and bounded receipt identity rather than creating another scaffold.

The structured project context, configuration, and bootstrap receipt examples are under `examples/data/`.
