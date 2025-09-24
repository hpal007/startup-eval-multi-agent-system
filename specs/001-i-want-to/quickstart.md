# Quickstart: Multi-Agent Startup Evaluation System

## Prerequisites
- Docker and Docker Compose installed
- Python 3.12+
- Git

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd se-system
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys for AI providers
   ```

3. **Build and run with Docker**:
   ```bash
   docker-compose up --build
   ```

The ADK will start the built-in FastAPI server on port 8000.

## Basic Usage

### 1. Create a Startup
```bash
curl -X POST http://localhost:8000/api/v1/startups \
  -H "Content-Type: application/json" \
  -d '{"name": "Example Startup", "description": "AI-powered analytics platform"}'
```

Response:
```json
{
  "startup_id": "uuid-here",
  "message": "Startup created successfully"
}
```

### 2. Upload Data Sources
```bash
curl -X POST http://localhost:8000/api/v1/startups/{startup_id}/files \
  -F "files=@pitch_deck.pdf" \
  -F "files=@founder_interview.mp3" \
  -F "types=deck" \
  -F "types=audio"
```

### 3. Start Evaluation
```bash
curl -X POST http://localhost:8000/api/v1/startups/{startup_id}/evaluate \
  -H "Content-Type: application/json" \
  -d '{"evaluation_type": "comprehensive"}'
```

### 4. Check Status
```bash
curl http://localhost:8000/api/v1/evaluations/{evaluation_id}
```

### 5. Get Report
```bash
curl http://localhost:8000/api/v1/evaluations/{evaluation_id}/report
```

## Configuration

### AI Providers
Configure in `.env`:
```
OPENROUTER_API_KEY=your_key
HUGGINGFACE_API_KEY=your_key
OLLAMA_BASE_URL=http://localhost:11434
```

### Docker Services
- **api**: FastAPI application (port 8000)
- **ollama**: Local LLM service (port 11434)
- **redis**: Session state cache (optional)

## Development

### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server (main.py with ADK integration)
python main.py
```

### Testing
```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/
```

## Troubleshooting

### Common Issues
- **AI model not responding**: Check API keys and network connectivity
- **File upload fails**: Verify file format and size limits
- **Evaluation stuck**: Check agent logs and session state

### Logs
```bash
# View API logs
docker-compose logs api

# View session logs
tail -f sessions/{session_id}/logs/agent_*.log
```

## Next Steps
- Upload sample data and run a test evaluation
- Review the generated report and insights
- Customize agent configurations for specific evaluation criteria