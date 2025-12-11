"""
Test Suite for User Story Extraction Agent (Agent 2)

Tests the extract_user_stories and generate_acceptance_criteria tools.
JIRA Ticket: SCRUM-78
"""
import pytest
from agents.userstory_extract import extract_user_stories, generate_acceptance_criteria


class TestExtractUserStories:
    """Test cases for extract_user_stories tool."""
    
    def test_extract_direct_user_stories(self):
        """Test extracting existing user stories."""
        requirements = {
            "functional": [],
            "non_functional": [],
            "user_stories": [
                {"id": "US-001", "text": "As a user, I want to login"},
                {"id": "US-002", "text": "As an admin, I want to manage users"}
            ],
            "constraints": [],
            "raw_items": []
        }
        result = extract_user_stories(requirements)
        
        assert len(result) == 2
        assert result[0]["id"] == "US-001"
        assert result[0]["source"] == "direct"
        assert result[0]["original_id"] == "US-001"
    
    def test_derive_stories_from_functional(self):
        """Test deriving user stories from functional requirements."""
        requirements = {
            "functional": [
                {"id": "FR-001", "text": "Allow users to create articles"},
                {"id": "FR-002", "text": "Enable article editing"}
            ],
            "non_functional": [],
            "user_stories": [],
            "constraints": [],
            "raw_items": []
        }
        result = extract_user_stories(requirements)
        
        assert len(result) == 2
        assert result[0]["source"] == "derived_from_fr"
        assert result[0]["original_id"] == "FR-001"
        assert "As a user" in result[0]["story"]
    
    def test_extract_mixed_sources(self):
        """Test extracting from both user stories and functional requirements."""
        requirements = {
            "functional": [
                {"id": "FR-001", "text": "Allow login"}
            ],
            "non_functional": [],
            "user_stories": [
                {"id": "US-001", "text": "As a user, I want to register"}
            ],
            "constraints": [],
            "raw_items": []
        }
        result = extract_user_stories(requirements)
        
        assert len(result) == 2
        # First should be direct story
        assert result[0]["source"] == "direct"
        # Second should be derived
        assert result[1]["source"] == "derived_from_fr"
    
    def test_extract_empty_requirements(self):
        """Test with empty requirements."""
        requirements = {
            "functional": [],
            "non_functional": [],
            "user_stories": [],
            "constraints": [],
            "raw_items": []
        }
        result = extract_user_stories(requirements)
        
        assert len(result) == 0
    
    def test_story_id_format(self):
        """Test that generated story IDs follow correct format."""
        requirements = {
            "functional": [
                {"id": "FR-001", "text": "Feature 1"},
                {"id": "FR-002", "text": "Feature 2"},
                {"id": "FR-003", "text": "Feature 3"}
            ],
            "non_functional": [],
            "user_stories": [],
            "constraints": [],
            "raw_items": []
        }
        result = extract_user_stories(requirements)
        
        assert result[0]["id"] == "US-001"
        assert result[1]["id"] == "US-002"
        assert result[2]["id"] == "US-003"


class TestGenerateAcceptanceCriteria:
    """Test cases for generate_acceptance_criteria tool."""
    
    def test_generate_criteria_for_empty_stories(self):
        """Test generating criteria when stories have no acceptance criteria."""
        stories = [
            {
                "id": "US-001",
                "story": "As a user, I want to login",
                "acceptance_criteria": [],
                "source": "direct"
            }
        ]
        result = generate_acceptance_criteria(stories)
        
        assert len(result) == 1
        assert len(result[0]["acceptance_criteria"]) > 0
        assert "GIVEN" in result[0]["acceptance_criteria"][0]
    
    def test_preserve_existing_criteria(self):
        """Test that existing acceptance criteria are preserved."""
        stories = [
            {
                "id": "US-001",
                "story": "As a user, I want to login",
                "acceptance_criteria": ["Existing criterion 1", "Existing criterion 2"],
                "source": "direct"
            }
        ]
        result = generate_acceptance_criteria(stories)
        
        assert len(result[0]["acceptance_criteria"]) == 2
        assert result[0]["acceptance_criteria"][0] == "Existing criterion 1"
    
    def test_add_priority_and_effort(self):
        """Test that priority and effort are added."""
        stories = [
            {
                "id": "US-001",
                "story": "As a user, I want to login",
                "acceptance_criteria": [],
                "source": "direct"
            }
        ]
        result = generate_acceptance_criteria(stories)
        
        assert result[0]["priority"] == "medium"
        assert result[0]["estimated_effort"] == "medium"
    
    def test_multiple_stories(self):
        """Test generating criteria for multiple stories."""
        stories = [
            {"id": "US-001", "story": "Story 1", "acceptance_criteria": [], "source": "direct"},
            {"id": "US-002", "story": "Story 2", "acceptance_criteria": [], "source": "direct"},
            {"id": "US-003", "story": "Story 3", "acceptance_criteria": [], "source": "direct"}
        ]
        result = generate_acceptance_criteria(stories)
        
        assert len(result) == 3
        for story in result:
            assert len(story["acceptance_criteria"]) > 0
            assert "priority" in story


class TestIntegration:
    """Integration tests for the full extraction flow."""
    
    def test_full_extraction_pipeline(self):
        """Test complete extraction and enhancement flow."""
        requirements = {
            "functional": [
                {"id": "FR-001", "text": "Create articles"},
                {"id": "FR-002", "text": "Edit articles"}
            ],
            "non_functional": [],
            "user_stories": [
                {"id": "US-001", "text": "As an author, I want to publish articles"}
            ],
            "constraints": [],
            "raw_items": []
        }
        
        stories = extract_user_stories(requirements)
        enhanced = generate_acceptance_criteria(stories)
        
        assert len(enhanced) == 3
        for story in enhanced:
            assert "acceptance_criteria" in story
            assert len(story["acceptance_criteria"]) > 0
            assert "priority" in story
