# Design

## Context

See proposal.md. The user deploys to Ubuntu in one Docker container and requests application-owned Caveman execution. Existing routing includes HTTP, SSE, WebSocket and provider conversions.

## Goals / Non-Goals

Preserve routing, reservations and response protocols. No cloud connection, client plugin, lossy history pruning, image compression, reasoning-effort override or advertised percentage saving.

## Decisions

- Store `caveman_enabled` as a non-null default-false API-key column and carry it through immutable key data/cache and dashboard schemas.
- Integrate Python request preparation with official `caveman-engine toon encode/decode`. The SDK `Cave.compress` targets a connected service and blocks for up to 300 seconds; native middleware only compresses with an attested recovery executor. The standalone proxy's internal recovery loop does not support streaming and it has no WebSocket transport. Those alternatives cannot transparently meet this deployment/client contract.
- Use stateless, request-owned native child processes rather than a second persistent proxy listener. Bundle upstream Engine from a fixed commit in a Docker build stage. Each process starts only for eligible enabled-key traffic and is awaited/killed by Python. No operator action is needed in Docker.
- Restrict input to bounded uniform arrays of scalar-valued objects inside tool-result text. Check typed JSON round-trip equivalence and smaller output, including a TOON format marker. Preserve repeated prior context deterministically; do not persist customer content or call recovery tools.
- Add compact output guidance idempotently to instructions (Responses) or a system message (Chat). Preserve all client instructions and requested structured output.

## Risks / Trade-offs

- TOON can change model interpretation even when data is reversible: limit eligible shapes, retain every value, document exact-text limitations and test round trips.
- Short answers are model guidance, not a token cap. JSON compression and guidance overhead can affect cache and billing; provider usage remains authoritative.
- Native process overhead: cap input, number of segments, concurrent work and deadline; fail open on engine failure.
- Native binary packaging: use a pinned source revision and preserve upstream notices. Verify image build separately from Python tests.

## Migration Plan

Apply the normal additive migration on startup; historical rows are false. Disable the flag to restore original request preparation. Downgrade removes only the new column.
