"""
User Story Extraction Agent - Agent 2 of 5

This agent extracts user stories and acceptance criteria from parsed requirements.
JIRA Ticket: SCRUM-75
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from laddr import tool


@tool(name="extract_user_stories", description="Extract user stories from requirements")
def extract_user_stories(requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract and generate user stories from requirements."""
    stories = []
    story_id = 1
    
    # Process existing user stories
    for item in requirements.get("user_stories", []):
        stories.append({
            "id": f"US-{story_id:03d}",
            "original_id": item.get("id"),
            "story": item.get("text", ""),
            "acceptance_criteria": [],
            "source": "direct"
        })
        story_id += 1
    
    # Generate stories from functional requirements
    for item in requirements.get("functional", []):
        text = item.get("text", "")
        story = f"As a user, I want to {text.lower()}"
        stories.append({
            "id": f"US-{story_id:03d}",
            "original_id": item.get("id"),
            "story": story,
            "acceptance_criteria": [f"Given the system is ready, when user performs action, then {text}"],
            "source": "derived_from_fr"
        })
        story_id += 1
    
    return stories


@tool(name="generate_acceptance_criteria", description="Generate acceptance criteria for user stories")
def generate_acceptance_criteria(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate detailed acceptance criteria for each user story."""
    enhanced_stories = []
    
    for story in stories:
        criteria = story.get("acceptance_criteria", [])
        
        if not criteria:
            story_text = story.get("story", "")
            criteria = [
                f"GIVEN the user is authenticated",
                f"WHEN the user {story_text.split('want to')[-1] if 'want to' in story_text else 'performs the action'}",
                f"THEN the system should complete successfully",
                f"AND the user should receive confirmation"
            ]
        
        enhanced_stories.append({
            **story,
            "acceptance_criteria": criteria,
            "priority": "medium",
            "estimated_effort": "medium"
        })
    
    return enhanced_stories


# Export tools for pipeline
__all__ = ["extract_user_stories", "generate_acceptance_criteria"]
