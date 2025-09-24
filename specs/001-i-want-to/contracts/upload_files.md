# Contract: Upload Files

## Implementation
This contract is implemented in `main.py` using FastAPI with ADK integration for file handling.

## Endpoint
```
POST /api/v1/startups/{startup_id}/files
```

## Purpose
Upload data source files (PDF, audio, deck, email) for a startup evaluation.

## Request
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Path Parameters**:
  - `startup_id` (string, UUID): ID of the startup

- **Form Data**:
  - `files` (file array): One or more files to upload
  - `types` (string array): Corresponding file types (pdf, audio, deck, email)

## Response
- **Status**: 201 Created
- **Content-Type**: application/json

```json
{
  "startup_id": "uuid",
  "uploaded_files": [
    {
      "file_id": "uuid",
      "filename": "pitch_deck.pdf",
      "type": "deck",
      "size_bytes": 2048576,
      "uploaded_at": "2025-09-23T10:00:00Z"
    }
  ],
  "message": "Files uploaded successfully"
}
```

## Error Responses
- **400 Bad Request**: Invalid file type or missing required fields
- **404 Not Found**: Startup not found
- **413 Payload Too Large**: File size exceeds limit
- **500 Internal Server Error**: Upload failed

## Validation
- File types must be supported (pdf, audio, deck, email)
- Maximum file size: 50MB per file
- Maximum 10 files per upload
- Files must be valid format (not corrupted)