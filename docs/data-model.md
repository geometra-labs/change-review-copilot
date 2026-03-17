# Data Model

## User

- id
- email
- password_hash
- created_at

## Project

- id
- owner_id
- name
- description
- created_at

## ModelVersion

- id
- project_id
- label
- source_type
- file_uri
- parse_status
- parse_error
- created_at

## Part

- id
- model_version_id
- part_key
- name
- parent_part_key
- transform_json
- bbox_json
- centroid_json
- volume_estimate
- geometry_signature
- metadata_json

## Relationship

- id
- model_version_id
- source_part_id
- target_part_id
- relationship_type
- score
- evidence_json

## ComparisonRun

- id
- project_id
- before_model_version_id
- after_model_version_id
- status
- summary_json
- created_at

## PartMatch

- id
- comparison_run_id
- before_part_id
- after_part_id
- match_confidence
- match_method
- change_type

## ImpactFinding

- id
- comparison_run_id
- part_id
- severity
- risk_type
- evidence_json
- reason_text
- recommended_check
- rank_score

## ReportArtifact

- id
- comparison_run_id
- artifact_type
- uri
- created_at
