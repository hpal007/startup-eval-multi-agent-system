# Data Model: Multi-Agent Startup Evaluation System

## Core Entities

### Startup
- **id**: Unique identifier (UUID)
- **name**: Startup name (string)
- **description**: Brief description (string, optional)
- **created_at**: Creation timestamp (datetime)
- **updated_at**: Last update timestamp (datetime)
- **status**: Processing status (enum: pending, processing, completed, failed)

### DataSource
- **id**: Unique identifier (UUID)
- **startup_id**: Foreign key to Startup
- **type**: Data type (enum: pdf, audio, deck, email)
- **file_path**: Path to uploaded file (string)
- **metadata**: Additional info (JSON: size, format, duration for audio)
- **processed_at**: Processing timestamp (datetime, optional)
- **status**: Processing status (enum: uploaded, processing, processed, failed)

### EvaluationInsight
- **id**: Unique identifier (UUID)
- **startup_id**: Foreign key to Startup
- **category**: Analysis category (enum: traction, team, market, financials, product)
- **content**: Extracted/summarized content (text)
- **confidence**: AI confidence score (float 0-1)
- **source_type**: Data source type that generated this (enum)
- **created_at**: Creation timestamp (datetime)

### Comparison
- **id**: Unique identifier (UUID)
- **startup_ids**: List of startup IDs being compared (JSON array)
- **criteria**: Comparison criteria (JSON: categories to compare)
- **results**: Comparison results (JSON: strengths/weaknesses per startup)
- **created_at**: Creation timestamp (datetime)

### Report
- **id**: Unique identifier (UUID)
- **startup_id**: Foreign key to Startup
- **summary**: Executive summary (text)
- **strengths**: List of key strengths (JSON array)
- **weaknesses**: List of key weaknesses (JSON array)
- **recommendation**: Investment recommendation (text)
- **score**: Overall score (float 0-10, optional)
- **generated_at**: Generation timestamp (datetime)

## Relationships

### Startup → DataSource (1:N)
- One startup can have multiple data sources
- Cascade delete: removing startup removes all associated data

### Startup → EvaluationInsight (1:N)
- One startup generates multiple insights across categories
- Insights aggregated from all data sources

### Startup → Report (1:N)
- One startup can have multiple reports (different versions)
- Latest report is the current evaluation

### DataSource → EvaluationInsight (1:N)
- One data source can generate multiple insights
- Links insights to their originating data

## Session State Structure

### Session Folder Layout
```
sessions/
├── {session_id}/
│   ├── inputs/
│   │   ├── startup_data.json
│   │   └── files/
│   │       ├── document.pdf
│   │       ├── interview.mp3
│   │       └── pitch_deck.pptx
│   ├── outputs/
│   │   ├── agent_{agent_name}_output.json
│   │   ├── evaluation_insights.json
│   │   └── final_report.json
│   └── metadata.json
```

### Runtime State Schema
```json
{
  "session_id": "uuid",
  "startup_id": "uuid",
  "status": "processing",
  "agents": {
    "pdf_processor": {
      "status": "completed",
      "output_file": "outputs/agent_pdf_processor_output.json"
    },
    "audio_transcriber": {
      "status": "running",
      "progress": 0.7
    }
  },
  "data_sources": [...],
  "insights": [...],
  "created_at": "2025-09-23T10:00:00Z",
  "updated_at": "2025-09-23T10:05:00Z"
}
```

## Data Flow

1. **Input**: Files uploaded to session inputs/files/
2. **Processing**: Agents read from inputs, write to outputs/
3. **Aggregation**: Insights collected from agent outputs
4. **Synthesis**: Final report generated from aggregated insights
5. **Persistence**: All data saved to database and session files

## Validation Rules

- Startup name required, unique per user
- Data source file must exist and be valid format
- Evaluation insights must have valid category and non-empty content
- Confidence scores must be between 0 and 1
- Reports must have summary and recommendation