# Threat Model

## Risks

- unauthorized file access
- path traversal and unsafe file names
- malicious uploads
- prompt injection inside metadata
- report leakage via share links
- resource exhaustion from oversized files
- accidental training on customer data

## Controls

- signed object storage access
- file name sanitization
- MIME plus extension allowlist
- max upload size
- background job quotas
- metadata sanitization before LLM
- no customer data used for training without explicit consent
- report share links optional and revocable
