## Summary

- What behavior changed
- Whether this affects YNM core contracts
- Why this change is backward compatible (or why it is not)

## Validation

- `python validation/validate_ynm.py`:
- `python validation/validate_release_integrity.py`:
- `python -m unittest discover -s tests -v`:
- `python scripts/build_skill_package.py --output-dir dist --overwrite`:
- `skills-ref validate dist/ynm`:
- `skills-ref read-properties dist/ynm`:

## Contract and compatibility impact

- Contract/schema files changed:
- Runtime package impact:
- Security/write-boundary impact:
- New or changed evidence claims:

## Notes

- PR is intentionally release-candidate only (not a tag/release)
- `YNM-VAL-001` status is unchanged if not resolved
