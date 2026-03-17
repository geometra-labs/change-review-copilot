# API Contracts

## Auth

`POST /auth/register`  
`POST /auth/login`  
`GET /auth/me`

## Projects

`POST /projects`  
`GET /projects`  
`GET /projects/{project_id}`

## Model Versions

`POST /projects/{project_id}/model-versions`  
`GET /model-versions/{id}`  
`POST /model-versions/{id}/parse`  
`GET /model-versions/{id}/parts`

## Comparisons

`POST /projects/{project_id}/comparisons`  
`GET /comparisons/{comparison_id}`  
`GET /comparisons/{comparison_id}/diff`

## Impact

`POST /comparisons/{comparison_id}/impact`  
`GET /comparisons/{comparison_id}/findings`

## Explanation + Report

`POST /comparisons/{comparison_id}/explanation`  
`GET /comparisons/{comparison_id}/report`  
`POST /comparisons/{comparison_id}/export`

## Conventions

- all POST endpoints validate ownership
- all long-running jobs return `queued`, `running`, `completed`, or `failed`
- all failed jobs include code plus safe message
- all comparison and report endpoints return partial structured data if explanation fails
