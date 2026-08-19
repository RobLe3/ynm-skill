# YNM Repository Guidance

## Purpose and sources

This repository contains the YNM review methodology and its public validation history. Normative behavior lives in `SKILL.md`, `contracts/`, `loops/`, and `methodology/`. Examples illustrate contracts but do not redefine them.

## Validation

Run before release or after a contract change:

```text
python3 validation/validate_ynm.py
python3 -m unittest discover -s tests -v
```

## Mutation and history

- Review remains read-only unless a requested class of write is explicit.
- Do not edit historical 1.0.0 or 1.1.0 maturity reports or release-state files.
- Add a new release-state directory and baseline hashes for each maturation change.
- Do not commit local databases, caches, credentials, private paths, or project-identifying evidence.

## Contributions and publication

Preserve disposition semantics, evidence provenance, lifecycle separation, focal ownership, capability standards, authority boundaries, and manual execution. Update dependent schemas, examples, tests, manifest, version, changelog, and maturity evidence when their canonical source changes. Release preparation does not authorize external publication unless that authority is explicit.
