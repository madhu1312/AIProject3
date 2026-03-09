#!/usr/bin/env python
"""
Pipeline Demo - Requirements to Test Cases

Demonstrates the full 5-agent pipeline by calling the tool functions directly.
No OpenAI API key required for this demo.

Usage:
    python pipeline_demo.py
"""
from __future__ import annotations

import json
import re
import csv
from io import StringIO
from typing import Any, Dict, List


# ─────────────────────────────────────────────
# Inline tool implementations (no laddr needed)
# ─────────────────────────────────────────────

def parse_requirements(content: str) -> Dict[str, Any]:
    """Agent 1: Parse raw requirements text into structured sections."""
    sections = []
    current_section = None

    for line in content.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            level = len(re.match(r"^#+", line).group())
            title = line.lstrip("#").strip()
            current_section = {"level": level, "title": title, "content": [], "requirements": []}
            sections.append(current_section)
        elif current_section:
            req_match = re.match(r"^(REQ|FR|NFR|UC|US)-(\d+):?\s*(.*)", line, re.IGNORECASE)
            if req_match:
                current_section["requirements"].append({
                    "id": f"{req_match.group(1).upper()}-{req_match.group(2)}",
                    "text": req_match.group(3) or "",
                    "type": req_match.group(1).upper(),
                })
            else:
                current_section["content"].append(line)

    all_reqs = [req for sec in sections for req in sec["requirements"]]
    return {
        "sections": sections,
        "total_sections": len(sections),
        "total_requirements": len(all_reqs),
        "all_requirements": all_reqs,
    }


def generate_user_stories(requirements: List[Dict]) -> Dict[str, Any]:
    """Agent 2: Generate user stories from requirements."""
    user_stories = []
    for idx, req in enumerate(requirements):
        req_id = req.get("id", f"REQ-{idx + 1}")
        req_text = req.get("text", "")
        story = {
            "id": f"US-{idx + 1:03d}",
            "source_requirement": req_id,
            "story": f"As a user, I want to {req_text.lower()}, so that I can achieve the desired outcome",
            "acceptance_criteria": [
                f"Given the system is ready, when the user performs the action, then {req_text}",
                "The feature should be accessible to authorized users",
                "The system should provide appropriate feedback",
            ],
            "priority": "Medium",
        }
        user_stories.append(story)
    return {"user_stories": user_stories, "total_stories": len(user_stories)}


def design_test_cases(user_stories: List[Dict]) -> Dict[str, Any]:
    """Agent 3: Design test cases from user stories."""
    test_cases = []
    tc_counter = 1
    for story in user_stories:
        story_id = story.get("id", "US-000")
        for ac_idx, _ in enumerate(story.get("acceptance_criteria", [])):
            test_cases.append({
                "id": f"TC-{tc_counter:04d}",
                "title": f"Verify {story_id} - Positive Path {ac_idx + 1}",
                "type": "positive",
                "priority": "high",
                "source_story": story_id,
                "preconditions": ["System is in ready state", "User is authenticated"],
                "test_steps": [
                    {"step": 1, "action": "Navigate to the feature", "expected": "Feature is accessible"},
                    {"step": 2, "action": "Perform the main action", "expected": "Action completes successfully"},
                    {"step": 3, "action": "Verify the result", "expected": "Expected outcome is achieved"},
                ],
                "tags": ["positive", story_id],
            })
            tc_counter += 1
            test_cases.append({
                "id": f"TC-{tc_counter:04d}",
                "title": f"Verify {story_id} - Negative Path {ac_idx + 1}",
                "type": "negative",
                "priority": "medium",
                "source_story": story_id,
                "preconditions": ["System is in ready state"],
                "test_steps": [
                    {"step": 1, "action": "Attempt action with invalid input", "expected": "Error is displayed"},
                    {"step": 2, "action": "Verify error handling", "expected": "Appropriate error message shown"},
                ],
                "tags": ["negative", story_id],
            })
            tc_counter += 1
    return {"test_cases": test_cases, "total_test_cases": len(test_cases)}


def assess_risk(test_cases: List[Dict]) -> List[Dict]:
    """Agent 4: Assess risk for each test case."""
    risk_factors = {
        "positive": {"business_impact": 5, "failure_likelihood": 2},
        "negative": {"business_impact": 4, "failure_likelihood": 4},
        "edge_case": {"business_impact": 3, "failure_likelihood": 5},
    }
    assessments = []
    for tc in test_cases:
        factors = risk_factors.get(tc.get("type", "positive"), {"business_impact": 3, "failure_likelihood": 3})
        risk_score = (factors["business_impact"] * 2 + factors["failure_likelihood"]) / 3
        assessments.append({
            "test_case_id": tc["id"],
            "risk_score": round(risk_score, 2),
            "risk_level": "high" if risk_score >= 4 else "medium" if risk_score >= 2.5 else "low",
        })
    return assessments


def create_execution_plan(test_cases: List[Dict], risk_assessments: List[Dict]) -> Dict[str, Any]:
    """Agent 4: Create execution plan with risk-based priorities."""
    risk_lookup = {r["test_case_id"]: r for r in risk_assessments}
    prioritized = []
    for tc in test_cases:
        risk = risk_lookup.get(tc["id"], {"risk_score": 2.5, "risk_level": "medium"})
        prioritized.append({
            **tc,
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "execution_priority": 1 if risk["risk_level"] == "high" else 2,
        })
    prioritized.sort(key=lambda x: (x["execution_priority"], -x["risk_score"]))
    for idx, tc in enumerate(prioritized):
        tc["execution_order"] = idx + 1
    return {"prioritized_tests": prioritized, "total_prioritized": len(prioritized)}


def generate_playwright_stubs(test_cases: List[Dict], base_url: str = "http://localhost:5173") -> str:
    """Agent 5: Generate Playwright TypeScript test stubs."""
    code = f"""import {{ test, expect }} from '@playwright/test';

/**
 * Auto-generated test stubs from Requirements Pipeline
 * Generated by Export Agent
 */

test.describe('Generated Test Cases', () => {{
  test.beforeEach(async ({{ page }}) => {{
    await page.goto('{base_url}');
  }});

"""
    for tc in test_cases:
        tc_id = tc.get("id", "TC-0000")
        title = tc.get("title", "Test Case")
        steps = tc.get("test_steps", [])
        code += f"  test('{tc_id}: {title}', async ({{ page }}) => {{\n"
        for step in steps:
            code += f"    // Step {step.get('step', 0)}: {step.get('action', '')}\n"
            code += f"    // Expected: {step.get('expected', '')}\n"
            code += "    // TODO: Implement step\n\n"
        code += "    expect(true).toBe(true); // Placeholder\n"
        code += "  });\n\n"
    code += "});\n"
    return code


def export_to_zephyr_csv(test_cases: List[Dict]) -> str:
    """Agent 5: Export test cases to Zephyr-compatible CSV."""
    output = StringIO()
    headers = ["Name", "Description", "Priority", "Status", "Labels", "Test Steps", "Expected Result"]
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for tc in test_cases:
        steps = tc.get("test_steps", [])
        writer.writerow({
            "Name": tc.get("title", tc.get("id")),
            "Description": tc.get("description", f"Test case {tc.get('id')}"),
            "Priority": tc.get("priority", "Medium").capitalize(),
            "Status": "Not Executed",
            "Labels": ",".join(tc.get("tags", [])),
            "Test Steps": " | ".join([f"{s['step']}. {s['action']}" for s in steps]),
            "Expected Result": " | ".join([f"{s['step']}. {s['expected']}" for s in steps]),
        })
    return output.getvalue()


# ─────────────────────────────────────────────
# Demo runner
# ─────────────────────────────────────────────

SAMPLE_REQUIREMENTS = """
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


def run_pipeline(requirements_doc: str) -> Dict[str, Any]:
    """Run the full 5-stage pipeline and return results."""
    print("=" * 60)
    print("Requirements to Test Cases Pipeline")
    print("=" * 60)

    # Stage 1
    print("\n[1/5] Requirements Ingestion Agent...")
    parsed = parse_requirements(requirements_doc)
    all_reqs = parsed["all_requirements"]
    print(f"  → Parsed {parsed['total_requirements']} requirements from {parsed['total_sections']} sections")

    # Stage 2
    print("\n[2/5] User Story Extraction Agent...")
    stories_result = generate_user_stories(all_reqs)
    stories = stories_result["user_stories"]
    print(f"  → Generated {stories_result['total_stories']} user stories")

    # Stage 3
    print("\n[3/5] Test Case Design Agent...")
    cases_result = design_test_cases(stories)
    test_cases = cases_result["test_cases"]
    print(f"  → Designed {cases_result['total_test_cases']} test cases")

    # Stage 4
    print("\n[4/5] Risk Prioritization Agent...")
    risk = assess_risk(test_cases)
    plan = create_execution_plan(test_cases, risk)
    prioritized = plan["prioritized_tests"]
    print(f"  → Prioritized {plan['total_prioritized']} tests")

    # Stage 5
    print("\n[5/5] Export Agent...")
    playwright_code = generate_playwright_stubs(prioritized)
    zephyr_csv = export_to_zephyr_csv(prioritized)
    print(f"  → Generated Playwright stubs ({len(playwright_code)} chars)")
    print(f"  → Generated Zephyr CSV ({len(zephyr_csv.splitlines())} rows)")

    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)

    return {
        "status": "success",
        "parsed_requirements": parsed,
        "user_stories": stories_result,
        "test_cases": cases_result,
        "execution_plan": plan,
        "exports": {
            "playwright_stubs": playwright_code,
            "zephyr_csv": zephyr_csv,
        },
    }


if __name__ == "__main__":
    result = run_pipeline(SAMPLE_REQUIREMENTS)

    print("\n--- Sample Playwright Stub (first 1000 chars) ---")
    print(result["exports"]["playwright_stubs"][:1000])

    print("\n--- Sample Zephyr CSV (first 5 lines) ---")
    for line in result["exports"]["zephyr_csv"].splitlines()[:5]:
        print(line)

    print(f"\nSummary: {result['test_cases']['total_test_cases']} test cases generated")
    print(json.dumps({
        "requirements": result["parsed_requirements"]["total_requirements"],
        "user_stories": result["user_stories"]["total_stories"],
        "test_cases": result["test_cases"]["total_test_cases"],
        "prioritized": result["execution_plan"]["total_prioritized"],
    }, indent=2))
