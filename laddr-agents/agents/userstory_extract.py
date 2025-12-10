"""
User Story Extraction Agent - Agent 2 of 5

This agent extracts user stories and acceptance criteria from 
parsed requirements.

JIRA Ticket: SCRUM-74
"""
from __future__ import annotations

import asyncio
import os
import json
import re
from typing import Any, Dict, List
from dotenv import load_dotenv
from laddr import Agent, WorkerRunner
from laddr.llms import openai
from laddr.core.tools import tool

load_dotenv()


@tool(
    name="generate_user_stories",
    description="Generate user stories from requirements",
    parameters={
        "type": "object",
        "properties": {
            "requirements": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Array of parsed requirement objects"
            }
        },
        "required": ["requirements"]
    }
)
def generate_user_stories(requirements: List[Dict]) -> Dict[str, Any]:
    """Generate user stories from requirements."""
    user_stories = []
    
    for idx, req in enumerate(requirements):
        req_id = req.get("id", f"REQ-{idx+1}")
        req_text = req.get("text", "")
        req_type = req.get("type", "GENERAL")
        
        # Generate user story format
        story = {
            "id": f"US-{idx+1:03d}",
            "source_requirement": req_id,
            "type": req_type,
            "story": f"As a user, I want to {req_text.lower()}, so that I can achieve the desired outcome",
            "acceptance_criteria": [],
            "priority": "Medium",
            "estimated_complexity": "Medium"
        }
        
        # Generate basic acceptance criteria
        story["acceptance_criteria"] = [
            f"Given the system is ready, when the user performs the action, then {req_text}",
            f"The feature should be accessible to authorized users",
            f"The system should provide appropriate feedback"
        ]
        
        user_stories.append(story)
    
    return {
        "user_stories": user_stories,
        "total_stories": len(user_stories)
    }


@tool(
    name="extract_acceptance_criteria",
    description="Extract and refine acceptance criteria from user stories",
    parameters={
        "type": "object",
        "properties": {
            "story_text": {"type": "string", "description": "User story text to analyze"},
            "context": {"type": "string", "description": "Additional context for criteria generation"}
        },
        "required": ["story_text"]
    }
)
def extract_acceptance_criteria(story_text: str, context: str = "") -> Dict[str, Any]:
    """Extract acceptance criteria from story text."""
    criteria = []
    
    # Parse Given/When/Then format if present
    gherkin_patterns = re.findall(
        r'(Given|When|Then|And|But)\s+(.+?)(?=(?:Given|When|Then|And|But|$))',
        story_text,
        re.IGNORECASE | re.DOTALL
    )
    
    if gherkin_patterns:
        scenario = {"steps": []}
        for keyword, text in gherkin_patterns:
            scenario["steps"].append({
                "keyword": keyword.capitalize(),
                "text": text.strip()
            })
        criteria.append({
            "type": "gherkin",
            "scenario": scenario
        })
    else:
        # Generate generic acceptance criteria
        criteria.append({
            "type": "checklist",
            "items": [
                "The functionality is implemented as specified",
                "The feature is accessible and usable",
                "Error handling is appropriate",
                "Performance meets requirements"
            ]
        })
    
    return {
        "acceptance_criteria": criteria,
        "source_story": story_text[:100] + "..." if len(story_text) > 100 else story_text
    }


@tool(
    name="link_stories_to_requirements",
    description="Create traceability links between stories and source requirements",
    parameters={
        "type": "object",
        "properties": {
            "user_stories": {"type": "array", "items": {"type": "object"}},
            "requirements": {"type": "array", "items": {"type": "object"}}
        },
        "required": ["user_stories", "requirements"]
    }
)
def link_stories_to_requirements(user_stories: List[Dict], requirements: List[Dict]) -> Dict[str, Any]:
    """Create traceability matrix between stories and requirements."""
    traceability = []
    
    for story in user_stories:
        link = {
            "story_id": story.get("id"),
            "requirement_id": story.get("source_requirement"),
            "coverage": "full",
            "notes": ""
        }
        traceability.append(link)
    
    return {
        "traceability_matrix": traceability,
        "total_links": len(traceability),
        "coverage_summary": {
            "fully_covered": len([t for t in traceability if t["coverage"] == "full"]),
            "partially_covered": len([t for t in traceability if t["coverage"] == "partial"]),
            "not_covered": 0
        }
    }


TOOLS = [generate_user_stories, extract_acceptance_criteria, link_stories_to_requirements]

userstory_extract = Agent(
    name="userstory_extract",
    role="User Story Analyst",
    goal="Extract user stories and acceptance criteria from requirements",
    backstory="""You are a business analyst who specializes in transforming 
    requirements into user stories with clear acceptance criteria. You understand
    the user story format (As a... I want... So that...) and can create detailed
    Gherkin-style acceptance criteria. You ensure traceability between stories
    and their source requirements.""",
    
    llm=openai(model=os.getenv("LLM_MODEL_USERSTORY_EXTRACT", "gpt-4o-mini"), temperature=0.2),
    tools=TOOLS,
    
    max_retries=2,
    max_iterations=5,
    max_tool_calls=15,
    timeout=120,
    
    trace_enabled=True,
    trace_mask=[],
    
    instructions="""
    ## Your Role
    You are the second agent in a Requirements → Test Cases pipeline.
    You receive parsed requirements from Agent 1 (requirements_ingest).
    
    ## Your Task
    1. Use generate_user_stories to create user stories from requirements
    2. Use extract_acceptance_criteria to refine the acceptance criteria
    3. Use link_stories_to_requirements to create traceability
    4. Return complete user stories with acceptance criteria
    
    ## Output Format
    Return a JSON object with:
    {
        "status": "success",
        "user_stories": [...],
        "traceability_matrix": [...],
        "summary": "X user stories generated from Y requirements"
    }
    
    ## User Story Format
    - As a [role], I want [feature], so that [benefit]
    - Include 3-5 acceptance criteria per story
    - Use Gherkin format where possible (Given/When/Then)
    - Maintain links to source requirements
    """
)


async def main():
    """Run this agent as a worker."""
    runner = WorkerRunner(agent=userstory_extract)
    print("Starting userstory_extract worker...")
    await runner.start()


if __name__ == "__main__":
    asyncio.run(main())
