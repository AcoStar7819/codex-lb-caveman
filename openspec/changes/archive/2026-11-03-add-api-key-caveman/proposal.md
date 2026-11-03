# Proposal

## Why

Operators need opt-in token reduction per API key without changing their clients or single-container deployment.

## What Changes

- Add a default-off Caveman checkbox to API-key Limits and persist it through key management and authentication.
- Apply concise-output guidance and official Caveman lossless TOON encoding to eligible JSON tool results before inference, including streaming and WebSocket turns.
- Bundle the pinned Caveman Engine in Docker; Python owns bounded child-process execution and cleanup. No extra container, port, cloud account or client tool is required.
- Preserve originals on unsupported input or engine failure. Do not promise a fixed token or billing reduction.

## Capabilities

### New Capabilities

- `caveman-context`: Opt-in context projection and managed local engine execution.

### Modified Capabilities

- `api-keys`: Persist and expose the Caveman flag in the key Limits editor.

## Impact

API-key schema, migration, dashboard forms, proxy request preparation, Docker build and regression tests. Existing keys remain disabled. The Python SDK/middleware requires a separate recovery executor and cannot transparently compress streaming Codex traffic; use the official stateless Engine encoder through a Python adapter instead of adding an unused SDK dependency.
