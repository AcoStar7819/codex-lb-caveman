## Purpose

Reduce model-visible context and answer verbosity for opted-in keys without requiring changes to client tools or deployment topology.

## ADDED Requirements

### Requirement: Opt-in request projection
The proxy SHALL apply concise-answer guidance to inference requests authenticated by a Caveman-enabled key across HTTP and WebSocket transports. Disabled and unauthenticated requests MUST remain unchanged by Caveman. Guidance MUST preserve requested language, correctness, executable code and structured-output contracts.

#### Scenario: Enabled streaming turn
- **WHEN** an enabled key submits an inference turn
- **THEN** the upstream request contains concise-answer guidance once
- **AND** responses retain their existing streaming protocol

#### Scenario: Disabled key
- **WHEN** a disabled key submits a request
- **THEN** Caveman performs no transformation or engine invocation

### Requirement: Reversible JSON context compression
The proxy SHALL use Caveman to encode eligible uniform JSON arrays in tool results as TOON only when the encoded representation is smaller and decodes to the same typed values. It MUST preserve other context, tool arguments, tool schemas and caller-owned history. Compression failure MUST retain the original result.

#### Scenario: Repeated JSON fields
- **WHEN** a tool result contains a sufficiently large uniform JSON array
- **THEN** Caveman encodes it into a smaller reversible representation before upstream dispatch

#### Scenario: Unsupported or failed compression
- **WHEN** input is irregular, malformed, too large, or the engine fails
- **THEN** the original tool result is sent

### Requirement: Managed single-container execution
The Docker image SHALL include a pinned Caveman engine. The application MUST bound engine execution time and concurrency, reap its child processes on success, failure and cancellation, and require no additional container, public port or cloud account. Content and credentials MUST NOT appear in engine failure logs.

#### Scenario: Cancellation
- **WHEN** a request is cancelled during compression
- **THEN** its engine process is terminated and awaited
- **AND** cancellation propagates
