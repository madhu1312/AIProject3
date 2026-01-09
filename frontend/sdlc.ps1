# ═══════════════════════════════════════════════════════════════════════════════
# SDLC Automation Script - Ticket to Deploy
# JIRA: SCRUM-85
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./sdlc.ps1 -Feature "Add new feature" -Epic "SCRUM-17"
#   ./sdlc.ps1 -TicketKey "SCRUM-85" -Action "deploy"
#
# ═══════════════════════════════════════════════════════════════════════════════

param(
    [Parameter(Mandatory=$false)]
    [string]$Feature,
    
    [Parameter(Mandatory=$false)]
    [string]$Epic,
    
    [Parameter(Mandatory=$false)]
    [string]$TicketKey,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("create", "develop", "test", "build", "deploy", "all")]
    [string]$Action = "all"
)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
$ErrorActionPreference = "Stop"
$JIRA_BASE_URL = "https://mstik5726.atlassian.net"

# ─────────────────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────────────────

function Write-Step {
    param([string]$Message, [string]$Icon = "▶")
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host " $Icon $Message" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ️  $Message" -ForegroundColor Yellow
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: Create JIRA Ticket
# ─────────────────────────────────────────────────────────────────────────────
function New-JiraTicket {
    param([string]$Summary, [string]$ParentEpic)
    
    Write-Step "Creating JIRA Ticket" "📋"
    
    # This would call the JIRA API to create a ticket
    # For now, we'll output instructions
    Write-Info "To create a JIRA ticket, use the following:"
    Write-Host "  Summary: $Summary"
    Write-Host "  Epic: $ParentEpic"
    Write-Host ""
    Write-Info "Or create via Copilot: 'Create JIRA ticket for: $Summary'"
    
    return $null
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: Create Feature Branch
# ─────────────────────────────────────────────────────────────────────────────
function New-FeatureBranch {
    param([string]$TicketKey)
    
    Write-Step "Creating Feature Branch" "🌿"
    
    if (-not $TicketKey) {
        Write-Error "No ticket key provided"
        return
    }
    
    $branchName = "feature/$TicketKey"
    
    try {
        git checkout develop
        git pull origin develop
        git checkout -b $branchName
        Write-Success "Created branch: $branchName"
    }
    catch {
        Write-Error "Failed to create branch: $_"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: Run Tests
# ─────────────────────────────────────────────────────────────────────────────
function Invoke-Tests {
    Write-Step "Running Tests" "🧪"
    
    try {
        Write-Info "Running lint..."
        npm run lint
        Write-Success "Lint passed"
        
        Write-Info "Running unit tests..."
        npm test
        Write-Success "Unit tests passed"
        
        Write-Info "Running E2E tests..."
        npm run test:e2e
        Write-Success "E2E tests passed"
    }
    catch {
        Write-Error "Tests failed: $_"
        exit 1
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 4: Build
# ─────────────────────────────────────────────────────────────────────────────
function Invoke-Build {
    Write-Step "Building Application" "🏗️"
    
    try {
        npm run build
        Write-Success "Build completed successfully"
    }
    catch {
        Write-Error "Build failed: $_"
        exit 1
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 5: Deploy
# ─────────────────────────────────────────────────────────────────────────────
function Invoke-Deploy {
    param([string]$Environment = "staging")
    
    Write-Step "Deploying to $Environment" "🚀"
    
    try {
        if ($Environment -eq "production") {
            Write-Info "Deploying to production..."
            npx vercel --prod
        }
        else {
            Write-Info "Deploying to staging..."
            npx vercel
        }
        Write-Success "Deployment completed"
    }
    catch {
        Write-Error "Deployment failed: $_"
        exit 1
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 6: Commit and Push
# ─────────────────────────────────────────────────────────────────────────────
function Send-Changes {
    param([string]$TicketKey, [string]$Message)
    
    Write-Step "Committing and Pushing Changes" "📤"
    
    try {
        git add .
        git commit -m "${TicketKey}: $Message"
        git push origin HEAD
        Write-Success "Changes pushed successfully"
        
        Write-Info "Create PR at: https://github.com/YOUR_REPO/compare"
    }
    catch {
        Write-Error "Failed to push: $_"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║            🚀 SDLC AUTOMATION - Ticket to Deploy 🚀              ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta

switch ($Action) {
    "create" {
        if ($Feature) {
            New-JiraTicket -Summary $Feature -ParentEpic $Epic
        }
        else {
            Write-Error "Feature description required for 'create' action"
        }
    }
    "develop" {
        New-FeatureBranch -TicketKey $TicketKey
    }
    "test" {
        Invoke-Tests
    }
    "build" {
        Invoke-Build
    }
    "deploy" {
        Invoke-Deploy -Environment "staging"
    }
    "all" {
        if ($Feature -and -not $TicketKey) {
            # Full flow: create ticket, branch, develop, test, build, deploy
            New-JiraTicket -Summary $Feature -ParentEpic $Epic
            Write-Info "Please create the JIRA ticket first, then run:"
            Write-Host "  ./sdlc.ps1 -TicketKey 'SCRUM-XX' -Action all"
        }
        elseif ($TicketKey) {
            New-FeatureBranch -TicketKey $TicketKey
            Invoke-Tests
            Invoke-Build
            # Deployment happens via GitHub Actions on push
            Write-Success "Ready for deployment! Push to trigger CI/CD pipeline."
        }
        else {
            Write-Error "Provide either -Feature or -TicketKey"
        }
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host " ✅ SDLC Script Completed" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
