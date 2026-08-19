# Publication Package Example

The repository contains more evidence than an installation needs.

| Class | Examples | Required at runtime? |
|---|---|---|
| NORMATIVE | `SKILL.md`, `contracts/`, `loops/`, `methodology/` | Yes, according to the selected invocation |
| OPTIONAL | `schemas/`, `scripts/`, examples, `agents/openai.yaml` | Only for the selected capability or runtime |
| PACKAGING | `manifest.yaml`, README, license, version, changelog | Required for distribution, not methodology semantics |
| PROVENANCE | historical design notes and prior internal notes | No |
| VALIDATION | tests, candidate assessment ledgers, sanity checks | No; supports release claims |

A minimal package for general review contains the entrypoint, normative directories, license and notice. Project initialization additionally needs `scripts/project_integration.py`, its record contract, and three schemas. Removing provenance and maturation history must not affect either operation.
