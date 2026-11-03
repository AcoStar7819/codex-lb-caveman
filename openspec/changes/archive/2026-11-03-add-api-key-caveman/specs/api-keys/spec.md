## ADDED Requirements

### Requirement: Per-key Caveman setting
API-key create, update and read operations SHALL support a boolean `cavemanEnabled`. New and existing keys MUST default to false. Omitting the field on update MUST preserve its value. The Limits section of key creation and editing MUST display a checkbox labelled `Caveman (Less token usage)`. Updates MUST invalidate cached key policy.

#### Scenario: Enable and reload
- **WHEN** an operator enables Caveman and saves a key
- **THEN** subsequent reads and authenticated requests use the enabled policy

#### Scenario: Preserve and disable
- **WHEN** an enabled key is updated without the Caveman field
- **THEN** it remains enabled
- **AND** explicitly setting the field to false disables it
