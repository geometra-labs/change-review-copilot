# Acceptance Criteria

## MVP is accepted when:

1. user can create a project
2. user can upload before/after files
3. parse succeeds on seeded demo fixtures
4. system produces changed-parts summary
5. system produces affected-parts ranking
6. every affected part has:
   - severity
   - risk_type
   - evidence
   - recommended_check
7. explanation is grounded in findings JSON only
8. report is readable without the 3D viewer
9. failures are explicit, not silent
10. at least 3 engineers say results are directionally useful

## Not acceptable if:

- model invents geometry findings not present in evidence
- system fails hard on missing optional data
- upload/parse state is ambiguous to the user
- `uncertain` cases are mislabeled as certain
- report requires the viewer to make sense
