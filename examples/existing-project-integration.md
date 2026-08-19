# Existing Documentation Integration Example

## Before YNM

```text
handbook-project/
├── AGENTS.md
├── README.md
├── DESIGN.md
├── CONTRIBUTING.md
└── docs/
```

Discovery maps the existing files to agent guidance, project entry, architecture source, contribution guidance, and adoption guidance. It does not create replacement documents.

Without write authorization, initialization returns a proposed scaffold and `REQUIRES_HUMAN`; no file is created. With explicit authorization for persistent state and an `AGENTS.md` integration section:

```text
python3 /path/to/ynm/scripts/project_integration.py handbook-project \
  --initialize --agents-section --apply
```

YNM appends one bounded section to `AGENTS.md` while preserving every existing byte outside the markers. The section points to existing documents and `.ynm/`; it does not duplicate their contents. A second run replaces only the bounded section if its generated content changed.

If the file has malformed or duplicate YNM markers, initialization returns `BLOCKED`, leaves the file untouched, and records the conflict. Project instructions that forbid an otherwise available action remain authoritative.
