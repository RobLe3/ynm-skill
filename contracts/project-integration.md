# Project Integration Records

These records describe project-local integration. They do not redefine findings, evidence, dispositions, or authorization.

## Project context

Required fields are `schema_version`, `project.name`, `project.root`, `documentation_roles`, `ynm_state_location`, `persistence_mode`, and `discovered_at`. Project purpose, type, sources, applicable loops, exclusions, constraints, and discovered capabilities are optional because discovery may not establish them.

Each documentation-role entry records `role`, `artifacts`, and `status`. An artifact records a relative path and evidence for the mapping. Relative paths preserve portability; absolute project paths may be used transiently during discovery but must not enter a public example or reusable package.

## Project configuration

Configuration controls local execution only. It may select persistence, default read-only mode, loop selection, include/exclude scope, state location, and mutation policy. It cannot redefine YES, NO, MAYBE, evidence sufficiency, lifecycle transitions, or loop authority.

## Bootstrap receipt

Every initialization attempt records a bootstrap ID, project identifier, mode, terminal execution status, discovered and reused artifacts, created and updated artifacts, conflicts intentionally left untouched, canonical state location, authorization status, persistence mode, unresolved questions, and timestamp. Created and updated lists may be empty. `PARTIAL` and `BLOCKED` receipts explain why execution stopped.

## Ownership

YNM-created standalone files carry `managed_by: ynm` and a format version where their format permits it. A YNM-managed section in a human file is owned only between its markers. Absence of ownership evidence means ownership is unknown, not YNM-owned.
