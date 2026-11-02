## Context

See proposal.md. Both Responses routes use the shared include allowlist.

## Decisions

Extend the existing allowlist by one entry, as requested. Keep validation of unknown values intact; removing the allowlist would broaden the contract unnecessarily. Test model serialization and both HTTP routes with a stub upstream.

## Risks / Trade-offs

Upstream support remains upstream's responsibility. This change only removes the local rejection and preserves the requested include.
