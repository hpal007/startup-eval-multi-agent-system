
# Implementation Plan: Multi-Ag## Summary
Build a multi-agent system for evaluating startups using diverse data sources (PDFs, audio, decks, emails). Agents specialize in data types, collaborate via shared state, and produce comprehensive reports. Technical approach uses Python with Google ADK for orchestration, LangChain for agent tools, flexible AI providers (Ollama/OpenRouter/HuggingFace), FastAPI server in main.py, Docker containers, and session-based state management.t Startup Evaluation System

**Branch**: `001-i-want-to` | **Date**: 2025-09-23 | **Spec**: /Users/harish/dev/projects/se-system/specs/001-i-want-to/spec.md
**Input**: Feature specification from /Users/harish/dev/projects/se-system/specs/001-i-want-to/spec.md

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build a multi-agent system for evaluating startups using diverse data sources (PDFs, audio, decks, emails). Agents specialize in data types, collaborate via shared state, and produce comprehensive reports. Technical approach uses Python with Google ADK for orchestration, flexible AI providers (Ollama/OpenRouter/HuggingFace), Docker containers, FastAPI for APIs, and session-based state management.

## Technical Context
**Language/Version**: Python 3.12  
**Primary Dependencies**: google-adk, langchain, Ollama, OpenRouter, HuggingFace, FastAPI  
**Storage**: JSON files in session folders + runtime state  
**Testing**: pytest  
**Target Platform**: Docker containers on Linux  
**Project Type**: single (backend multi-agent system)  
**Performance Goals**: Complete evaluation in few minutes per startup  
**Constraints**: Single startup processing at a time, flexible AI provider selection, standard security practices  
**Scale/Scope**: Single concurrent startup evaluation

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Agent Specialization**: Agents will specialize by data type (PDF, audio, etc.) and analysis focus (traction, team, etc.)
- **Data Security and Privacy**: Standard encryption and access controls for sensitive data
- **Multi-Modal Input Processing**: Support PDF, audio, deck, email processing pipelines
- **Collaborative Intelligence**: Agents share outputs via session state and JSON files
- **Continuous Learning and Improvement**: Include feedback collection for model refinement
- **ADK Agent Implementation**: All agents implemented using Google ADK for consistency
- **Governance**: Follow semantic versioning for changes, require consensus for amendments

Status: PASS - No violations detected

**Post-Design Check**: PASS - Design aligns with all constitutional principles

## Project Structure

## Project Structure

### Documentation (this feature)
```
specs/001-i-want-to/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── AGENTS.md            # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   ├── upload_files.md
│   ├── start_evaluation.md
│   ├── get_evaluation_status.md
│   └── get_evaluation_report.md
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
agents/
├── base.py
├── pdf_processor.py
├── audio_transcriber.py
├── deck_analyzer.py
├── email_parser.py
├── traction_analyzer.py
├── team_assessor.py
├── market_researcher.py
├── financial_reviewer.py
├── product_evaluator.py
├── insight_aggregator.py
└── report_generator.py
workflows/
├── evaluation_workflow.py
└── api_endpoints.py  # ADK-provided API endpoints
core/
├── session_manager.py
├── ai_providers.py
└── config.py
utils/
├── file_processing.py
├── text_extraction.py
└── validation.py
models/
├── startup.py
├── evaluation.py
└── report.py

main.py          # FastAPI server from ADK integration
tools/           # LangChain-based tools
├── __init__.py
├── search_tools.py
├── analysis_tools.py
└── report_tools.py

tests/
├── unit/
├── integration/
└── e2e/

docker/
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

**Structure Decision**: [DEFAULT to Option 1 unless Technical Context indicates web/mobile app]

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Plan Phase 2: Task Generation Approach
*STOP: Ready for /tasks command*

**Input**: All Phase 1 artifacts (data-model.md, contracts/, quickstart.md, AGENTS.md)

**Approach**:
1. Load design documents and extract implementation components
2. Categorize tasks: Setup (Docker, dependencies), Core (agents, API), Integration (workflows, AI providers), Testing (unit, integration), Polish (docs, optimization)
3. Apply TDD: Tests before implementation, contract tests for APIs
4. Parallel tasks for independent components (different agents, test files)
5. Sequential dependencies: Setup → Core → Integration → Testing → Polish
6. Number tasks T001-T0XX with [P] for parallel execution

**Expected Categories**:
- Setup: Project structure, Docker, dependencies (T001-T010)
- Tools: LangChain-based tools for agents (T011-T020)
- Agents: Base classes and specialized agents using ADK (T021-T050)
- Workflows: ADK workflows and API integration (T051-T070)
- API: FastAPI endpoints in main.py (T071-T090)
- Integration: AI providers, session management (T091-T110)
- Testing: Unit, integration, contract tests (T111-T140)
- Documentation: Update README, API docs (T141-T150)

**Implementation Notes**:
- All agent implementations must follow Google ADK best practices
- Consult ADK documentation (https://google.github.io/adk-docs/) before implementing agents
- Use provided API references and tutorials for proper ADK usage

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
