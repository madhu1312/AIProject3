#!/usr/bin/env python
"""
Requirements Agent - CI/CD Pipeline Interface
JIRA: SCRUM-85

This script wraps the requirements ingestion agents for use in the AI SDLC pipeline.
It can be called from GitHub Actions to analyze JIRA ticket requirements.

Usage:
    python requirements_agent.py --input requirements.txt --output analysis.json
    python requirements_agent.py --ticket SCRUM-85 --jira-url https://site.atlassian.net
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from agents.requirements_ingest import parse_requirements, extract_requirement_ids
    from agents.userstory_extract import generate_user_stories, extract_acceptance_criteria
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    print("Warning: Laddr agents not fully available. Using fallback mode.")


def fetch_jira_ticket(ticket_key: str, jira_url: str) -> Dict[str, Any]:
    """Fetch ticket details from JIRA API."""
    import requests
    
    email = os.environ.get('JIRA_EMAIL')
    token = os.environ.get('JIRA_API_TOKEN')
    
    if not email or not token:
        return {"error": "JIRA credentials not configured"}
    
    response = requests.get(
        f"{jira_url}/rest/api/3/issue/{ticket_key}",
        auth=(email, token),
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        return {"error": f"Failed to fetch ticket: {response.status_code}"}
    
    data = response.json()
    
    # Extract relevant fields
    description = ""
    if data.get("fields", {}).get("description"):
        desc = data["fields"]["description"]
        if isinstance(desc, dict) and desc.get("content"):
            # Parse ADF format
            for block in desc.get("content", []):
                if block.get("content"):
                    for item in block["content"]:
                        if item.get("text"):
                            description += item["text"] + "\n"
        else:
            description = str(desc)
    
    return {
        "key": data.get("key"),
        "summary": data.get("fields", {}).get("summary", ""),
        "description": description,
        "issue_type": data.get("fields", {}).get("issuetype", {}).get("name", "Task"),
        "status": data.get("fields", {}).get("status", {}).get("name", ""),
        "priority": data.get("fields", {}).get("priority", {}).get("name", "Medium"),
        "labels": data.get("fields", {}).get("labels", []),
        "acceptance_criteria": extract_acceptance_criteria_from_description(description)
    }


def extract_acceptance_criteria_from_description(description: str) -> list:
    """Extract acceptance criteria from ticket description."""
    criteria = []
    
    # Look for acceptance criteria section
    lines = description.split('\n')
    in_ac_section = False
    
    for line in lines:
        line = line.strip()
        
        # Check for AC section header
        if any(header in line.lower() for header in ['acceptance criteria', 'ac:', 'done when']):
            in_ac_section = True
            continue
        
        # Check for next section
        if in_ac_section and line.startswith('#'):
            in_ac_section = False
            continue
        
        # Extract bullet points in AC section
        if in_ac_section and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
            criteria.append(line.lstrip('-*• ').strip())
    
    return criteria


def analyze_requirements(content: str, source: str = "input") -> Dict[str, Any]:
    """Analyze requirements from content."""
    result = {
        "source": source,
        "timestamp": datetime.now().isoformat(),
        "analysis": {}
    }
    
    if AGENTS_AVAILABLE:
        # Use Laddr agents
        parsed = parse_requirements(content)
        req_ids = extract_requirement_ids(content)
        
        result["analysis"]["parsed_sections"] = parsed.get("sections", [])
        result["analysis"]["requirement_ids"] = req_ids.get("requirement_ids", {})
        result["analysis"]["total_requirements"] = parsed.get("total_requirements", 0)
    else:
        # Fallback: basic parsing
        result["analysis"]["raw_content"] = content
        result["analysis"]["line_count"] = len(content.split('\n'))
        result["analysis"]["word_count"] = len(content.split())
    
    # Generate implementation plan
    result["implementation_plan"] = generate_implementation_plan(content)
    
    return result


def generate_implementation_plan(content: str) -> Dict[str, Any]:
    """Generate a basic implementation plan from requirements."""
    plan = {
        "files_to_create": [],
        "files_to_modify": [],
        "dependencies": [],
        "estimated_complexity": "medium",
        "suggested_approach": []
    }
    
    content_lower = content.lower()
    
    # Detect what kind of implementation is needed
    if any(term in content_lower for term in ['component', 'ui', 'button', 'form', 'page', 'modal']):
        plan["files_to_create"].append({
            "type": "component",
            "path": "src/components/NewComponent.tsx",
            "reason": "UI component detected in requirements"
        })
        plan["suggested_approach"].append("Create React component with TypeScript")
    
    if any(term in content_lower for term in ['api', 'endpoint', 'rest', 'fetch', 'service']):
        plan["files_to_create"].append({
            "type": "service",
            "path": "src/services/newService.ts",
            "reason": "API/service integration needed"
        })
        plan["suggested_approach"].append("Create service layer for API calls")
    
    if any(term in content_lower for term in ['test', 'verify', 'validate', 'check']):
        plan["files_to_create"].append({
            "type": "test",
            "path": "src/__tests__/feature.test.ts",
            "reason": "Testing requirements detected"
        })
        plan["suggested_approach"].append("Write unit and integration tests")
    
    if any(term in content_lower for term in ['database', 'collection', 'store', 'persist']):
        plan["files_to_modify"].append({
            "type": "schema",
            "path": "pocketbase/pb_schema.json",
            "reason": "Database changes may be needed"
        })
        plan["suggested_approach"].append("Update PocketBase schema")
    
    # Estimate complexity
    if len(plan["files_to_create"]) + len(plan["files_to_modify"]) > 5:
        plan["estimated_complexity"] = "high"
    elif len(plan["files_to_create"]) + len(plan["files_to_modify"]) <= 2:
        plan["estimated_complexity"] = "low"
    
    return plan


def main():
    parser = argparse.ArgumentParser(description="Requirements Analysis Agent")
    parser.add_argument("--input", "-i", help="Input file with requirements")
    parser.add_argument("--output", "-o", help="Output JSON file", default="/tmp/requirements_output.json")
    parser.add_argument("--ticket", "-t", help="JIRA ticket key")
    parser.add_argument("--jira-url", help="JIRA base URL", default=os.environ.get("JIRA_URL", "https://mstik5726.atlassian.net"))
    parser.add_argument("--summary", "-s", help="Ticket summary (if not fetching from JIRA)")
    parser.add_argument("--description", "-d", help="Ticket description (if not fetching from JIRA)")
    
    args = parser.parse_args()
    
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "ticket": args.ticket,
        "data": {}
    }
    
    try:
        # Get requirements content
        if args.ticket and not args.description:
            # Fetch from JIRA
            print(f"📋 Fetching ticket: {args.ticket}")
            ticket_data = fetch_jira_ticket(args.ticket, args.jira_url)
            
            if "error" in ticket_data:
                result["status"] = "error"
                result["error"] = ticket_data["error"]
            else:
                result["data"]["ticket"] = ticket_data
                content = f"{ticket_data['summary']}\n\n{ticket_data['description']}"
                result["data"]["analysis"] = analyze_requirements(content, args.ticket)
        
        elif args.input:
            # Read from file
            print(f"📄 Reading requirements from: {args.input}")
            with open(args.input, 'r') as f:
                content = f.read()
            result["data"]["analysis"] = analyze_requirements(content, args.input)
        
        elif args.summary or args.description:
            # Use provided content
            content = f"{args.summary or ''}\n\n{args.description or ''}"
            result["data"]["analysis"] = analyze_requirements(content, "cli-input")
        
        else:
            result["status"] = "error"
            result["error"] = "No input provided. Use --input, --ticket, or --summary/--description"
    
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Analysis saved to: {args.output}")
    print(json.dumps(result, indent=2))
    
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
