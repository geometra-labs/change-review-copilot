# AGENTS.md

## Product

We are building a geometry-aware copilot for mechanical engineering teams.

## V1 goal

Given a CAD assembly and one design change, generate an impact report that tells the user:

- which parts are likely affected
- what interfaces may break
- where clearance/interference risk may appear
- what to inspect next

## V1 scope

- Onshape-first or upload-first workflow
- deterministic impact logic
- simple report UI

## Not in V1

- text-to-CAD
- generative design
- simulation
- FEA
- manufacturing planning
- multi-CAD support
- custom model training

## Stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Database: Postgres
- LLM use: explanation layer only
- Core logic: deterministic rules + graph-based logic

## Main entities

- Project
- Assembly
- Component
- ChangeEvent
- Warning
- ImpactReport

## Allowed change types

- dimension_changed
- part_replaced
- part_moved
- part_added_removed

## Warning levels

- high
- medium
- low

## Engineering rules

- keep scope narrow
- prefer simple deterministic logic
- do not overengineer
- keep API contracts stable
- keep diffs small
- ask before adding major dependencies
