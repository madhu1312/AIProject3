#!/usr/bin/env python
"""
Requirements to Test Cases Pipeline Runner

This is the main entry point for running the 5-agent pipeline:
1. Requirements Ingestion
2. User Story Extraction
3. Test Case Design
4. Risk Prioritization
5. Export (Zephyr/Jira/Playwright/Tosca)

Usage:
    python main.py run '{"requirements": "..."}'
    python main.py pipeline pipelines/requirements_pipeline.yml
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from laddr import AgentRunner, LaddrConfig

# Load environment variables
load_dotenv()


async def run_pipeline(requirements_content: str) -> dict:
    """
    Run the full pipeline with the given requirements content.
    
    Args:
        requirements_content: Raw requirements document text
    
    Returns:
        Final pipeline output with all exports
    """
    config = LaddrConfig()
    runner = AgentRunner(env_config=config)
    
    print("=" * 60)
    print("Requirements to Test Cases Pipeline")
    print("=" * 60)
    
    # Stage 1: Requirements Ingestion
    print("\n[1/5] Running Requirements Ingestion Agent...")
    stage1_result = await runner.run(
        inputs={"requirements_document": requirements_content},
        agent_name="requirements_ingest"
    )
    print(f"  → Parsed {stage1_result.get('result', {}).get('total_requirements', 'N/A')} requirements")
    
    # Stage 2: User Story Extraction
    print("\n[2/5] Running User Story Extraction Agent...")
    stage2_result = await runner.run(
        inputs={"parsed_requirements": stage1_result.get("result", {})},
        agent_name="userstory_extract"
    )
    print(f"  → Generated {stage2_result.get('result', {}).get('total_stories', 'N/A')} user stories")
    
    # Stage 3: Test Case Design
    print("\n[3/5] Running Test Case Design Agent...")
    stage3_result = await runner.run(
        inputs={"user_stories": stage2_result.get("result", {})},
        agent_name="testcase_design"
    )
    print(f"  → Designed {stage3_result.get('result', {}).get('total_test_cases', 'N/A')} test cases")
    
    # Stage 4: Risk Prioritization
    print("\n[4/5] Running Risk Prioritization Agent...")
    stage4_result = await runner.run(
        inputs={"test_cases": stage3_result.get("result", {})},
        agent_name="risk_prioritize"
    )
    print(f"  → Prioritized tests with execution plan")
    
    # Stage 5: Export
    print("\n[5/5] Running Export Agent...")
    stage5_result = await runner.run(
        inputs={"prioritized_tests": stage4_result.get("result", {})},
        agent_name="export_agent"
    )
    print(f"  → Exported to Zephyr, Jira, Playwright, and Tosca formats")
    
    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)
    
    return {
        "status": "success",
        "stages": {
            "requirements_ingestion": stage1_result,
            "user_story_extraction": stage2_result,
            "test_case_design": stage3_result,
            "risk_prioritization": stage4_result,
            "export": stage5_result
        }
    }


async def run_single_agent(agent_name: str, inputs: dict) -> dict:
    """Run a single agent with given inputs."""
    config = LaddrConfig()
    runner = AgentRunner(env_config=config)
    
    print(f"Running agent: {agent_name}")
    result = await runner.run(inputs=inputs, agent_name=agent_name)
    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py run '<json_input>'")
        print("  python main.py agent <agent_name> '<json_input>'")
        print("  python main.py demo")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "run":
        if len(sys.argv) < 3:
            print("Error: Please provide JSON input")
            sys.exit(1)
        
        try:
            inputs = json.loads(sys.argv[2])
            requirements = inputs.get("requirements", "")
            result = asyncio.run(run_pipeline(requirements))
            print("\nResult:")
            print(json.dumps(result, indent=2, default=str))
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)
    
    elif command == "agent":
        if len(sys.argv) < 4:
            print("Error: Please provide agent name and JSON input")
            sys.exit(1)
        
        agent_name = sys.argv[2]
        try:
            inputs = json.loads(sys.argv[3])
            result = asyncio.run(run_single_agent(agent_name, inputs))
            print("\nResult:")
            print(json.dumps(result, indent=2, default=str))
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)
    
    elif command == "demo":
        # Run with sample requirements
        sample_requirements = """
# CMS Application Requirements

## Functional Requirements

FR-001: The system shall allow users to create new articles with a title and content
FR-002: The system shall allow users to edit existing articles
FR-003: The system shall allow users to delete articles
FR-004: The system shall support saving articles as drafts
FR-005: The system shall allow publishing draft articles
FR-006: The system shall display a list of all articles

## Non-Functional Requirements

NFR-001: The system shall load the article list within 2 seconds
NFR-002: The system shall support concurrent access by 100 users
NFR-003: The system shall encrypt all data in transit

## User Stories

US-001: As an author, I want to create articles so that I can share content
US-002: As an editor, I want to review drafts so that I can ensure quality
"""
        result = asyncio.run(run_pipeline(sample_requirements))
        print("\nResult:")
        print(json.dumps(result, indent=2, default=str)[:5000] + "...")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
