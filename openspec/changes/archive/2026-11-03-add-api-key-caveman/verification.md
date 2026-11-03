# Verification

## Requirement coverage

| Contract | Evidence |
| --- | --- |
| Default-off key flag, persistence, update preservation and cache invalidation | API integration toggles the flag around real authenticated requests; migration upgrade/downgrade test covers historical rows |
| Limits UI | Create/edit submit tests, TypeScript check, production build, before/after Playwright screenshots |
| Opt-in HTTP, Chat, compact and WebSocket guidance | Route integration tests cover canonical/trailing-slash Responses paths, Chat conversion, external Chat source, compact and WebSocket frames |
| Reversible compression and untouched arguments/history | Real Engine encode/decode test plus invalid input, typed round-trip rejection and disabled-key tests |
| Managed process cleanup and failure fallback | Real sleeping child cancellation/deadline tests; engine-failure tests preserve original content |
| Single-container packaging | Dockerfile pinned source stage; native Windows build and Linux amd64 static cross-build succeed; no new runtime listener or setup variables |

## Checks

- API-key integration suite and focused service/repository/adapter/migration tests: 222 passed.
- Two WebSocket policy integration cases and 32 dashboard create/edit tests.
- Real Caveman Engine sample: 1490 input bytes to 523 output bytes, decoded values identical. This is a representation-size observation, not a billing or quality claim.
- Disposable database: `codex-lb-db upgrade head`, followed by `check`: `migration_policy=ok`, `schema_drift=none`.
- Ruff lint/format, Python type check for changed application modules, frontend lint/typecheck/build.
- All architecture, cancellation, timing, configuration-tier and migration-topology commands from `make lint` run directly (make is not installed on this Windows host).
- Strict validation of this change passes. All 68 main specs validate with pre-existing long-requirement warnings.
- Screenshots: `docs/screenshots/api-key-caveman-before.jpg` and `api-key-caveman-after.jpg`.

## Limitations

Docker daemon is unavailable on the development host: the complete container image has not been built or run. The Engine's pinned source was compiled for Linux amd64 independently. No Ubuntu VDS deployment or paid model request was made. Live model interpretation, tokenizer savings and billed savings require deployment-specific evaluation. The integration deliberately uses the official reversible Engine through Python, rather than the SDK's recovery-dependent middleware; rationale is in context.md.

No missing implementation requirements found. Deployment verification remains an explicit follow-up, not evidence claimed by local tests.
