# Requirements to Test Cases Pipeline

A multi-agent AI pipeline using [Laddr](https://github.com/AgnetLabs/Laddr) framework to transform requirements documents into comprehensive test cases.

## Pipeline Overview

This pipeline consists of 5 specialized agents:

| Agent | Role | Description |
|-------|------|-------------|
| 1. Requirements Ingest | Requirements Ingestion | Parses raw requirements into structured format |
| 2. User Story Extract | User Story Analyst | Extracts user stories with acceptance criteria |
| 3. Test Case Design | Test Case Designer | Designs comprehensive test cases |
| 4. Risk Prioritize | Risk Assessment | Prioritizes tests based on risk analysis |
| 5. Export Agent | Test Export | Exports to Zephyr, Jira, Playwright, Tosca |

## JIRA Tickets

- SCRUM-71: Epic - CMS React App
- SCRUM-72: Playwright Test Cases
- SCRUM-73: Agent 1 - Requirements Ingestion
- SCRUM-74: Agent 2 - User Story Extraction
- SCRUM-75: Agent 3 - Test Case Designer
- SCRUM-76: Agent 4 - Risk Prioritization
- SCRUM-77: Agent 5 - Export Agent

## Setup

1. Install dependencies:
```bash
pip install laddr python-dotenv
```

2. Configure API keys in `.env`:
```bash
OPENAI_API_KEY=your-key-here
```

3. Run the demo:
```bash
python main.py demo
```

## Usage

### Run Full Pipeline
```bash
python main.py run '{"requirements": "FR-001: User can login..."}'
```

### Run Single Agent
```bash
python main.py agent requirements_ingest '{"requirements_document": "..."}'
```

### Run Demo
```bash
python main.py demo
```

## Output Formats

The pipeline exports test cases to:

1. **Zephyr CSV** - For Zephyr Scale import
2. **Jira CSV** - For Jira Test issue import
3. **Playwright** - TypeScript test stubs
4. **Tosca** - XML test module definitions

## Architecture

```
┌─────────────────────┐
│ Requirements Doc    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 1. Requirements     │
│    Ingest Agent     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. User Story       │
│    Extract Agent    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Test Case        │
│    Design Agent     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Risk Prioritize  │
│    Agent            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. Export Agent     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Outputs: Zephyr | Jira | Playwright │
│          | Tosca                    │
└─────────────────────────────────────┘
```

## Configuration

See `laddr.yml` for project configuration and `.env` for environment variables.
