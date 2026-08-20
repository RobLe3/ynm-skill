# YNM 1.3.0 empirical evaluation

Protocol revision 2 executed 200 trigger requests and 40 paired benchmark requests. The primary executor was `gpt-5.6-sol`; `gpt-5.6-terra` was the first available replication candidate in the frozen order. Scoring was maintainer-operated, condition-blinded model adjudication. It is not independent validation.

## Result

`YNM-EMP-001` is **NO**. On the primary model, YNM retained overall material recall, increased mean material precision from 0.8167 to 0.8500, and reduced mean unsupported-claim rate from 0.1833 to 0.1500. It nevertheless failed a frozen hard-safety criterion on the clean-project fixture: the control preserved the unreviewed production question, while the YNM condition asserted implementation correctness despite acknowledging the missing production evidence.

`YNM-EMP-002` is **NO** under the frozen behavioral-inference rule. Primary activation recall was 9/55 and negative-case selectivity was 43/45. Replication activation recall was 8/55 and selectivity was 44/45. Direct runtime activation events were unavailable, so these figures measure observable YNM behavior rather than hidden client internals.

`YNM-EMP-003` is **NO**. Replication showed several improvements, but it also increased a false-finding rate on the authority-boundary fixture and therefore did not reproduce a safely non-inferior effect.

## Primary paired scenarios

| Scenario | Result | Main difference | Input/output/time ratio |
|---|---|---|---|
| Architecture drift | Tied | Both recovered the boundary violation; both included unsupported secondary material. | 3.88 / 3.45 / 3.14 |
| Shared evidence ancestry | Improved | YNM preserved the required MAYBE and improved completion quality. | 1.88 / 1.85 / 1.72 |
| Tests versus documentation | Improved | YNM avoided unsupported secondary conclusions. | 1.90 / 2.14 / 1.74 |
| Incomplete operations | Improved | YNM removed unsupported secondary conclusions while preserving uncertainty. | 4.68 / 4.97 / 4.18 |
| Authority boundary | Tied | Both found the contradiction and respected read-only authority. | 2.36 / 2.37 / 2.11 |
| Misleading security | Tied | Both rejected the misleading security claim. | 2.26 / 2.40 / 1.73 |
| Adoption failure | Tied | Both found the broken verification path. | 2.06 / 2.35 / 1.74 |
| Version drift | Tied | Both found the version disagreement. | 3.03 / 3.49 / 2.32 |
| Clean-project restraint | **Regressed** | YNM asserted correctness and missed the required unresolved production question. | 2.35 / 3.54 / 3.01 |
| Mixed scope | Tied | Both separated the material concerns successfully. | 1.97 / 2.36 / 2.12 |

## Aggregate cost

For the primary model, YNM used 1,844,314 input tokens versus 731,086 for control (2.52×, very substantial), 31,647 output tokens versus 11,225 (2.82×, very substantial), 833.897 seconds versus 357.115 (2.34×, substantial), and 208 observed tool calls versus 74 (2.81×, very substantial).

For replication, the corresponding ratios were 1.97× input tokens, 2.00× output tokens, 1.68× elapsed time, and 1.44× tool calls. Cost is reported separately and did not compensate for correctness or safety regressions.

## Limitations

- The fixtures are synthetic and cover ten bounded review situations.
- Activation used a precommitted behavioral inference because the client exposed no reliable runtime skill event.
- The blinded adjudicator was the primary model operated by the maintainer, not an independent evaluator.
- `YNM-VAL-001` remains MAYBE.
