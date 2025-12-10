"""
Test Case Designer Agent - Agent 3 of 5

This agent designs test cases from user stories and acceptance criteria.

JIRA Ticket: SCRUM-75
"""
from __future__ import annotations

import asyncio
import os
import json
from typing import Any, Dict, List
from dotenv import load_dotenv
from laddr import Agent, WorkerRunner
from laddr.llms import openai
from laddr.core.tools import tool

load_dotenv()


@tool(
    name="design_test_cases",
    description="Design test cases from user stories",
    parameters={
        "type": "object",
        "properties": {
            "user_stories": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Array of user stories with acceptance criteria"
            },
            "test_type": {
                "type": "string",
                "enum": ["unit", "integration", "e2e", "all"],
                "default": "all"
            }
        },
        "required": ["user_stories"]
    }
)
def design_test_cases(user_stories: List[Dict], test_type: str = "all") -> Dict[str, Any]:
    """Design test cases from user stories."""
    test_cases = []
    tc_counter = 1
    
    for story in user_stories:
        story_id = story.get("id", "US-000")
        acceptance_criteria = story.get("acceptance_criteria", [])
        
        # Generate test cases for each acceptance criterion
        for ac_idx, ac in enumerate(acceptance_criteria):
            # Positive test case
            test_cases.append({
                "id": f"TC-{tc_counter:04d}",
                "title": f"Verify {story_id} - Positive Path {ac_idx + 1}",
                "description": f"Test positive scenario for {story_id}",
                "type": "positive",
                "priority": "high",
                "source_story": story_id,
                "preconditions": ["System is in ready state", "User is authenticated"],
                "test_steps": [
                    {"step": 1, "action": "Navigate to the feature", "expected": "Feature is accessible"},
                    {"step": 2, "action": "Perform the main action", "expected": "Action completes successfully"},
                    {"step": 3, "action": "Verify the result", "expected": "Expected outcome is achieved"}
                ],
                "expected_result": "Feature works as specified in acceptance criteria",
                "test_data": [],
                "tags": ["positive", story_id]
            })
            tc_counter += 1
            
            # Negative test case
            test_cases.append({
                "id": f"TC-{tc_counter:04d}",
                "title": f"Verify {story_id} - Negative Path {ac_idx + 1}",
                "description": f"Test negative scenario for {story_id}",
                "type": "negative",
                "priority": "medium",
                "source_story": story_id,
                "preconditions": ["System is in ready state"],
                "test_steps": [
                    {"step": 1, "action": "Attempt action with invalid input", "expected": "Error is displayed"},
                    {"step": 2, "action": "Verify error handling", "expected": "Appropriate error message shown"},
                    {"step": 3, "action": "Verify system state", "expected": "System remains stable"}
                ],
                "expected_result": "System handles invalid input gracefully",
                "test_data": [],
                "tags": ["negative", story_id]
            })
            tc_counter += 1
        
        # Edge case test
        test_cases.append({
            "id": f"TC-{tc_counter:04d}",
            "title": f"Verify {story_id} - Edge Cases",
            "description": f"Test boundary conditions for {story_id}",
            "type": "edge_case",
            "priority": "medium",
            "source_story": story_id,
            "preconditions": ["System is in ready state", "User is authenticated"],
            "test_steps": [
                {"step": 1, "action": "Test with minimum valid input", "expected": "Accepted"},
                {"step": 2, "action": "Test with maximum valid input", "expected": "Accepted"},
                {"step": 3, "action": "Test with boundary values", "expected": "Handled correctly"}
            ],
            "expected_result": "Edge cases handled properly",
            "test_data": [],
            "tags": ["edge_case", story_id]
        })
        tc_counter += 1
    
    return {
        "test_cases": test_cases,
        "total_test_cases": len(test_cases),
        "by_type": {
            "positive": len([tc for tc in test_cases if tc["type"] == "positive"]),
            "negative": len([tc for tc in test_cases if tc["type"] == "negative"]),
            "edge_case": len([tc for tc in test_cases if tc["type"] == "edge_case"])
        }
    }


@tool(
    name="map_tests_to_acceptance",
    description="Map test cases to acceptance criteria for coverage",
    parameters={
        "type": "object",
        "properties": {
            "test_cases": {"type": "array", "items": {"type": "object"}},
            "user_stories": {"type": "array", "items": {"type": "object"}}
        },
        "required": ["test_cases", "user_stories"]
    }
)
def map_tests_to_acceptance(test_cases: List[Dict], user_stories: List[Dict]) -> Dict[str, Any]:
    """Create test coverage mapping."""
    coverage_map = []
    
    for story in user_stories:
        story_id = story.get("id")
        related_tests = [tc for tc in test_cases if tc.get("source_story") == story_id]
        
        coverage_map.append({
            "story_id": story_id,
            "test_count": len(related_tests),
            "test_ids": [tc["id"] for tc in related_tests],
            "coverage_percentage": min(100, len(related_tests) * 20),  # Rough estimate
            "coverage_status": "complete" if len(related_tests) >= 3 else "partial"
        })
    
    return {
        "coverage_map": coverage_map,
        "overall_coverage": sum(c["coverage_percentage"] for c in coverage_map) / len(coverage_map) if coverage_map else 0,
        "stories_fully_covered": len([c for c in coverage_map if c["coverage_status"] == "complete"]),
        "stories_partially_covered": len([c for c in coverage_map if c["coverage_status"] == "partial"])
    }


@tool(
    name="generate_test_data",
    description="Generate test data for test cases",
    parameters={
        "type": "object",
        "properties": {
            "test_case_id": {"type": "string"},
            "data_type": {"type": "string", "enum": ["string", "number", "email", "date", "boolean"]}
        },
        "required": ["test_case_id", "data_type"]
    }
)
def generate_test_data(test_case_id: str, data_type: str) -> Dict[str, Any]:
    """Generate test data based on type."""
    test_data = {
        "string": {"valid": ["test", "sample text", "a" * 255], "invalid": ["", None, "a" * 1000]},
        "number": {"valid": [0, 1, 100, 999999], "invalid": [-1, None, "abc", 10000000]},
        "email": {"valid": ["test@test.com", "user.name@domain.org"], "invalid": ["invalid", "@test.com", "test@"]},
        "date": {"valid": ["2024-01-01", "2024-12-31"], "invalid": ["invalid-date", "2024-13-45", ""]},
        "boolean": {"valid": [True, False], "invalid": [None, "yes", 1, 0]}
    }
    
    return {
        "test_case_id": test_case_id,
        "data_type": data_type,
        "test_data": test_data.get(data_type, {"valid": [], "invalid": []})
    }


TOOLS = [design_test_cases, map_tests_to_acceptance, generate_test_data]

testcase_design = Agent(
    name="testcase_design",
    role="Test Case Designer",
    goal="Design comprehensive test cases from user stories and acceptance criteria",
    backstory="""You are a QA engineer who specializes in test case design. 
    You understand testing principles including positive/negative testing, 
    boundary value analysis, and equivalence partitioning. You create thorough
    test cases that ensure complete coverage of acceptance criteria.""",
    
    llm=openai(model=os.getenv("LLM_MODEL_TESTCASE_DESIGN", "gpt-4o-mini"), temperature=0.1),
    tools=TOOLS,
    
    max_retries=2,
    max_iterations=5,
    max_tool_calls=20,
    timeout=180,
    
    trace_enabled=True,
    trace_mask=[],
    
    instructions="""
    ## Your Role
    You are the third agent in a Requirements → Test Cases pipeline.
    You receive user stories from Agent 2 (userstory_extract).
    
    ## Your Task
    1. Use design_test_cases to create test cases from user stories
    2. Use map_tests_to_acceptance to verify coverage
    3. Use generate_test_data to create test data
    4. Return complete test cases with coverage mapping
    
    ## Output Format
    Return a JSON object with:
    {
        "status": "success",
        "test_cases": [...],
        "coverage_map": [...],
        "summary": "X test cases designed covering Y stories"
    }
    
    ## Test Case Requirements
    - Include positive and negative test cases
    - Cover edge cases and boundary conditions
    - Provide clear test steps with expected results
    - Include appropriate test data
    - Map to source user stories
    """
)


async def main():
    """Run this agent as a worker."""
    runner = WorkerRunner(agent=testcase_design)
    print("Starting testcase_design worker...")
    await runner.start()


if __name__ == "__main__":
    asyncio.run(main())
