## ADDED Requirements

### Requirement: Encrypted output include passthrough
Responses endpoints MUST accept `output.encrypted_content` in `include` and preserve it in the upstream request alongside other supported include values.

#### Scenario: Encrypted output requested through Responses routes
- **WHEN** a valid request to `/v1/responses` or `/backend-api/codex/responses` includes `["reasoning.encrypted_content", "output.encrypted_content"]`
- **THEN** the request passes include validation
- **AND** the upstream request retains both include values in order
