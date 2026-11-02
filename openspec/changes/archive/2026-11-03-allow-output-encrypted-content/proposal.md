## Why

Responses requests containing `include: ["output.encrypted_content"]` currently fail local validation. Accept this value so the requested include reaches upstream.

## What Changes

- Add `output.encrypted_content` to the Responses include allowlist.
- Cover validation and forwarding through the Responses HTTP routes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: Accept and preserve encrypted output includes.

## Impact

One allowlist entry in `app/core/openai/requests.py`, focused tests, and OpenSpec documentation. No new settings or dependencies.
