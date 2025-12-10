"""
Risk Prioritization Agent - Agent 4 of 5

This agent prioritizes test cases based on risk assessment.

JIRA Ticket: SCRUM-76
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
    name="assess_risk",
    description="Assess risk factors for test cases",
    parameters={
        "type": "object",
        "properties": {
            "test_cases": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Array of test cases to assess"
            }
        },
        "required": ["test_cases"]
    }
)
def assess_risk(test_cases: List[Dict]) -> Dict[str, Any]:
    """Assess risk for each test case."""
    risk_assessments = []
    
    risk_factors = {
        "positive": {"business_impact": 5, "failure_likelihood": 2},
        "negative": {"business_impact": 4, "failure_likelihood": 4},
        "edge_case": {"business_impact": 3, "failure_likelihood": 5}
    }
    
    for tc in test_cases:
        tc_type = tc.get("type", "positive")
        factors = risk_factors.get(tc_type, {"business_impact": 3, "failure_likelihood": 3})
        
        # Calculate risk score
        risk_score = (factors["business_impact"] * 2 + factors["failure_likelihood"]) / 3
        
        assessment = {
            "test_case_id": tc.get("id"),
            "test_type": tc_type,
            "risk_factors": {
                "business_impact": factors["business_impact"],
                "failure_likelihood": factors["failure_likelihood"],
                "technical_complexity": 3,
                "integration_risk": 3 if "integration" in tc.get("tags", []) else 2
            },
            "risk_score": round(risk_score, 2),
            "risk_level": "high" if risk_score >= 4 else "medium" if risk_score >= 2.5 else "low"
        }
        risk_assessments.append(assessment)
    
    return {
        "risk_assessments": risk_assessments,
        "total_assessed": len(risk_assessments),
        "risk_distribution": {
            "high": len([r for r in risk_assessments if r["risk_level"] == "high"]),
            "medium": len([r for r in risk_assessments if r["risk_level"] == "medium"]),
            "low": len([r for r in risk_assessments if r["risk_level"] == "low"])
        }
    }


@tool(
    name="prioritize_tests",
    description="Prioritize test cases based on risk assessment",
    parameters={
        "type": "object",
        "properties": {
            "test_cases": {"type": "array", "items": {"type": "object"}},
            "risk_assessments": {"type": "array", "items": {"type": "object"}}
        },
        "required": ["test_cases", "risk_assessments"]
    }
)
def prioritize_tests(test_cases: List[Dict], risk_assessments: List[Dict]) -> Dict[str, Any]:
    """Prioritize test cases based on risk."""
    # Create risk lookup
    risk_lookup = {r["test_case_id"]: r for r in risk_assessments}
    
    # Add priority to test cases
    prioritized = []
    for tc in test_cases:
        tc_id = tc.get("id")
        risk = risk_lookup.get(tc_id, {"risk_score": 2.5, "risk_level": "medium"})
        
        prioritized.append({
            **tc,
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "execution_priority": 1 if risk["risk_level"] == "high" else 2 if risk["risk_level"] == "medium" else 3
        })
    
    # Sort by priority (lower number = higher priority)
    prioritized.sort(key=lambda x: (x["execution_priority"], -x["risk_score"]))
    
    # Add execution order
    for idx, tc in enumerate(prioritized):
        tc["execution_order"] = idx + 1
    
    return {
        "prioritized_tests": prioritized,
        "total_prioritized": len(prioritized),
        "priority_summary": {
            "critical": len([t for t in prioritized if t["execution_priority"] == 1]),
            "important": len([t for t in prioritized if t["execution_priority"] == 2]),
            "normal": len([t for t in prioritized if t["execution_priority"] == 3])
        }
    }


@tool(
    name="generate_execution_plan",
    description="Generate test execution plan based on priorities",
    parameters={
        "type": "object",
        "properties": {
            "prioritized_tests": {"type": "array", "items": {"type": "object"}},
            "time_budget_hours": {"type": "number", "default": 8}
        },
        "required": ["prioritized_tests"]
    }
)
def generate_execution_plan(prioritized_tests: List[Dict], time_budget_hours: float = 8) -> Dict[str, Any]:
    """Generate execution plan with time estimates."""
    avg_time_per_test = 0.25  # 15 minutes per test
    total_tests = len(prioritized_tests)
    max_tests_in_budget = int(time_budget_hours / avg_time_per_test)
    
    # Phase 1: Critical tests (always run)
    phase1 = [t for t in prioritized_tests if t["execution_priority"] == 1]
    
    # Phase 2: Important tests (run if time permits)
    phase2 = [t for t in prioritized_tests if t["execution_priority"] == 2]
    
    # Phase 3: Normal tests (run with full regression)
    phase3 = [t for t in prioritized_tests if t["execution_priority"] == 3]
    
    return {
        "execution_plan": {
            "total_tests": total_tests,
            "estimated_total_hours": total_tests * avg_time_per_test,
            "time_budget_hours": time_budget_hours,
            "max_tests_in_budget": max_tests_in_budget,
            "phases": [
                {
                    "name": "Critical Path",
                    "tests": [t["id"] for t in phase1],
                    "count": len(phase1),
                    "estimated_hours": len(phase1) * avg_time_per_test,
                    "run_when": "always"
                },
                {
                    "name": "Important",
                    "tests": [t["id"] for t in phase2],
                    "count": len(phase2),
                    "estimated_hours": len(phase2) * avg_time_per_test,
                    "run_when": "time_permits"
                },
                {
                    "name": "Full Regression",
                    "tests": [t["id"] for t in phase3],
                    "count": len(phase3),
                    "estimated_hours": len(phase3) * avg_time_per_test,
                    "run_when": "full_regression"
                }
            ]
        },
        "recommendation": f"Run Phase 1 ({len(phase1)} tests) for quick validation, add Phase 2 ({len(phase2)} tests) for standard testing"
    }


TOOLS = [assess_risk, prioritize_tests, generate_execution_plan]

risk_prioritize = Agent(
    name="risk_prioritize",
    role="Risk Assessment Specialist",
    goal="Prioritize test cases based on risk analysis for optimal test execution",
    backstory="""You are a quality assurance manager who specializes in risk-based 
    testing. You understand how to assess business impact, failure likelihood, and 
    technical complexity to prioritize test execution. You create efficient test 
    execution plans that maximize coverage within time constraints.""",
    
    llm=openai(model=os.getenv("LLM_MODEL_RISK_PRIORITIZE", "gpt-4o-mini"), temperature=0.0),
    tools=TOOLS,
    
    max_retries=2,
    max_iterations=5,
    max_tool_calls=15,
    timeout=120,
    
    trace_enabled=True,
    trace_mask=[],
    
    instructions="""
    ## Your Role
    You are the fourth agent in a Requirements → Test Cases pipeline.
    You receive test cases from Agent 3 (testcase_design).
    
    ## Your Task
    1. Use assess_risk to evaluate risk factors for each test case
    2. Use prioritize_tests to order tests by risk
    3. Use generate_execution_plan to create a phased execution plan
    4. Return prioritized tests with execution recommendations
    
    ## Output Format
    Return a JSON object with:
    {
        "status": "success",
        "prioritized_tests": [...],
        "execution_plan": {...},
        "summary": "X tests prioritized, Y high-risk identified"
    }
    
    ## Risk Assessment Factors
    - Business impact (1-5)
    - Failure likelihood (1-5)
    - Technical complexity (1-5)
    - Integration dependencies (1-5)
    
    ## Priority Levels
    - Priority 1 (Critical): Run always
    - Priority 2 (Important): Run in standard test cycle
    - Priority 3 (Normal): Run in full regression
    """
)


async def main():
    """Run this agent as a worker."""
    runner = WorkerRunner(agent=risk_prioritize)
    print("Starting risk_prioritize worker...")
    await runner.start()


if __name__ == "__main__":
    asyncio.run(main())
