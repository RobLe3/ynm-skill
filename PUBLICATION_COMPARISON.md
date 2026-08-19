# Publication Comparison: cc-blender-skill

This non-normative analysis records lessons from the read-only `cc-blender-skill` repository at revision `11016c9a5847897491dde935c346571bd7548e3d`. No Blender implementation or source expression is required by YNM.

| Observed pattern | Abstract problem solved | YNM equivalent | Specific elements removed | Decision |
|---|---|---|---|---|
| Installable plugin is separated from research and process documents | Users need a clear runtime boundary | Manifest classifies normative, optional, provenance, validation, and packaging artifacts | Blender plugin tree, asset libraries, domain knowledge | Adopt |
| Machine-readable skill registry | Installers need paths and versions that can be checked | Provider-neutral `manifest.yaml` | Claude, Blender, MCP requirements and skill registry roles | Adopt |
| Root and package READMEs provide install and verification steps | New users need an executable onboarding path | One public README plus manifest-driven verification | Claude-specific directories and restart instructions | Adopt in simpler form |
| Skills progressively load specialist references | Large skills should not consume unnecessary context | `SKILL.md` loads core contracts and selected loops/methods | Blender domain hierarchy and 30-skill routing | Retain existing YNM pattern |
| README separates what works from what remains limited | Capability claims need evidence labels | Five publication capability labels and explicit limitations | Scene-class claims and Blender version matrix | Adopt |
| Changelog and version rationale are distinct | Users need both changes and compatibility reasoning | `CHANGELOG.md` and concise `VERSIONING.md` | Long scene-by-scene development narrative | Adopt |
| Contribution and issue templates request reproducible context | Reports need enough evidence without exposing projects | Neutral contribution rules and privacy-aware issue forms | Blender version, MCP version, render requirements | Adopt |
| Failure-state evidence is retained | Validation should not cherry-pick success | Sanitized failure → finding → correction → regression records | Render assets and project-specific prompts | Adopt |
| Refinement workflow sanitizes project lessons before reuse | Project knowledge can contaminate a public skill | Publication improvement gate | Candidate generation, Blender repair queues, release push handoff | Adopt only the methodology |
| Provider-specific plugin manifest and installation | One runtime can offer convenient adapters | Optional `agents/openai.yaml` remains an adapter | Claude-only dependency and provider semantics | Reject as core |
| Extensive domain assets and runtime integrations | Blender tasks require domain tooling | None | Blender, Python scene scripts, MCP, geometry and rendering mechanisms | Reject |

The comparison supports packaging decisions only. It is not evidence for YNM's epistemic or lifecycle contracts.
