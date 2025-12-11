# CMS React App with AI-Powered Test Generation

A full-stack Content Management System built with React + TypeScript, PocketBase backend, Playwright E2E tests, and a Laddr multi-agent pipeline for automated test case generation from requirements.

## 🚀 Project Overview

This project demonstrates a complete modern web application stack with AI-powered testing capabilities:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React 18 + TypeScript + Vite | CMS for article management |
| **Backend** | PocketBase | SQLite-based REST API + Auth |
| **E2E Tests** | Playwright | Browser automation testing |
| **AI Agents** | Laddr Framework | Requirements → Test cases pipeline |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CMS React App                            │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React)      │  Backend (PocketBase)                  │
│  ├── TipTap Editor     │  ├── SQLite Database                   │
│  ├── TailwindCSS       │  ├── REST API                          │
│  └── React Router      │  └── Real-time Subscriptions           │
├─────────────────────────────────────────────────────────────────┤
│  Testing Layer                                                   │
│  ├── Playwright E2E Tests (frontend/tests/)                     │
│  └── Laddr Multi-Agent Pipeline (laddr-agents/)                 │
│      ├── Requirements Ingestion                                  │
│      ├── User Story Extraction                                   │
│      ├── Test Case Design                                        │
│      ├── Risk Prioritization                                     │
│      └── Multi-Format Export (Zephyr, JIRA, Playwright, TOSCA)  │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
cms-app/
├── frontend/                 # React + TypeScript CMS
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── lib/              # PocketBase client
│   │   └── App.tsx           # Main app
│   ├── tests/                # Playwright E2E tests
│   └── playwright.config.ts
│
├── pocketbase/               # Backend database
│   ├── pocketbase.exe        # PocketBase binary
│   ├── pb_data/              # Database files
│   └── pb_migrations/        # Schema migrations
│
├── laddr-agents/             # AI Test Generation Pipeline
│   ├── agents/               # 5 Laddr agents
│   │   ├── requirements_ingest.py
│   │   ├── userstory_extract.py
│   │   ├── testcase_design.py
│   │   ├── risk_prioritize.py
│   │   └── export_agent.py
│   ├── tests/                # 87 unit + integration tests
│   └── README.md             # Detailed agent documentation
│
└── README.md                 # This file
```

## 🛠️ Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Git

### 1. Clone Repository

```bash
git clone git@github.com:madhu1312/AIProject3.git
cd AIProject3/cms-app
```

### 2. Start Backend (PocketBase)

```bash
cd pocketbase
./pocketbase serve
# Runs on http://127.0.0.1:8090
# Admin UI: http://127.0.0.1:8090/_/
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### 4. Run E2E Tests

```bash
cd frontend
npx playwright test
```

### 5. Run Agent Pipeline

```bash
cd laddr-agents
pip install -r requirements.txt
python pipeline_demo.py
```

## 📋 CMS Features

| Feature | Description |
|---------|-------------|
| 📝 **Create Articles** | Rich text editor with TipTap |
| ✏️ **Edit Articles** | Full CRUD operations |
| 🗑️ **Delete Articles** | With confirmation dialog |
| 📤 **Publish/Unpublish** | Toggle article visibility |
| 💾 **Auto-save** | Draft saving every 30 seconds |
| 📱 **Responsive** | Mobile-friendly design |

## 🧪 Testing

### Playwright E2E Tests

```bash
cd frontend
npx playwright test              # Run all tests
npx playwright test --ui         # Interactive UI mode
npx playwright show-report       # View test report
```

### Laddr Agent Tests

```bash
cd laddr-agents
python -m pytest tests/ -v       # Run all 87 tests
python -m pytest tests/test_integration.py -v -s  # Integration tests only
```

### Test Coverage

| Component | Tests | Pass Rate |
|-----------|-------|-----------|
| Agent Unit Tests | 67 | 100% |
| Agent Integration Tests | 20 | 100% |
| Playwright E2E Tests | 6 | - |
| **Total** | **93** | - |

## 🤖 AI Test Generation Pipeline

The Laddr multi-agent pipeline automatically generates test cases from requirements:

```
Requirements Doc → User Stories → Test Cases → Risk Assessment → Exports
```

### Pipeline Agents

| # | Agent | Input | Output |
|---|-------|-------|--------|
| 1 | Requirements Ingest | Raw requirements doc | Structured requirements |
| 2 | User Story Extract | Requirements | User stories + criteria |
| 3 | Test Case Design | User stories | Test cases with steps |
| 4 | Risk Prioritize | Test cases | Prioritized execution plan |
| 5 | Export Agent | Execution plan | Zephyr/JIRA/Playwright/TOSCA |

### Export Formats

- **Zephyr CSV** - Import to Zephyr Scale
- **JIRA CSV** - Create JIRA test issues
- **Playwright TypeScript** - Auto-generated test stubs
- **TOSCA XML** - Tricentis TOSCA test modules

### Usage Example

```python
from agents.requirements_ingest import parse_requirements
from agents.userstory_extract import extract_user_stories
from agents.testcase_design import design_test_cases
from agents.risk_prioritize import assess_risk, create_execution_plan
from agents.export_agent import generate_playwright_stubs

# Run full pipeline
parsed = parse_requirements(requirements_doc)
stories = extract_user_stories(parsed)
test_cases = design_test_cases(stories)
risk_assessed = assess_risk(test_cases)
plan = create_execution_plan(risk_assessed)
playwright_code = generate_playwright_stubs(plan)
```

## 🔗 JIRA Integration

This project follows JIRA-driven development:

| Ticket | Description | Status |
|--------|-------------|--------|
| SCRUM-71 | Epic: CMS React App Development | ✅ |
| SCRUM-72 | Export Agent Implementation | ✅ |
| SCRUM-73 | Risk Prioritization Agent | ✅ |
| SCRUM-74 | Test Case Design Agent | ✅ |
| SCRUM-75 | User Story Extraction Agent | ✅ |
| SCRUM-76 | Requirements Ingestion Agent | ✅ |
| SCRUM-77 | Playwright E2E Tests | ✅ |
| SCRUM-78 | Unit Tests for Agents | ✅ |
| SCRUM-79 | Functional Integration Tests | ✅ |

## 📈 Metrics

| Metric | Value |
|--------|-------|
| Test case generation ratio | 3.0 per user story |
| Automation candidates | 67% |
| Agent pipeline execution | < 1 second |
| Total test coverage | 87 tests passing |

## 🤝 Contributing

1. Create a JIRA ticket for your change
2. Create feature branch: `git checkout -b feature/SCRUM-XXX-description`
3. Write tests for new functionality
4. Ensure all tests pass
5. Create PR linking to JIRA ticket

## 📄 License

MIT License

---

**Built with** ❤️ using React, PocketBase, Playwright, and Laddr
