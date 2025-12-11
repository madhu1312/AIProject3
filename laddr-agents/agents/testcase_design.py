"""
Test Case Designer Agent - Agent 3 of 5

This agent designs test cases from user stories and acceptance criteria.
JIRA Ticket: SCRUM-74
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from laddr import tool


@tool(name="design_test_cases", description="Design test cases from user stories")
def design_test_cases(user_stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Design comprehensive test cases from user stories."""
    test_cases = []
    tc_id = 1
    
    for story in user_stories:
        story_id = story.get("id", "")
        
        # Create positive test case
        test_cases.append({
            "id": f"TC-{tc_id:03d}",
            "name": f"Verify {story_id} - Happy Path",
            "description": f"Verify successful execution of {story.get('story', '')}",
            "story_id": story_id,
            "type": "positive",
            "preconditions": ["User is logged in", "System is in ready state"],
            "steps": [
                {"step": 1, "action": "Navigate to the feature", "expected": "Feature page loads"},
                {"step": 2, "action": "Perform the main action", "expected": "Action completes successfully"},
                {"step": 3, "action": "Verify the result", "expected": "Expected outcome is achieved"}
            ],
            "expected_result": "Feature works as specified",
            "priority": story.get("priority", "medium")
        })
        tc_id += 1
        
        # Create negative test case
        test_cases.append({
            "id": f"TC-{tc_id:03d}",
            "name": f"Verify {story_id} - Error Handling",
            "description": f"Verify error handling for {story.get('story', '')}",
            "story_id": story_id,
            "type": "negative",
            "preconditions": ["User is logged in"],
            "steps": [
                {"step": 1, "action": "Attempt action with invalid input", "expected": "Error is displayed"},
                {"step": 2, "action": "Verify error message", "expected": "Message is user-friendly"}
            ],
            "expected_result": "Errors are handled gracefully",
            "priority": "medium"
        })
        tc_id += 1
        
        # Create edge case test
        test_cases.append({
            "id": f"TC-{tc_id:03d}",
            "name": f"Verify {story_id} - Edge Cases",
            "description": f"Verify edge cases for {story.get('story', '')}",
            "story_id": story_id,
            "type": "edge_case",
            "preconditions": ["System is in specific state"],
            "steps": [
                {"step": 1, "action": "Test boundary conditions", "expected": "System handles correctly"}
            ],
            "expected_result": "Edge cases are handled",
            "priority": "low"
        })
        tc_id += 1
    
    return test_cases


@tool(name="add_test_data", description="Add test data requirements to test cases")
def add_test_data(test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add test data requirements to each test case."""
    for tc in test_cases:
        tc["test_data"] = {
            "required_data": ["Valid user credentials", "Test environment access"],
            "data_setup": "Use standard test data set",
            "cleanup": "Reset to initial state after test"
        }
        tc["automation_candidate"] = tc.get("type") in ["positive", "negative"]
    
    return test_cases


# Export tools for pipeline
__all__ = ["design_test_cases", "add_test_data"]
