"""
Requirements Ingestion Agent - Agent 1 of 5

This agent ingests requirements documents and parses them into structured format.
JIRA Ticket: SCRUM-76
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from laddr import tool


@tool(name="parse_requirements", description="Parse raw requirements text into structured sections")
def parse_requirements(raw_text: str) -> Dict[str, Any]:
    """Parse requirements document into structured format."""
    sections = {
        "functional": [],
        "non_functional": [],
        "user_stories": [],
        "constraints": [],
        "raw_items": []
    }
    
    current_section = "raw_items"
    lines = raw_text.strip().split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers
        lower = line.lower()
        if "functional requirement" in lower:
            current_section = "functional"
            continue
        elif "non-functional" in lower or "non functional" in lower:
            current_section = "non_functional"
            continue
        elif "user stor" in lower:
            current_section = "user_stories"
            continue
        elif "constraint" in lower:
            current_section = "constraints"
            continue
        
        # Parse requirement IDs
        req_match = re.match(r"^([A-Z]{2,}-\d+)[:\s]+(.+)$", line)
        if req_match:
            sections[current_section].append({
                "id": req_match.group(1),
                "text": req_match.group(2).strip(),
                "type": current_section
            })
        elif line.startswith("-") or line.startswith("*"):
            sections[current_section].append({
                "id": f"AUTO-{len(sections[current_section]) + 1}",
                "text": line[1:].strip(),
                "type": current_section
            })
    
    return sections


@tool(name="validate_requirements", description="Validate parsed requirements for completeness")
def validate_requirements(parsed_reqs: Dict[str, Any]) -> Dict[str, Any]:
    """Validate requirements for completeness and quality."""
    issues = []
    
    total = sum(len(v) for v in parsed_reqs.values() if isinstance(v, list))
    
    if total == 0:
        issues.append("No requirements found")
    if not parsed_reqs.get("functional"):
        issues.append("No functional requirements defined")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "total_requirements": total
    }


# Export tools for pipeline
__all__ = ["parse_requirements", "validate_requirements"]
