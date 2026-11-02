## Verification

Completeness: all three tasks complete; the delta requirement is synced to the main spec and the allowlist reference is updated.

Correctness: the new unit case and both HTTP route cases failed before the patch (unsupported include / HTTP 400) and passed afterward. The focused include suite passed all 6 tests, including rejection of unknown values.

Coherence: the implementation adds exactly the requested allowlist entry. No new settings or dependencies.

Validation: Ruff check and format passed across the repository; all five architecture checks passed; strict validation of this change passed; normal validation of all 67 main specs passed. Global strict validation reports pre-existing long-requirement and scenario warnings across 59 main specs. The full local-ci hook could not run because `make` is unavailable on this Windows host.

No implementation or scenario coverage issues found. The full CI environment limitation remains as described above.
