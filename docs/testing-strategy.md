# Testing Strategy

## Test layers

### Unit tests

- bbox calculations
- part matching
- diff classification
- severity scoring
- impact propagation rules
- config validation

### Integration tests

- upload -> parse -> compare -> impact -> report
- parse failure handling
- comparison with unresolved parts
- explanation fallback behavior

### Contract tests

- API responses match schema
- frontend can render report payloads

### Golden fixtures

Store seeded before/after assemblies and expected:

- changed_parts
- top findings
- severity
- explanation inputs

### Smoke tests

- user signup/login
- project creation
- upload
- one comparison run
- one report fetch

## Edge-case tests

- empty assembly
- single-part assembly
- duplicate part names
- unmatched parts
- missing metadata
- invalid file type
- oversized upload
- job timeout
- explanation service unavailable
