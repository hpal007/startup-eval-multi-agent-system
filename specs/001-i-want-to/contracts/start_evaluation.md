# Contract: Start Evaluation

## Implementation
This contract is implemented in `main.py` using FastAPI with ADK runner for workflow execution.

## Endpoint
```
POST /api/v1/startups/{startup_id}/evaluate
```

## Purpose
Initiate the multi-agent evaluation process for a startup with uploaded data sources.

## Request
- **Method**: POST
- **Content-Type**: application/json
- **Path Parameters**:
  - `startup_id` (string, UUID): ID of the startup

- **Body**:
```json
{
  "evaluation_type": "comprehensive",
  "priority": "normal"
}
```

## Response
- **Status**: 202 Accepted
- **Content-Type**: application/json

```json
{
  "evaluation_id": "uuid",
  "startup_id": "uuid",
  "status": "processing",
  "estimated_completion": "2025-09-23T10:05:00Z",
  "message": "Evaluation started successfully"
}
```

## Error Responses
- **400 Bad Request**: Invalid evaluation type or missing data sources
- **404 Not Found**: Startup not found
- **409 Conflict**: Evaluation already in progress
- **500 Internal Server Error**: Failed to start evaluation

## Validation
- Startup must have at least one uploaded data source
- Evaluation type must be valid (comprehensive, quick)
- No concurrent evaluations for same startup