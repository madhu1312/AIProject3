# Content Management System (CMS) React App - Project Plan

## Project Overview
A React + TypeScript Content Management System for writing and publishing articles to the web.

## Plan of Action

### Phase 1: Project Setup & Infrastructure
1. **Create React App with TypeScript using Vite** (non-interactive mode)
   - Use `npm create vite@latest -- --template react-ts` 
   - Set up project structure

2. **Database Selection: PocketBase**
   - Latest lightweight CMS database
   - SQLite-based with real-time subscriptions
   - Built-in authentication and file storage
   - REST API out of the box
   - Perfect for CMS applications

3. **Git Repository Setup**
   - Clone/initialize repo: git@github.com:madhu1312/AIProject3.git

### Phase 2: CMS App Development
1. **Core Features:**
   - Index page listing all articles
   - Create document button
   - Article details: created, edited, published dates
   - Edit article functionality
   - Open in CMS view
   - View in browser option
   - Rich text editor for content

2. **Tech Stack:**
   - React 18 + TypeScript
   - Vite for build tooling
   - TailwindCSS for styling
   - TipTap or Slate for rich text editing
   - PocketBase for database
   - React Router for navigation

### Phase 3: Testing
1. **Playwright Test Cases:**
   - Test article creation
   - Test article editing
   - Test article listing
   - Test publish functionality
   - Test navigation

### Phase 4: Laddr Multi-Agent Framework
1. **Set up Laddr** from https://github.com/AgnetLabs/Laddr
2. **Create 5 Agents:**
   - **Agent 1: Requirements Ingestion Agent** - Ingests requirements documents
   - **Agent 2: User Story Extraction Agent** - Extracts user stories & acceptance criteria
   - **Agent 3: Test Case Designer Agent** - Designs test cases from stories
   - **Agent 4: Risk Prioritization Agent** - Prioritizes test cases by risk
   - **Agent 5: Export Agent** - Exports to Zephyr/Jira CSV + Playwright/Tosca stubs

### Phase 5: JIRA Integration & PR Management
1. **Create JIRA Tickets:**
   - CMS App Development
   - Playwright Test Creation
   - Each Agent Creation (5 tickets)

2. **Create PRs:**
   - PR for CMS app
   - PR for test cases
   - PRs for each agent

## Directory Structure
```
cms-app/
├── frontend/           # React + TypeScript app
├── pocketbase/         # PocketBase database
├── tests/              # Playwright tests
├── laddr-agents/       # Laddr multi-agent framework
│   ├── agent-requirements/
│   ├── agent-userstory/
│   ├── agent-testdesign/
│   ├── agent-prioritization/
│   └── agent-export/
└── docs/               # Documentation
```

## Current Status
- [ ] Phase 1: Project Setup
- [ ] Phase 2: CMS Development
- [ ] Phase 3: Testing
- [ ] Phase 4: Laddr Agents
- [ ] Phase 5: JIRA & PRs

## Next Steps
1. Check Vite help for non-interactive options
2. Create React app
3. Set up PocketBase
4. Implement CMS features

---
*Plan created: December 10, 2025*
*Last updated: December 10, 2025*
