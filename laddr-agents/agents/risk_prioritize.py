"""
Risk Prioritization Agent - Agent 4 of 5

This agent prioritizes test cases based on risk assessment.
JIRA Ticket: SCRUM-73
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from laddr import tool


@tool(name="assess_risk", description="Assess risk factors for each test case")
def assess_risk(test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Assess risk factors for test cases."""
    for tc in test_cases:
        risk_factors = {
            "business_impact": 3 if tc.get("type") == "positive" else 2,
            "complexity": 2 if len(tc.get("steps", [])) > 2 else 1,
            "failure_probability": 2 if tc.get("type") == "edge_case" else 1,
            "user_frequency": 3 if tc.get("type") == "positive" else 1
        }
        
        risk_score = sum(risk_factors.values())
        
        if risk_score >= 9:
            priority = "critical"
        elif risk_score >= 7:
            priority = "high"
        elif risk_score >= 5:
            priority = "medium"
        else:
            priority = "low"
        
        tc["risk_assessment"] = {
            "factors": risk_factors,
            "total_score": risk_score,
            "priority": priority
        }
        tc["priority"] = priority
    
    return test_cases


@tool(name="create_execution_plan", description="Create prioritized test execution plan")
def create_execution_plan(test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a prioritized execution plan."""
    sorted_cases = sorted(
        test_cases, 
        key=lambda x: x.get("risk_assessment", {}).get("total_score", 0),
        reverse=True
    )
    
    plan = {"critical": [], "high": [], "medium": [], "low": []}
    
    for tc in sorted_cases:
        priority = tc.get("priority", "medium")
        plan[priority].append(tc["id"])
    
    execution_order = plan["critical"] + plan["high"] + plan["medium"] + plan["low"]
    
    return {
        "test_cases": sorted_cases,
        "execution_order": execution_order,
        "priority_breakdown": {k: len(v) for k, v in plan.items()},
        "total_tests": len(test_cases),
        "recommended_first": execution_order[:5] if len(execution_order) >= 5 else execution_order
    }


# Export tools for pipeline
__all__ = ["assess_risk", "create_execution_plan"]
