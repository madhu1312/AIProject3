# 🚀 AI-Powered SDLC Pipeline - Setup Guide

## Overview

This project includes a complete AI-powered Software Development Lifecycle (SDLC) pipeline that automates everything from requirement analysis to production deployment.

```
New Requirement → JIRA Ticket → AI Code Generation → Tests → Review → Deploy
```

---

## 📋 Prerequisites

- Node.js 18+
- Python 3.11+
- GitHub CLI (`gh`)
- Access to:
  - GitHub repository
  - JIRA/Atlassian account
  - Vercel account (for deployment)
  - OpenAI or Anthropic API key (for AI features)

---

## 🔐 Step 1: Configure GitHub Secrets

Run these commands to set up required secrets:

### Required Secrets

```powershell
# Navigate to project
cd cms-app/frontend

# JIRA Integration
gh secret set JIRA_EMAIL --repo madhu1312/AIProject3
# Enter your Atlassian email when prompted

gh secret set JIRA_API_TOKEN --repo madhu1312/AIProject3
# Enter your JIRA API token (get from https://id.atlassian.com/manage-profile/security/api-tokens)

# AI/LLM (choose one or both)
gh secret set OPENAI_API_KEY --repo madhu1312/AIProject3
# Enter your OpenAI API key

gh secret set ANTHROPIC_API_KEY --repo madhu1312/AIProject3
# Enter your Anthropic API key (optional)

# Vercel Deployment
gh secret set VERCEL_TOKEN --repo madhu1312/AIProject3
# Get from https://vercel.com/account/tokens

gh secret set VERCEL_ORG_ID --repo madhu1312/AIProject3
# Find in .vercel/project.json after running `vercel link`

gh secret set VERCEL_PROJECT_ID --repo madhu1312/AIProject3
# Find in .vercel/project.json after running `vercel link`
```

### Optional Secrets

```powershell
# Slack Notifications
gh secret set SLACK_WEBHOOK_URL --repo madhu1312/AIProject3
# Get from Slack App settings → Incoming Webhooks
```

### Verify Secrets

```powershell
gh secret list --repo madhu1312/AIProject3
```

---

## 🌍 Step 2: Configure GitHub Environments

Create environments for deployment protection:

```powershell
# Create environments via GitHub UI or API
# Go to: https://github.com/madhu1312/AIProject3/settings/environments

# Create these environments:
# 1. staging - No protection rules
# 2. production - Required reviewers
# 3. review - Required reviewers (for ai_assist mode)
```

### Environment Settings:

| Environment | Protection Rules | Purpose |
|-------------|-----------------|---------|
| `staging` | None | Auto-deploy previews |
| `production` | Required reviewers | Production deployment |
| `review` | Required reviewers | Human approval gate for AI code |

---

## 🔗 Step 3: Link Vercel Project

```powershell
# Install Vercel CLI
npm i -g vercel

# Link project (run in frontend directory)
cd frontend
vercel link

# This creates .vercel/project.json with orgId and projectId
# Use these values for VERCEL_ORG_ID and VERCEL_PROJECT_ID secrets
```

---

## 🎮 Step 4: Using the Pipeline

### Option A: Full AI Automation (`ai_full`)

1. Create JIRA ticket with requirements
2. Go to **GitHub → Actions → "AI-Powered SDLC Pipeline"**
3. Click **"Run workflow"**
4. Enter:
   - JIRA ticket: `SCRUM-XX`
   - Mode: `ai_full`
   - Environment: `staging` or `production`
5. Pipeline automatically:
   - Fetches JIRA requirements
   - Generates code (React components, services)
   - Generates tests
   - Reviews code
   - Deploys to target environment

### Option B: AI with Human Review (`ai_assist`)

Same as above, but:
- Mode: `ai_assist`
- Pipeline creates a **Pull Request** with AI-generated code
- **You review** the PR
- **Approve** to continue deployment

### Option C: Manual Code, Automated CI/CD (`manual`)

1. Write code yourself
2. Push to branch
3. Pipeline runs:
   - Lint & type check
   - Unit tests
   - E2E tests
   - Build
   - Deploy

---

## 📁 Pipeline Files

```
cms-app/
├── frontend/
│   ├── .github/workflows/
│   │   ├── ai-sdlc-pipeline.yml    # Full AI pipeline
│   │   └── full-sdlc-pipeline.yml  # CI/CD only
│   ├── Dockerfile                   # Docker build
│   ├── nginx.conf                   # Production server
│   └── .env.example                 # Environment template
│
└── laddr-agents/
    ├── run_pipeline.py              # CLI entry point
    ├── requirements.txt             # Python dependencies
    └── agents/
        ├── requirements_agent.py    # Analyzes JIRA tickets
        ├── code_generator_agent.py  # Generates code
        ├── test_generator_agent.py  # Generates tests
        └── code_reviewer_agent.py   # Reviews code
```

---

## 🧪 Local Testing

### Run AI Agents Locally

```powershell
cd cms-app/laddr-agents

# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:JIRA_EMAIL = "your-email@example.com"
$env:JIRA_API_TOKEN = "your-token"
$env:OPENAI_API_KEY = "your-key"

# Run full pipeline
python run_pipeline.py --phase all --ticket SCRUM-85 --description "Add new feature"

# Run individual phases
python run_pipeline.py --phase requirements --ticket SCRUM-85
python run_pipeline.py --phase code_generation --ticket SCRUM-85 --description "Add button"
```

### Run Frontend Locally

```powershell
cd cms-app/frontend

# Install dependencies
npm install

# Development server
npm run dev

# Run tests
npm test
npm run test:e2e

# Build
npm run build
```

---

## 🔍 Troubleshooting

### Pipeline fails at JIRA step
- Verify `JIRA_EMAIL` and `JIRA_API_TOKEN` secrets are set
- Check JIRA ticket key format (e.g., `SCRUM-85`)
- Ensure token has read permissions

### AI code generation fails
- Verify `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set
- Check API key has sufficient credits
- Review agent logs in GitHub Actions

### Deployment fails
- Verify Vercel secrets are configured
- Run `vercel link` locally first
- Check Vercel dashboard for errors

### Tests fail
- Run tests locally first: `npm test`
- Check if Playwright is installed: `npx playwright install`

---

## 📊 JIRA Integration

### Supported Transitions
The pipeline automatically updates JIRA ticket status:
- **Start**: Ticket → "In Progress"
- **Complete**: Ticket → "Done"

### JIRA URL
```
https://mstik5726.atlassian.net
```

### Project Key
```
SCRUM
```

---

## 🏷️ Available Epics

| Epic | Name | Use For |
|------|------|---------|
| SCRUM-14 | Platform Foundations | Infrastructure, setup, config |
| SCRUM-15 | AI Agent Orchestration | AI/ML features |
| SCRUM-16 | Backlog & Ticket Experience | JIRA integration |
| SCRUM-17 | Quality Automation | Testing, CI/CD |
| SCRUM-18 | AI Insights & Reporting | Analytics, dashboards |
| SCRUM-84 | CMS Feature Enhancements | UI components, features |

---

## 📞 Support

For issues with this pipeline, create a JIRA ticket under epic **SCRUM-17 (Quality Automation)**.

---

*Generated for SCRUM-85: CI/CD Pipeline Enhancement*
