"""
Test Suite for Test Case Designer Agent (Agent 3)

Tests the design_test_cases and add_test_data tools.
JIRA Ticket: SCRUM-78
"""
import pytest
from agents.testcase_design import design_test_cases, add_test_data


class TestDesignTestCases:
    """Test cases for design_test_cases tool."""
    
    def test_design_from_single_story(self):
        """Test designing test cases from a single user story."""
        stories = [
            {
                "id": "US-001",
                "story": "As a user, I want to login",
                "acceptance_criteria": ["User can enter credentials"],
                "priority": "high"
            }
        ]
        result = design_test_cases(stories)
        
        # Should create 3 test cases per story (positive, negative, edge)
        assert len(result) == 3
        
        # Check test case types
        types = [tc["type"] for tc in result]
        assert "positive" in types
        assert "negative" in types
        assert "edge_case" in types
    
    def test_test_case_structure(self):
        """Test that test cases have correct structure."""
        stories = [
            {
                "id": "US-001",
                "story": "As a user, I want to login",
                "acceptance_criteria": [],
                "priority": "medium"
            }
        ]
        result = design_test_cases(stories)
        
        for tc in result:
            assert "id" in tc
            assert "name" in tc
            assert "description" in tc
            assert "story_id" in tc
            assert "type" in tc
            assert "preconditions" in tc
            assert "steps" in tc
            assert "expected_result" in tc
    
    def test_test_case_id_format(self):
        """Test that test case IDs are sequential."""
        stories = [
            {"id": "US-001", "story": "Story 1", "acceptance_criteria": [], "priority": "medium"},
            {"id": "US-002", "story": "Story 2", "acceptance_criteria": [], "priority": "medium"}
        ]
        result = design_test_cases(stories)
        
        # 6 test cases total (3 per story)
        assert len(result) == 6
        assert result[0]["id"] == "TC-001"
        assert result[5]["id"] == "TC-006"
    
    def test_positive_test_case_structure(self):
        """Test positive test case has correct properties."""
        stories = [
            {"id": "US-001", "story": "Login feature", "acceptance_criteria": [], "priority": "high"}
        ]
        result = design_test_cases(stories)
        
        positive = [tc for tc in result if tc["type"] == "positive"][0]
        
        assert "Happy Path" in positive["name"]
        assert positive["story_id"] == "US-001"
        assert len(positive["steps"]) >= 2
        assert len(positive["preconditions"]) >= 1
    
    def test_negative_test_case(self):
        """Test negative test case properties."""
        stories = [
            {"id": "US-001", "story": "Feature", "acceptance_criteria": [], "priority": "medium"}
        ]
        result = design_test_cases(stories)
        
        negative = [tc for tc in result if tc["type"] == "negative"][0]
        
        assert "Error Handling" in negative["name"]
        assert any("invalid" in step["action"].lower() for step in negative["steps"])
    
    def test_empty_stories(self):
        """Test with empty stories list."""
        result = design_test_cases([])
        assert len(result) == 0
    
    def test_steps_have_correct_structure(self):
        """Test that steps have action and expected fields."""
        stories = [
            {"id": "US-001", "story": "Test", "acceptance_criteria": [], "priority": "medium"}
        ]
        result = design_test_cases(stories)
        
        for tc in result:
            for step in tc["steps"]:
                assert "step" in step
                assert "action" in step
                assert "expected" in step


class TestAddTestData:
    """Test cases for add_test_data tool."""
    
    def test_add_test_data_to_cases(self):
        """Test adding test data to test cases."""
        test_cases = [
            {
                "id": "TC-001",
                "name": "Test Case 1",
                "type": "positive",
                "steps": []
            }
        ]
        result = add_test_data(test_cases)
        
        assert "test_data" in result[0]
        assert "required_data" in result[0]["test_data"]
        assert "data_setup" in result[0]["test_data"]
        assert "cleanup" in result[0]["test_data"]
    
    def test_automation_candidate_positive(self):
        """Test that positive tests are marked as automation candidates."""
        test_cases = [
            {"id": "TC-001", "type": "positive", "steps": []},
            {"id": "TC-002", "type": "negative", "steps": []}
        ]
        result = add_test_data(test_cases)
        
        assert result[0]["automation_candidate"] is True
        assert result[1]["automation_candidate"] is True
    
    def test_automation_candidate_edge_case(self):
        """Test that edge cases are not automation candidates."""
        test_cases = [
            {"id": "TC-001", "type": "edge_case", "steps": []}
        ]
        result = add_test_data(test_cases)
        
        assert result[0]["automation_candidate"] is False
    
    def test_preserves_existing_data(self):
        """Test that existing test case data is preserved."""
        test_cases = [
            {
                "id": "TC-001",
                "name": "My Test",
                "type": "positive",
                "steps": [{"step": 1, "action": "Do something"}],
                "custom_field": "custom_value"
            }
        ]
        result = add_test_data(test_cases)
        
        assert result[0]["name"] == "My Test"
        assert result[0]["custom_field"] == "custom_value"
        assert len(result[0]["steps"]) == 1


class TestIntegration:
    """Integration tests for the full design flow."""
    
    def test_full_design_pipeline(self):
        """Test complete design and data enhancement flow."""
        stories = [
            {
                "id": "US-001",
                "story": "As a user, I want to create articles",
                "acceptance_criteria": ["Article is saved", "User sees confirmation"],
                "priority": "high"
            },
            {
                "id": "US-002",
                "story": "As a user, I want to delete articles",
                "acceptance_criteria": ["Article is removed"],
                "priority": "medium"
            }
        ]
        
        test_cases = design_test_cases(stories)
        enhanced = add_test_data(test_cases)
        
        assert len(enhanced) == 6  # 3 per story
        
        for tc in enhanced:
            assert "test_data" in tc
            assert "automation_candidate" in tc
            assert tc["story_id"] in ["US-001", "US-002"]
