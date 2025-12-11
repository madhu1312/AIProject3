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
    python main.py demo
    python main.py run "path/to/requirements.md"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Import tools directly from agents
from agents.requirements_ingest import parse_requirements, validate_requirements
from agents.userstory_extract import extract_user_stories, generate_acceptance_criteria
from agents.testcase_design import design_test_cases, add_test_data
from agents.risk_prioritize import assess_risk, create_execution_plan
from agents.export_agent import (
    export_to_zephyr_csv, 
    export_to_jira_csv, 
    generate_playwright_stubs, 
    generate_tosca_xml
)


def run_pipeline(requirements_content: str) -> dict:
    """
    Run the full pipeline with the given requirements content.
    
    Args:
        requirements_content: Raw requirements document text
    
    Returns:
        Final pipeline output with all exports
    """
    print("=" * 60)
    print("Requirements to Test Cases Pipeline")
    print("=" * 60)
    
    # Stage 1: Requirements Ingestion
    print("\n[1/5] Running Requirements Ingestion...")
    parsed = parse_requirements(requirements_content)
    validation = validate_requirements(parsed)
    print(f"  → Parsed {validation['total_requirements']} requirements")
    print(f"  → Valid: {validation['valid']}")
    
    # Stage 2: User Story Extraction
    print("\n[2/5] Extracting User Stories...")
    stories = extract_user_stories(parsed)
    enhanced_stories = generate_acceptance_criteria(stories)
    print(f"  → Generated {len(enhanced_stories)} user stories")
    
    # Stage 3: Test Case Design
    print("\n[3/5] Designing Test Cases...")
    test_cases = design_test_cases(enhanced_stories)
    test_cases_with_data = add_test_data(test_cases)
    print(f"  → Designed {len(test_cases_with_data)} test cases")
    
    # Stage 4: Risk Prioritization
    print("\n[4/5] Prioritizing by Risk...")
    assessed_cases = assess_risk(test_cases_with_data)
    execution_plan = create_execution_plan(assessed_cases)
    print(f"  → Priority breakdown: {execution_plan['priority_breakdown']}")
    
    # Stage 5: Export
    print("\n[5/5] Exporting to Multiple Formats...")
    zephyr_csv = export_to_zephyr_csv(execution_plan)
    jira_csv = export_to_jira_csv(execution_plan)
    playwright_code = generate_playwright_stubs(execution_plan)
    tosca_xml = generate_tosca_xml(execution_plan)
    print("  → Generated: Zephyr CSV, Jira CSV, Playwright stubs, Tosca XML")
    
    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)
    
    return {
        "status": "success",
        "summary": {
            "requirements_parsed": validation['total_requirements'],
            "user_stories": len(enhanced_stories),
            "test_cases": len(test_cases_with_data),
            "priority_breakdown": execution_plan['priority_breakdown']
        },
        "exports": {
            "zephyr_csv": zephyr_csv,
            "jira_csv": jira_csv,
            "playwright_code": playwright_code,
            "tosca_xml": tosca_xml
        },
        "execution_order": execution_plan['execution_order']
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py demo              - Run with sample requirements")
        print("  python main.py run <file>        - Run with requirements file")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "demo":
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

## User Stories

US-001: As an author, I want to create articles so that I can share content
US-002: As an editor, I want to review drafts so that I can ensure quality
"""
        result = run_pipeline(sample_requirements)
        
        # Print summary
        print("\n--- SUMMARY ---")
        print(json.dumps(result["summary"], indent=2))
        
        # Save exports to files
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        (output_dir / "zephyr_tests.csv").write_text(result["exports"]["zephyr_csv"])
        (output_dir / "jira_tests.csv").write_text(result["exports"]["jira_csv"])
        (output_dir / "playwright_tests.spec.ts").write_text(result["exports"]["playwright_code"])
        (output_dir / "tosca_tests.xml").write_text(result["exports"]["tosca_xml"])
        
        print(f"\n✅ Exports saved to {output_dir.absolute()}/")
        print("  - zephyr_tests.csv")
        print("  - jira_tests.csv")
        print("  - playwright_tests.spec.ts")
        print("  - tosca_tests.xml")
    
    elif command == "run":
        if len(sys.argv) < 3:
            print("Error: Please provide a requirements file path")
            sys.exit(1)
        
        filepath = Path(sys.argv[2])
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        
        content = filepath.read_text()
        result = run_pipeline(content)
        print("\n--- RESULT ---")
        print(json.dumps(result["summary"], indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
