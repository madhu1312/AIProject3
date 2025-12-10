"""
Requirements Ingestion Agent - Agent 1 of 5

This agent ingests requirements documents (markdown, text, etc.) and 
parses them into a structured format for downstream agents.

JIRA Ticket: SCRUM-73
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

# Custom tools for requirements ingestion

@tool(
    name="parse_requirements",
    description="Parse raw requirements text into structured sections",
    parameters={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "Raw requirements document content"},
            "format": {"type": "string", "enum": ["markdown", "text", "bullet_list"], "default": "markdown"}
        },
        "required": ["content"]
    }
)
def parse_requirements(content: str, format: str = "markdown") -> Dict[str, Any]:
    """Parse requirements document into structured sections."""
    sections = []
    current_section = None
    
    lines = content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect headers (markdown style)
        if line.startswith('#'):
            level = len(re.match(r'^#+', line).group())
            title = line.lstrip('#').strip()
            current_section = {
                "level": level,
                "title": title,
                "content": [],
                "requirements": []
            }
            sections.append(current_section)
        elif current_section:
            # Detect requirement patterns (REQ-XXX, FR-XXX, NFR-XXX)
            req_match = re.match(r'^(REQ|FR|NFR|UC|US)-(\d+):?\s*(.*)', line, re.IGNORECASE)
            if req_match:
                current_section["requirements"].append({
                    "id": f"{req_match.group(1).upper()}-{req_match.group(2)}",
                    "text": req_match.group(3) or "",
                    "type": req_match.group(1).upper()
                })
            else:
                current_section["content"].append(line)
    
    return {
        "sections": sections,
        "total_sections": len(sections),
        "total_requirements": sum(len(s["requirements"]) for s in sections)
    }


@tool(
    name="extract_requirement_ids",
    description="Extract all requirement IDs from text",
    parameters={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "Text content to scan for requirement IDs"}
        },
        "required": ["content"]
    }
)
def extract_requirement_ids(content: str) -> Dict[str, List[str]]:
    """Extract requirement IDs from text."""
    patterns = {
        "functional": re.findall(r'FR-\d+', content, re.IGNORECASE),
        "non_functional": re.findall(r'NFR-\d+', content, re.IGNORECASE),
        "use_case": re.findall(r'UC-\d+', content, re.IGNORECASE),
        "user_story": re.findall(r'US-\d+', content, re.IGNORECASE),
        "general": re.findall(r'REQ-\d+', content, re.IGNORECASE)
    }
    
    # Remove duplicates
    for key in patterns:
        patterns[key] = list(set(patterns[key]))
    
    return {
        "requirement_ids": patterns,
        "total_count": sum(len(v) for v in patterns.values())
    }


TOOLS = [parse_requirements, extract_requirement_ids]

requirements_ingest = Agent(
    name="requirements_ingest",
    role="Requirements Ingestion Specialist",
    goal="Ingest and parse requirements documents into structured format for analysis",
    backstory="""You are a requirements analyst who specializes in reading and 
    structuring requirements documents. You can parse various formats including 
    markdown, plain text, and bullet lists. Your job is to identify requirements,
    extract their IDs, and organize them into a clean structure for downstream
    processing by other agents.""",
    
    llm=openai(model=os.getenv("LLM_MODEL_REQUIREMENTS_INGEST", "gpt-4o-mini"), temperature=0.0),
    tools=TOOLS,
    
    max_retries=2,
    max_iterations=5,
    max_tool_calls=10,
    timeout=120,
    
    trace_enabled=True,
    trace_mask=[],
    
    instructions="""
    ## Your Role
    You are the first agent in a Requirements → Test Cases pipeline.
    
    ## Your Task
    1. Receive raw requirements documents (markdown, text, etc.)
    2. Use the parse_requirements tool to structure the content
    3. Use extract_requirement_ids to identify all requirement IDs
    4. Return a structured JSON with all parsed requirements
    
    ## Output Format
    Return a JSON object with:
    {
        "status": "success",
        "parsed_requirements": [...],
        "requirement_ids": {...},
        "summary": "Brief description of what was parsed"
    }
    
    ## Important
    - Preserve all original requirement text
    - Identify requirement types (functional, non-functional, use case, etc.)
    - Group related requirements together
    - Flag any ambiguous or incomplete requirements
    """
)


async def main():
    """Run this agent as a worker."""
    runner = WorkerRunner(agent=requirements_ingest)
    print("Starting requirements_ingest worker...")
    await runner.start()


if __name__ == "__main__":
    asyncio.run(main())
