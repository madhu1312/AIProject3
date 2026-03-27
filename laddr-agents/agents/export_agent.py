"""
Export Agent - Agent 5 of 5

This agent exports test cases to Zephyr/Jira CSV and generates Playwright/Tosca stubs.
JIRA Ticket: SCRUM-72
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from laddr import tool


@tool(name="export_to_zephyr_csv", description="Export test cases to Zephyr Scale CSV format")
def export_to_zephyr_csv(execution_plan: Dict[str, Any]) -> str:
    """Export test cases to Zephyr Scale CSV format."""
    test_cases = execution_plan.get("test_cases", [])
    
    lines = ["Name,Objective,Precondition,Priority,Status,Labels"]
    
    for tc in test_cases:
        name = tc.get("name", "").replace(",", ";")
        objective = tc.get("description", "").replace(",", ";")
        preconditions = "; ".join(tc.get("preconditions", [])).replace(",", ";")
        priority = tc.get("priority", "medium").capitalize()
        
        lines.append(f'"{name}","{objective}","{preconditions}","{priority}","Draft","automated"')
    
    return "\n".join(lines)


@tool(name="export_to_jira_csv", description="Export test cases to Jira CSV format")
def export_to_jira_csv(execution_plan: Dict[str, Any]) -> str:
    """Export test cases to Jira issue CSV format."""
    test_cases = execution_plan.get("test_cases", [])
    
    lines = ["Summary,Description,Issue Type,Priority,Labels"]
    
    for tc in test_cases:
        summary = tc.get("name", "").replace(",", ";")
        desc = tc.get("description", "").replace(",", ";")
        priority = tc.get("priority", "medium").capitalize()
        
        lines.append(f'"{summary}","{desc}","Test","{priority}","test-case"')
    
    return "\n".join(lines)


@tool(name="generate_playwright_stubs", description="Generate Playwright test stubs")
def generate_playwright_stubs(execution_plan: Dict[str, Any]) -> str:
    """Generate Playwright TypeScript test stubs."""
    test_cases = execution_plan.get("test_cases", [])
    
    code = f'''import {{ test, expect }} from '@playwright/test';

// Auto-generated test stubs from requirements pipeline
// Generated test cases: {len(test_cases)}

'''
    
    for tc in test_cases:
        tc_id = tc.get("id", "TC-000")
        name = tc.get("name", "Test Case")
        steps = tc.get("steps", [])
        preconditions = ", ".join(tc.get("preconditions", []))
        
        code += f'''
test('{tc_id}: {name}', async ({{ page }}) => {{
  // Preconditions: {preconditions}
  
'''
        
        for step in steps:
            action = step.get("action", "")
            expected = step.get("expected", "")
            code += f'''  // Step {step.get("step", 1)}: {action}
  // Expected: {expected}
  // TODO: Implement step
  
'''
        
        code += f'''  // Expected Result: {tc.get("expected_result", "")}
}});
'''
    
    return code


@tool(name="generate_tosca_xml", description="Generate Tosca test module XML")
def generate_tosca_xml(execution_plan: Dict[str, Any]) -> str:
    """Generate Tosca test module XML stubs."""
    test_cases = execution_plan.get("test_cases", [])
    
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<TestModule name="GeneratedTests">
'''
    
    for tc in test_cases:
        tc_id = tc.get("id", "TC-000")
        name = tc.get("name", "Test Case").replace("&", "&amp;").replace("<", "&lt;")
        
        xml += f'''  <TestCase id="{tc_id}" name="{name}">
    <Priority>{tc.get("priority", "medium")}</Priority>
    <Steps>
'''
        
        for step in tc.get("steps", []):
            action = step.get("action", "").replace("&", "&amp;").replace("<", "&lt;")
            xml += f'''      <Step number="{step.get("step", 1)}">{action}</Step>
'''
        
        xml += '''    </Steps>
  </TestCase>
'''
    
    xml += '''</TestModule>'''
    
    return xml


# Export tools for pipeline
__all__ = ["export_to_zephyr_csv", "export_to_jira_csv", "generate_playwright_stubs", "generate_tosca_xml"]
