# Laddr Multi-Agent Test Generation Pipeline

A multi-agent AI pipeline using [Laddr](https://github.com/AgnetLabs/Laddr) framework to transform requirements documents into comprehensive test cases.

## 🚀 Pipeline Overview

```
Requirements → User Stories → Test Cases → Risk Assessment → Exports
```

This pipeline consists of 5 specialized agents:

| Agent | Role | Tools | Description |
|-------|------|-------|-------------|
| 1. Requirements Ingest | Parser | `parse_requirements`, `validate_requirements` | Parses raw requirements into structured format |
| 2. User Story Extract | Analyst | `extract_user_stories`, `generate_acceptance_criteria` | Extracts user stories with acceptance criteria |
| 3. Test Case Design | Designer | `design_test_cases`, `add_test_data` | Designs comprehensive test cases |
| 4. Risk Prioritize | Assessor | `assess_risk`, `create_execution_plan` | Prioritizes tests based on risk analysis |
| 5. Export Agent | Exporter | `export_to_zephyr_csv`, `export_to_jira_csv`, `generate_playwright_stubs`, `generate_tosca_xml` | Exports to multiple formats |

## 🔗 JIRA Tickets

| Ticket | Description |
|--------|-------------|
| SCRUM-71 | Epic - CMS React App Development |
| SCRUM-72 | Export Agent Implementation |
| SCRUM-73 | Risk Prioritization Agent |
| SCRUM-74 | Test Case Design Agent |
| SCRUM-75 | User Story Extraction Agent |
| SCRUM-76 | Requirements Ingestion Agent |
| SCRUM-77 | Playwright E2E Tests |
| SCRUM-78 | Unit Tests for Agents |
| SCRUM-79 | Functional Integration Tests |

## 🛠️ Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys in `.env` (optional for demo):
```bash
OPENAI_API_KEY=your-key-here
```

## 📋 Usage

### Python API

```python
from agents.requirements_ingest import parse_requirements, validate_requirements
from agents.userstory_extract import extract_user_stories, generate_acceptance_criteria
from agents.testcase_design import design_test_cases, add_test_data
from agents.risk_prioritize import assess_risk, create_execution_plan
from agents.export_agent import export_to_zephyr_csv, generate_playwright_stubs

# 1. Parse requirements
requirements_doc = """
## Functional Requirements
FR-001: User authentication with email/password
FR-002: Password reset functionality

## User Stories
US-001: As a user, I want to login so I can access my account
"""

parsed = parse_requirements(requirements_doc)
validation = validate_requirements(parsed)

# 2. Extract and enrich user stories
stories = extract_user_stories(parsed)
enriched_stories = generate_acceptance_criteria(stories)

# 3. Design test cases
test_cases = design_test_cases(enriched_stories)
enhanced_cases = add_test_data(test_cases)

# 4. Assess risk and create plan
risk_assessed = assess_risk(enhanced_cases)
execution_plan = create_execution_plan(risk_assessed)

# 5. Export to various formats
zephyr_csv = export_to_zephyr_csv(execution_plan)
playwright_code = generate_playwright_stubs(execution_plan)
```

### Run Demo
```bash
python pipeline_demo.py
```

### Run Single Agent
```bash
python main.py agent requirements_ingest '{"requirements_document": "..."}'
```

### Run Demo
```bash
python main.py demo
```

## 📤 Output Formats

The pipeline exports test cases to:

| Format | File Type | Use Case |
|--------|-----------|----------|
| **Zephyr CSV** | `.csv` | Zephyr Scale import |
| **JIRA CSV** | `.csv` | JIRA Test issue import |
| **Playwright** | `.ts` | TypeScript test stubs |
| **TOSCA XML** | `.xml` | Tricentis TOSCA import |

### Playwright Example Output

```typescript
import { test, expect } from '@playwright/test';

test('TC-001: Verify user login', async ({ page }) => {
  // Step 1: Navigate to login page
  // Step 2: Enter valid credentials
  // Step 3: Click login button
  // Expected: User is logged in successfully
});
```

## 🧪 Testing

### Run All Tests (87 tests)
```bash
python -m pytest tests/ -v
```

### Run Unit Tests Only (67 tests)
```bash
python -m pytest tests/ -v --ignore=tests/test_integration.py
```

### Run Integration Tests Only (20 tests)
```bash
python -m pytest tests/test_integration.py -v -s
```

### Test Coverage Report
```bash
python -m pytest tests/ --cov=agents --cov-report=html
```

## 📊 Test Suite Summary

| Category | Tests | Description |
|----------|-------|-------------|
| **Unit Tests** | 67 | Individual agent function tests |
| **Integration Tests** | 20 | End-to-end pipeline tests |
| **Total** | **87** | 100% pass rate |

### Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_requirements_ingest.py` | 12 | Parsing, validation |
| `test_userstory_extract.py` | 10 | Story extraction |
| `test_testcase_design.py` | 12 | Test case design |
| `test_risk_prioritize.py` | 14 | Risk assessment |
| `test_export_agent.py` | 19 | All export formats |
| `test_integration.py` | 20 | Full pipeline flows |

## 📈 Pipeline Metrics

Based on integration test results:

| Metric | Value |
|--------|-------|
| Test case ratio | 3.0 per user story |
| Automation candidates | 67% of test cases |
| Priority distribution | Critical: 33%, Medium: 67% |
| Large doc handling | 50 reqs → 150 test cases |

## 🏗️ Architecture

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
│          | TOSCA                    │
└─────────────────────────────────────┘
```

## 📁 Project Structure

```
laddr-agents/
├── agents/
│   ├── __init__.py
│   ├── requirements_ingest.py   # Agent 1
│   ├── userstory_extract.py     # Agent 2
│   ├── testcase_design.py       # Agent 3
│   ├── risk_prioritize.py       # Agent 4
│   └── export_agent.py          # Agent 5
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_requirements_ingest.py
│   ├── test_userstory_extract.py
│   ├── test_testcase_design.py
│   ├── test_risk_prioritize.py
│   ├── test_export_agent.py
│   └── test_integration.py
├── pipeline_demo.py
├── requirements.txt
├── laddr.yml
└── README.md
```

## 🤝 Contributing

1. Create a JIRA ticket for your change
2. Create a feature branch: `git checkout -b feature/SCRUM-XXX-description`
3. Write tests for new functionality
4. Ensure all tests pass: `python -m pytest tests/ -v`
5. Create a PR linking to the JIRA ticket

## 📄 License

MIT License
