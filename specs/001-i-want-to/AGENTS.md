# Agent Development Guidelines: Multi-Agent Startup Evaluation System

## Overview
This document provides guidelines for developing and integrating agents in the startup evaluation system. All agents follow the Google ADK framework and operate within Docker containers. The ADK provides built-in FastAPI endpoints for workflow execution and API access.

**Key Resources**:
- ADK Documentation: https://google.github.io/adk-docs/
- API Reference: https://google.github.io/adk-docs/api-reference/python/index.html
- Agent Configuration: https://google.github.io/adk-docs/api-reference/agentconfig/
- Tutorials: https://google.github.io/adk-docs/tutorials/

When implementing agents, always consult the official ADK documentation first to ensure proper usage of the framework.

## Agent Types

### Data Processing Agents
- **PDF Processor**: Extracts text and metadata from PDF documents
- **Audio Transcriber**: Converts audio interviews to text transcripts
- **Deck Analyzer**: Processes presentation slides for key content
- **Email Parser**: Extracts insights from email communications

### Analysis Agents
- **Traction Analyzer**: Evaluates growth metrics and user acquisition
- **Team Assessor**: Analyzes founding team experience and capabilities
- **Market Researcher**: Assesses market size, competition, and opportunity
- **Financial Reviewer**: Analyzes financial projections and runway
- **Product Evaluator**: Reviews product features and market fit

### Synthesis Agents
- **Insight Aggregator**: Combines findings from analysis agents
- **Report Generator**: Creates final evaluation reports

## Agent Tools

Agents utilize LangChain-based tools for specialized functionality:

- **Search Tools**: Web search, data retrieval, market research
- **Analysis Tools**: Text analysis, sentiment analysis, data extraction
- **Report Tools**: Document generation, formatting, summarization

## Agent Interface

### Base Agent Class
```python
from google.adk import Agent

class BaseEvaluationAgent(Agent):
    def __init__(self, session_id: str, startup_id: str):
        super().__init__()
        self.session_id = session_id
        self.startup_id = startup_id
        self.output_file = f"sessions/{session_id}/outputs/agent_{self.name}_output.json"

    async def execute(self, inputs: dict) -> dict:
        # Agent-specific logic
        result = self.process(inputs)

        # Save output
        self.save_output(result)

        return result

    def save_output(self, result: dict):
        with open(self.output_file, 'w') as f:
            json.dump(result, f, indent=2)
```

### Input/Output Schema
All agents receive inputs from session state and previous agents:

```json
{
  "session_id": "uuid",
  "startup_id": "uuid",
  "data_sources": [...],
  "previous_outputs": {
    "agent_name": {...}
  }
}
```

Output format:
```json
{
  "agent_name": "pdf_processor",
  "status": "completed",
  "insights": [...],
  "confidence": 0.85,
  "processing_time": 45.2
}
```

## Development Workflow

### 1. Agent Creation
- Extend BaseEvaluationAgent
- Implement `process()` method
- Define input/output schemas
- Add comprehensive error handling

### 2. AI Integration
- Use flexible AI providers (Ollama/OpenRouter/HuggingFace)
- Implement fallback mechanisms
- Cache responses for consistency
- Handle rate limits and errors

### 3. Testing
- Unit tests for core logic
- Integration tests with mock AI responses
- End-to-end tests with sample data
- Performance benchmarks

### 4. Deployment
- Containerize with Docker
- Include model dependencies
- Configure resource limits
- Implement health checks

## Best Practices

### State Management
- Always read from and write to session state
- Use JSON for all persistent data
- Include timestamps and version info
- Handle concurrent access safely

### Error Handling
- Graceful degradation on AI failures
- Retry logic with exponential backoff
- Detailed error logging
- User-friendly error messages

### Performance
- Process data in batches when possible
- Cache expensive computations
- Monitor memory and CPU usage
- Optimize for single-startup processing

### Security
- Validate all inputs
- Sanitize data before AI processing
- Implement access controls
- Log security events

## Agent Registry

Maintain a registry of available agents:

```python
AGENT_REGISTRY = {
    "pdf_processor": PDFProcessorAgent,
    "audio_transcriber": AudioTranscriberAgent,
    "traction_analyzer": TractionAnalyzerAgent,
    # ...
}
```

## Orchestration

Use Google ADK workflows to define agent execution order:

```python
workflow = Workflow()
workflow.add_agent("pdf_processor")
workflow.add_agent("audio_transcriber", depends_on=["pdf_processor"])
workflow.add_agent("traction_analyzer", depends_on=["pdf_processor", "audio_transcriber"])
```

## Monitoring and Observability

- Log all agent activities
- Track performance metrics
- Monitor error rates
- Provide debugging interfaces

## Future Extensions

- Add new agent types for specialized analysis
- Implement agent learning from feedback
- Support custom evaluation criteria
- Integrate with external data sources