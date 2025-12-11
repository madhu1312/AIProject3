"""
Test Suite for Risk Prioritization Agent (Agent 4)

Tests the assess_risk and create_execution_plan tools.
JIRA Ticket: SCRUM-78
"""
import pytest
from agents.risk_prioritize import assess_risk, create_execution_plan


class TestAssessRisk:
    """Test cases for assess_risk tool."""
    
    def test_assess_positive_test_risk(self):
        """Test risk assessment for positive test cases."""
        test_cases = [
            {
                "id": "TC-001",
                "type": "positive",
                "steps": [{"step": 1}, {"step": 2}, {"step": 3}]
            }
        ]
        result = assess_risk(test_cases)
        
        assert "risk_assessment" in result[0]
        assert "factors" in result[0]["risk_assessment"]
        assert "total_score" in result[0]["risk_assessment"]
        assert "priority" in result[0]
    
    def test_positive_tests_higher_priority(self):
        """Test that positive tests get higher priority."""
        test_cases = [
            {"id": "TC-001", "type": "positive", "steps": [{"step": 1}, {"step": 2}, {"step": 3}]},
            {"id": "TC-002", "type": "edge_case", "steps": [{"step": 1}]}
        ]
        result = assess_risk(test_cases)
        
        positive = result[0]
        edge = result[1]
        
        # Positive should have higher score
        assert positive["risk_assessment"]["total_score"] > edge["risk_assessment"]["total_score"]
    
    def test_complexity_affects_score(self):
        """Test that more steps increase complexity score."""
        test_cases = [
            {"id": "TC-001", "type": "negative", "steps": [{"step": 1}]},
            {"id": "TC-002", "type": "negative", "steps": [{"step": 1}, {"step": 2}, {"step": 3}]}
        ]
        result = assess_risk(test_cases)
        
        simple = result[0]["risk_assessment"]["factors"]["complexity"]
        complex_tc = result[1]["risk_assessment"]["factors"]["complexity"]
        
        assert complex_tc > simple
    
    def test_priority_levels(self):
        """Test that different priority levels are assigned."""
        test_cases = [
            {"id": "TC-001", "type": "positive", "steps": [{"step": 1}, {"step": 2}, {"step": 3}]},
            {"id": "TC-002", "type": "edge_case", "steps": [{"step": 1}]}
        ]
        result = assess_risk(test_cases)
        
        priorities = [tc["priority"] for tc in result]
        assert "critical" in priorities or "high" in priorities or "medium" in priorities
    
    def test_risk_factors_present(self):
        """Test that all risk factors are calculated."""
        test_cases = [
            {"id": "TC-001", "type": "positive", "steps": []}
        ]
        result = assess_risk(test_cases)
        
        factors = result[0]["risk_assessment"]["factors"]
        assert "business_impact" in factors
        assert "complexity" in factors
        assert "failure_probability" in factors
        assert "user_frequency" in factors
    
    def test_empty_test_cases(self):
        """Test with empty test cases list."""
        result = assess_risk([])
        assert len(result) == 0


class TestCreateExecutionPlan:
    """Test cases for create_execution_plan tool."""
    
    def test_create_plan_structure(self):
        """Test execution plan has correct structure."""
        test_cases = [
            {
                "id": "TC-001",
                "priority": "high",
                "risk_assessment": {"total_score": 8}
            },
            {
                "id": "TC-002",
                "priority": "medium",
                "risk_assessment": {"total_score": 5}
            }
        ]
        result = create_execution_plan(test_cases)
        
        assert "test_cases" in result
        assert "execution_order" in result
        assert "priority_breakdown" in result
        assert "total_tests" in result
        assert "recommended_first" in result
    
    def test_sorted_by_risk_score(self):
        """Test that test cases are sorted by risk score."""
        test_cases = [
            {"id": "TC-001", "priority": "low", "risk_assessment": {"total_score": 3}},
            {"id": "TC-002", "priority": "critical", "risk_assessment": {"total_score": 10}},
            {"id": "TC-003", "priority": "medium", "risk_assessment": {"total_score": 6}}
        ]
        result = create_execution_plan(test_cases)
        
        # First should be highest score
        assert result["test_cases"][0]["id"] == "TC-002"
        # Last should be lowest score
        assert result["test_cases"][2]["id"] == "TC-001"
    
    def test_execution_order(self):
        """Test execution order is correct."""
        test_cases = [
            {"id": "TC-001", "priority": "critical", "risk_assessment": {"total_score": 10}},
            {"id": "TC-002", "priority": "high", "risk_assessment": {"total_score": 8}},
            {"id": "TC-003", "priority": "medium", "risk_assessment": {"total_score": 5}},
            {"id": "TC-004", "priority": "low", "risk_assessment": {"total_score": 2}}
        ]
        result = create_execution_plan(test_cases)
        
        order = result["execution_order"]
        # Critical first
        assert order[0] == "TC-001"
        # Low last
        assert order[-1] == "TC-004"
    
    def test_priority_breakdown(self):
        """Test priority breakdown counts."""
        test_cases = [
            {"id": "TC-001", "priority": "critical", "risk_assessment": {"total_score": 10}},
            {"id": "TC-002", "priority": "critical", "risk_assessment": {"total_score": 9}},
            {"id": "TC-003", "priority": "medium", "risk_assessment": {"total_score": 5}}
        ]
        result = create_execution_plan(test_cases)
        
        breakdown = result["priority_breakdown"]
        assert breakdown["critical"] == 2
        assert breakdown["medium"] == 1
        assert breakdown["high"] == 0
        assert breakdown["low"] == 0
    
    def test_total_tests_count(self):
        """Test total tests is counted correctly."""
        test_cases = [
            {"id": "TC-001", "priority": "medium", "risk_assessment": {"total_score": 5}},
            {"id": "TC-002", "priority": "medium", "risk_assessment": {"total_score": 5}},
            {"id": "TC-003", "priority": "medium", "risk_assessment": {"total_score": 5}}
        ]
        result = create_execution_plan(test_cases)
        
        assert result["total_tests"] == 3
    
    def test_recommended_first_limit(self):
        """Test recommended_first has max 5 items."""
        test_cases = [
            {"id": f"TC-{i:03d}", "priority": "medium", "risk_assessment": {"total_score": 5}}
            for i in range(1, 11)
        ]
        result = create_execution_plan(test_cases)
        
        assert len(result["recommended_first"]) == 5
    
    def test_recommended_first_small_list(self):
        """Test recommended_first with less than 5 items."""
        test_cases = [
            {"id": "TC-001", "priority": "medium", "risk_assessment": {"total_score": 5}},
            {"id": "TC-002", "priority": "medium", "risk_assessment": {"total_score": 5}}
        ]
        result = create_execution_plan(test_cases)
        
        assert len(result["recommended_first"]) == 2


class TestIntegration:
    """Integration tests for the full prioritization flow."""
    
    def test_full_prioritization_pipeline(self):
        """Test complete risk assessment and planning flow."""
        test_cases = [
            {"id": "TC-001", "type": "positive", "steps": [{"step": 1}, {"step": 2}, {"step": 3}]},
            {"id": "TC-002", "type": "negative", "steps": [{"step": 1}, {"step": 2}]},
            {"id": "TC-003", "type": "edge_case", "steps": [{"step": 1}]},
            {"id": "TC-004", "type": "positive", "steps": [{"step": 1}, {"step": 2}]}
        ]
        
        assessed = assess_risk(test_cases)
        plan = create_execution_plan(assessed)
        
        assert plan["total_tests"] == 4
        assert len(plan["execution_order"]) == 4
        
        # Verify sorting works
        scores = [tc["risk_assessment"]["total_score"] for tc in plan["test_cases"]]
        assert scores == sorted(scores, reverse=True)
