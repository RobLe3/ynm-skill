# Adaptive Execution Contract

YNM selects the least expensive execution path capable of supporting a defensible disposition. Execution level describes justified work, not result quality.

## Levels

- `YNM-0 ROUTE` bounds the proposition, risk, authority, perspectives, retrieval, capability, and budget. It does not conduct a broad review.
- `YNM-1 EVALUATE` acquires the minimum targeted evidence, checks sufficiency, assigns a bounded disposition, and stops early.
- `YNM-2 SPECIALIZE` adds only perspectives with credible expected information value.
- `YNM-3 ASSURE` adds comprehensive, adversarial, or independent evaluation for high-consequence work.

Every move to a higher level records `current_level`, `next_level`, reason codes, expected information gain, and expected cost. Supported reasons are `CONFLICTING_EVIDENCE`, `INSUFFICIENT_EVIDENCE`, `HIGH_IMPACT`, `AUTHORITY_AMBIGUITY`, `SECURITY_RELEVANT`, `SPECIALIST_DISAGREEMENT`, `BROAD_PROPOSITION`, `RELEASE_OR_PROMOTION`, and `USER_REQUESTED_DEEP_REVIEW`.

## Modes and budgets

`PORTABLE` uses ordinary project access. `ACCELERATED` may use verified optional capability providers. Both apply identical evidence and authority standards.

`LIGHT`, `NORMAL`, and `THOROUGH` bound specialists, evidence expansion, rechecks, and retrieval. Exhaustion preserves MAYBE; it never forces YES or NO.

## Evidence sufficiency

A material proposition records required, available, and missing evidence, affirmative support, coverage, contradiction-search status, and whether scope is bounded.

A normal affirmative YES requires affirmative support, sufficient coverage, and bounded scope. Absence of a discovered contradiction is not affirmative support. A bounded negative proposition can receive YES when the complete declared search space and prohibited set were examined.

Broad propositions are decomposed before depth increases. Unresolved sub-propositions remain visible in Delivery.

## Instrumentation

Record observable level, specialist, evidence, cache, retrieval, source-I/O, model/tool, timing, and early-stop metrics. Mark unavailable metrics unavailable rather than estimating them.
