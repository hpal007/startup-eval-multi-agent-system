# Contract: Get Evaluation Report

## Implementation
This contract is implemented in `main.py` using FastAPI with ADK result retrieval.

## Endpoint
```
GET /api/v1/evaluations/{evaluation_id}/report
```

## Purpose
Retrieve the final evaluation report once processing is complete.

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
  "status": "completed",
  "report": {
    "summary": "Strong traction with experienced team, but market competition is high",
    "strengths": [
      "Impressive user growth metrics",
      "Technical co-founder with relevant experience",
      "Clear product-market fit demonstrated"
    ],
    "weaknesses": [
      "Limited financial runway",
      "High market competition",
      "Unclear go-to-market strategy"
    ],
    "recommendation": "Consider seed investment with milestone-based funding",
    "score": 7.5,
    "insights": {
      "traction": "85% confidence - Strong user acquisition metrics",
      "team": "90% confidence - Experienced founding team",
      "market": "70% confidence - Growing market with competition",
      "financials": "60% confidence - Limited data provided",
      "product": "80% confidence - Innovative solution with early validation"
    }
  },
  "generated_at": "2025-09-23T10:05:00Z"
}
```

## Error Responses
- **404 Not Found**: Evaluation or report not found
- **409 Conflict**: Evaluation still in progress
- **500 Internal Server Error**: Report retrieval failed

## Validation
- Evaluation must be completed
- Report must exist in session outputs