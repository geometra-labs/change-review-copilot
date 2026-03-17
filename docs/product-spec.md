# Change Review Copilot

## Product statement

Upload two versions of a mechanical assembly and receive a grounded impact report showing:

- what changed
- what parts are likely affected
- what risks to inspect
- why they were flagged
- what to inspect next

## Job to be done

"I changed one thing. Tell me what I may have broken and what I should inspect next."

## Primary user

Mechanical engineer or product design engineer working on small or medium assemblies.

## Ideal first customers

- robotics startups
- hardware startups
- prototyping shops
- design consultancies
- enclosure/fixture designers

## In scope

- upload before/after assembly files
- parse assembly structure
- extract parts and hierarchy
- build part relationships
- compare versions
- detect direct changes
- rank affected parts
- generate grounded report
- export/share report

## Out of scope

- text-to-CAD
- autonomous design edits
- live CAD plugin
- FEA
- tolerance stack-up analysis
- manufacturability optimization
- multi-CAD platform coverage
- team collaboration suite
- enterprise SSO/on-prem
- model training

## Success metric

Primary:

- engineers say the affected-parts list is useful and credible

Secondary:

- time saved in revision review
- issue detection before downstream review
- acceptance rate of suggested `inspect next` items

## Product principles

1. Geometry first, language second.
2. Every warning must have inspectable evidence.
3. The system may be uncertain, but must not bluff.
4. The first version is assistive, not autonomous.
