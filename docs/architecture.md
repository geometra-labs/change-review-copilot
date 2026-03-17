# Architecture

## Overview

The system consists of:

- Next.js frontend
- FastAPI backend
- Postgres database
- object storage for uploaded files and report artifacts
- worker process for parsing, diffing, and impact analysis
- LLM explanation service used only after structured findings exist

## Pipeline

1. User uploads before/after model versions
2. Backend stores files and creates `ModelVersion` records
3. Worker parses each model into normalized assembly representation
4. Diff service matches parts across versions
5. Diff service labels direct changes
6. Impact service traverses graph and ranks affected parts
7. Explanation service converts structured findings into readable summary
8. Frontend renders report and viewer overlays

## Components

### Frontend

Responsibilities:

- auth
- projects
- uploads
- report rendering
- viewer shell
- error handling
- history

### API

Responsibilities:

- authentication
- CRUD for projects and versions
- job dispatch
- results retrieval
- validation
- authorization

### Worker

Responsibilities:

- file parsing
- metadata extraction
- comparison runs
- impact generation
- report artifact generation

### Database

Stores:

- users
- projects
- model_versions
- parts
- relationships
- comparison_runs
- part_matches
- impact_findings
- report_artifacts

### Object storage

Stores:

- raw file uploads
- normalized derived artifacts
- screenshots
- exported reports

## Failure handling

- invalid upload -> marked failed with error message
- parse timeout -> marked failed, retriable
- unmatched parts -> comparison may proceed with uncertainty
- explanation failure -> structured report still available
- viewer failure -> tabular report still available

## Design constraints

- LLM is never the source of truth for geometry findings
- all user-visible risks must link to evidence data
- systems should return partial results rather than all-or-nothing failure
