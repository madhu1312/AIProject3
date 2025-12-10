"""
Export Agent - Agent 5 of 5

This agent exports test cases to Zephyr/Jira CSV format and 
generates Playwright/Tosca test stubs.

JIRA Ticket: SCRUM-77
"""
from __future__ import annotations

import asyncio
import os
import json
import csv
from io import StringIO
from typing import Any, Dict, List
from dotenv import load_dotenv
from laddr import Agent, WorkerRunner
from laddr.llms import openai
from laddr.core.tools import tool

load_dotenv()


@tool(
    name="export_to_zephyr_csv",
    description="Export test cases to Zephyr-compatible CSV format",
    parameters={
        "type": "object",
        "properties": {
            "test_cases": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Array of test cases to export"
            },
            "project_key": {"type": "string", "default": "PROJ"}
        },
        "required": ["test_cases"]
    }
)
def export_to_zephyr_csv(test_cases: List[Dict], project_key: str = "PROJ") -> Dict[str, Any]:
    """Export test cases to Zephyr CSV format."""
    output = StringIO()
    
    # Zephyr CSV headers
    headers = [
        "Name", "Description", "Priority", "Status", "Labels",
        "Component", "Folder", "Precondition", "Test Steps", "Expected Result"
    ]
    
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    
    rows = []
    for tc in test_cases:
        # Format test steps
        steps = tc.get("test_steps", [])
        formatted_steps = "\n".join([
            f"{s['step']}. {s['action']}" for s in steps
        ])
        
        expected_results = "\n".join([
            f"{s['step']}. {s['expected']}" for s in steps
        ])
        
        row = {
            "Name": tc.get("title", tc.get("id")),
            "Description": tc.get("description", ""),
            "Priority": tc.get("priority", "Medium").capitalize(),
            "Status": "Not Executed",
            "Labels": ",".join(tc.get("tags", [])),
            "Component": "",
            "Folder": f"/{project_key}/Automated",
            "Precondition": "\n".join(tc.get("preconditions", [])),
            "Test Steps": formatted_steps,
            "Expected Result": expected_results
        }
        writer.writerow(row)
        rows.append(row)
    
    csv_content = output.getvalue()
    
    return {
        "format": "zephyr_csv",
        "csv_content": csv_content,
        "row_count": len(rows),
        "headers": headers
    }


@tool(
    name="export_to_jira_csv",
    description="Export test cases to Jira-compatible CSV format",
    parameters={
        "type": "object",
        "properties": {
            "test_cases": {"type": "array", "items": {"type": "object"}},
            "project_key": {"type": "string", "default": "PROJ"}
        },
        "required": ["test_cases"]
    }
)
def export_to_jira_csv(test_cases: List[Dict], project_key: str = "PROJ") -> Dict[str, Any]:
    """Export test cases to Jira CSV format for import."""
    output = StringIO()
    
    # Jira CSV headers
    headers = [
        "Summary", "Description", "Issue Type", "Priority", "Labels",
        "Component", "Custom Field (Test Type)", "Custom Field (Source Story)"
    ]
    
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    
    rows = []
    for tc in test_cases:
        # Format description with steps
        steps = tc.get("test_steps", [])
        description = f"{tc.get('description', '')}\n\n"
        description += "h3. Preconditions\n"
        description += "\n".join([f"* {p}" for p in tc.get("preconditions", [])])
        description += "\n\nh3. Test Steps\n"
        description += "\n".join([
            f"# {s['action']} -> Expected: {s['expected']}" for s in steps
        ])
        
        row = {
            "Summary": f"[{tc.get('id')}] {tc.get('title', '')}",
            "Description": description,
            "Issue Type": "Test",
            "Priority": tc.get("priority", "Medium").capitalize(),
            "Labels": " ".join(tc.get("tags", [])),
            "Component": "",
            "Custom Field (Test Type)": tc.get("type", "manual"),
            "Custom Field (Source Story)": tc.get("source_story", "")
        }
        writer.writerow(row)
        rows.append(row)
    
    csv_content = output.getvalue()
    
    return {
        "format": "jira_csv",
        "csv_content": csv_content,
        "row_count": len(rows),
        "headers": headers
    }


@tool(
    name="generate_playwright_stubs",
    description="Generate Playwright test file stubs from test cases",
    parameters={
        "type": "object",
        "properties": {
            "test_cases": {"type": "array", "items": {"type": "object"}},
            "base_url": {"type": "string", "default": "http://localhost:3000"}
        },
        "required": ["test_cases"]
    }
)
def generate_playwright_stubs(test_cases: List[Dict], base_url: str = "http://localhost:3000") -> Dict[str, Any]:
    """Generate Playwright test stubs."""
    
    playwright_code = '''import { test, expect } from '@playwright/test';

/**
 * Auto-generated test stubs from Requirements Pipeline
 * Generated by Export Agent
 */

test.describe('Generated Test Cases', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('%s');
  });

''' % base_url

    for tc in test_cases:
        tc_id = tc.get("id", "TC-0000")
        title = tc.get("title", "Test Case")
        steps = tc.get("test_steps", [])
        
        playwright_code += f'''
  test('{tc_id}: {title}', async ({{ page }}) => {{
    // Test Type: {tc.get("type", "unknown")}
    // Source Story: {tc.get("source_story", "N/A")}
    // Priority: {tc.get("priority", "Medium")}
    
'''
        
        for step in steps:
            playwright_code += f'''    // Step {step.get("step", 0)}: {step.get("action", "")}
    // Expected: {step.get("expected", "")}
    // TODO: Implement step
    
'''
        
        playwright_code += f'''    // Verify expected result
    // TODO: Add assertions
    expect(true).toBe(true); // Placeholder
  }});

'''
    
    playwright_code += '});\n'
    
    return {
        "format": "playwright",
        "code": playwright_code,
        "test_count": len(test_cases),
        "file_name": "generated.spec.ts"
    }


@tool(
    name="generate_tosca_stubs",
    description="Generate Tosca test module stubs from test cases",
    parameters={
        "type": "object",
        "properties": {
            "test_cases": {"type": "array", "items": {"type": "object"}}
        },
        "required": ["test_cases"]
    }
)
def generate_tosca_stubs(test_cases: List[Dict]) -> Dict[str, Any]:
    """Generate Tosca test module stubs in XML format."""
    
    tosca_xml = '''<?xml version="1.0" encoding="utf-8"?>
<ToscaTestSuite>
  <Name>Generated Test Suite</Name>
  <Description>Auto-generated from Requirements Pipeline</Description>
  <TestCases>
'''
    
    for tc in test_cases:
        tc_id = tc.get("id", "TC-0000")
        title = tc.get("title", "Test Case")
        steps = tc.get("test_steps", [])
        
        tosca_xml += f'''
    <TestCase id="{tc_id}">
      <Name>{title}</Name>
      <Type>{tc.get("type", "Manual")}</Type>
      <Priority>{tc.get("priority", "Medium")}</Priority>
      <SourceStory>{tc.get("source_story", "")}</SourceStory>
      <TestSteps>
'''
        
        for step in steps:
            tosca_xml += f'''        <Step number="{step.get("step", 0)}">
          <Action>{step.get("action", "")}</Action>
          <Expected>{step.get("expected", "")}</Expected>
        </Step>
'''
        
        tosca_xml += '''      </TestSteps>
    </TestCase>
'''
    
    tosca_xml += '''  </TestCases>
</ToscaTestSuite>
'''
    
    return {
        "format": "tosca_xml",
        "xml_content": tosca_xml,
        "test_count": len(test_cases),
        "file_name": "tosca_test_suite.xml"
    }


TOOLS = [export_to_zephyr_csv, export_to_jira_csv, generate_playwright_stubs, generate_tosca_stubs]

export_agent = Agent(
    name="export_agent",
    role="Test Export Specialist",
    goal="Export test cases to various formats for test management tools and automation frameworks",
    backstory="""You are a test automation engineer who specializes in integrating 
    test cases with various tools. You can export to Zephyr, Jira, and generate 
    code stubs for Playwright and Tosca. You ensure the exported formats are 
    compatible with the target systems and include all necessary metadata.""",
    
    llm=openai(model=os.getenv("LLM_MODEL_EXPORT_AGENT", "gpt-4o-mini"), temperature=0.0),
    tools=TOOLS,
    
    max_retries=2,
    max_iterations=5,
    max_tool_calls=10,
    timeout=120,
    
    trace_enabled=True,
    trace_mask=[],
    
    instructions="""
    ## Your Role
    You are the fifth and final agent in a Requirements → Test Cases pipeline.
    You receive prioritized test cases from Agent 4 (risk_prioritize).
    
    ## Your Task
    1. Use export_to_zephyr_csv to create Zephyr import file
    2. Use export_to_jira_csv to create Jira import file
    3. Use generate_playwright_stubs to create automation code
    4. Use generate_tosca_stubs to create Tosca modules
    5. Return all export formats
    
    ## Output Format
    Return a JSON object with:
    {
        "status": "success",
        "exports": {
            "zephyr_csv": {...},
            "jira_csv": {...},
            "playwright": {...},
            "tosca": {...}
        },
        "summary": "Exported X test cases to 4 formats"
    }
    
    ## Export Formats
    - Zephyr CSV: For Zephyr Scale test management
    - Jira CSV: For direct Jira import as Test issues
    - Playwright: TypeScript test stubs with TODOs
    - Tosca: XML test module definitions
    """
)


async def main():
    """Run this agent as a worker."""
    runner = WorkerRunner(agent=export_agent)
    print("Starting export_agent worker...")
    await runner.start()


if __name__ == "__main__":
    asyncio.run(main())
