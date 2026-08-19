# Authorization Contract

Authorization describes permission to perform a recommended action. It is independent of epistemic disposition and review execution.

| Status | Meaning |
|---|---|
| `NOT_REQUESTED` | No action permission was requested. |
| `REQUIRES_HUMAN` | The action exceeds delegated authority or requires an accountable human decision. |
| `AUTHORIZED` | A named authority permitted a defined action and scope. |
| `DENIED` | A named authority declined the requested action. |

An authorization event identifies `action`, `scope`, `status`, `actor`, `authority_basis`, `at`, and `rationale`. Add expiry, conditions, or integrity references when useful. Authorization for one action does not transfer to related actions.

YES never grants permission. NO never authorizes deletion or rollback. MAYBE never means execution failed. Capability existence also does not imply authorization. Destructive, irreversible, security-sensitive, privacy-sensitive, legal, migration, breaking, or ownership-sensitive actions default to `REQUIRES_HUMAN` unless explicit delegated authority is recorded.

