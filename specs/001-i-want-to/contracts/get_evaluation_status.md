# Contract: Get Evaluation Status

## Implementation
This contract is implemented in `main.py` using FastAPI with ADK session monitoring.

## Endpoint
```
GET /api/v1/evaluations/{evaluation_id}
```

## Purpose
Retrieve the current status and progress of an evaluation.

## Request
- **Method**: GET
- **Path Parameters**:
  - `evaluation_id` (string, UUID): ID of the evaluation

## Response
- **Status**: 200 OK
- **Content-Type**: application/json

```json
{
  "evaluation_id": "uuid",
  "startup_id": "uuid",
  "status": "processing",
  "progress": 0.65,
  "current_agent": "market_analyzer",
  "started_at": "2025-09-23T10:00:00Z",
  "estimated_completion": "2025-09-23T10:03:00Z",
  "agents_completed": [
    "pdf_processor",
    "audio_transcriber"
  ]
}
```

## Error Responses
- **404 Not Found**: Evaluation not found
- **500 Internal Server Error**: Status retrieval failed

## Validation
- Evaluation ID must exist
- Returns real-time status from session state