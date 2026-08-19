# Project Integration

Project Integration connects YNM to an existing project without making YNM the project's organizing system. It is a method selected before or alongside review, not a focal review loop.

## Modes and authority

| Mode | Default effect |
|---|---|
| `LOAD` | Read YNM instructions; do not inspect or modify project state. |
| `REVIEW` | Inspect and report; read-only unless another permission is explicit. |
| `INITIALIZE` | Create or update YNM-owned integration artifacts only with explicit write authorization. |
| `REVIEW + PERSIST` | Update authorized YNM state; do not modify other project artifacts. |
| `REVIEW + APPLY` | Modify only the explicitly authorized project scope after review. |

Capability never supplies authorization. Permission to write `.ynm/` does not grant permission to edit project documentation, and permission to edit one managed section does not grant permission to replace its containing file.

## Documentation-role discovery

Discover responsibilities from content, not filenames alone. Map available artifacts to these roles where evidence supports the mapping: project entry, agent guidance, project context, architecture source, implementation contracts, adoption guidance, operational guidance, contribution guidance, security guidance, release history, version policy, decision history, YNM configuration, YNM state, and YNM review history.

One artifact may satisfy several roles, and one role may require several artifacts. For each mapping retain the path, evidence for the mapping, and `CONFIRMED`, `CANDIDATE`, or `UNKNOWN` status. Existing artifacts take precedence over new scaffold files. An unfamiliar or conflicting artifact is inspected or left unresolved; it is not replaced.

## Minimal persistent scaffold

When persistence is requested, authorized, and not already supplied by an equivalent project mechanism, the default state root is `.ynm/`:

```text
.ynm/
├── README.md
├── project.yaml
├── config.yaml
└── state/
    ├── findings.yaml
    ├── events.jsonl
    └── receipts/<bootstrap-id>.yaml
```

Create assessment and snapshot directories only when they receive content. A project-native alternative may replace `.ynm/`, but `project.yaml` must record the canonical state location. Stateless review remains first-class and creates none of these files.

`project.yaml` records evidence-derived context and documentation-role mappings. `config.yaml` contains execution preferences, never core definitions. Unknown purpose, architecture, ownership, commands, or policy remains unknown; initialization must not manufacture project intent.

Project configuration may optionally set `review.max_immediate_iterations` to a positive integer. Absence means the implementation uses its safe execution decision without requiring a fixed count. The value is a safety bound and cannot redefine convergence or evidence sufficiency.

## AGENTS.md coexistence

`AGENTS.md` is optional. Preserve all existing content. A YNM section may be created or updated only when explicitly authorized and bounded by exactly one pair of markers:

```markdown
<!-- YNM:BEGIN -->
## YNM Project Review
...
<!-- YNM:END -->
```

If markers are malformed, duplicated, or ownership is otherwise uncertain, do not write. Report the ambiguity and require human resolution. The section contains only operational project context, source-of-truth pointers, invocation, read-only policy, state location, evidenced validation commands, mutation restrictions, authority boundaries, and handoffs. It does not copy YNM methodology or existing project documentation.

## Initialization algorithm

```text
load_ynm_read_only()
project = discover_project_and_documentation_roles()
existing = discover_project_instructions_and_ynm_state()
authority = determine_write_authorization()

map_existing_artifacts_before_proposing_files()
identify_only_missing_integration_responsibilities()

if persistence_not_requested or write_not_authorized:
    emit_recommendation_without_writing()
    emit_bootstrap_receipt()
    stop

plan_smallest_useful_scaffold()
compare_each_target_with_existing_content_and_ownership()
write_only_new_or_ynm_owned_authorized_surfaces()
validate_references_state_paths_and_no_overwrite()
emit_bootstrap_receipt()
```

Repeated initialization compares normalized desired state with existing state and produces no duplicate files, sections, or events. Generated files identify their YNM ownership and format version. User-maintained files are never replaced wholesale.

## Removal

Removal is planned, not assumed. A removal plan may delete a wholly YNM-owned state root and remove a valid bounded YNM section after separate authorization. It must list retained human-owned artifacts and warn about loss of longitudinal history. Core project operation must not depend on YNM unless the project deliberately created that dependency.

## Capability adaptation

A constrained executor performs narrower discovery, emits uncertain role mappings, and creates less. It does not generate speculative prose. A capable executor may inspect more evidence but receives no broader authority. Every bootstrap attempt emits a receipt, including read-only, blocked, and no-change outcomes.
