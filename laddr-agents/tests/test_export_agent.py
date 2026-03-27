"""
Test Suite for Export Agent (Agent 5)

Tests all export tools: Zephyr CSV, Jira CSV, Playwright stubs, Tosca XML.
JIRA Ticket: SCRUM-78
"""
import pytest
from agents.export_agent import (
    export_to_zephyr_csv,
    export_to_jira_csv,
    generate_playwright_stubs,
    generate_tosca_xml
)


class TestExportToZephyrCSV:
    """Test cases for export_to_zephyr_csv tool."""
    
    def test_csv_header(self):
        """Test that CSV has correct header."""
        execution_plan = {"test_cases": []}
        result = export_to_zephyr_csv(execution_plan)
        
        assert result.startswith("Name,Objective,Precondition,Priority,Status,Labels")
    
    def test_export_single_test_case(self):
        """Test exporting a single test case."""
        execution_plan = {
            "test_cases": [
                {
                    "id": "TC-001",
                    "name": "Login Test",
                    "description": "Test user login",
                    "preconditions": ["User exists", "System is up"],
                    "priority": "high"
                }
            ]
        }
        result = export_to_zephyr_csv(execution_plan)
        lines = result.split("\n")
        
        assert len(lines) == 2  # Header + 1 test case
        assert "Login Test" in lines[1]
        assert "High" in lines[1]
        assert "Draft" in lines[1]
    
    def test_export_multiple_test_cases(self):
        """Test exporting multiple test cases."""
        execution_plan = {
            "test_cases": [
                {"id": "TC-001", "name": "Test 1", "description": "Desc 1", "preconditions": [], "priority": "high"},
                {"id": "TC-002", "name": "Test 2", "description": "Desc 2", "preconditions": [], "priority": "medium"},
                {"id": "TC-003", "name": "Test 3", "description": "Desc 3", "preconditions": [], "priority": "low"}
            ]
        }
        result = export_to_zephyr_csv(execution_plan)
        lines = result.split("\n")
        
        assert len(lines) == 4  # Header + 3 test cases
    
    def test_comma_handling(self):
        """Test that commas in content are handled."""
        execution_plan = {
            "test_cases": [
                {
                    "id": "TC-001",
                    "name": "Test with, comma",
                    "description": "Description with, comma",
                    "preconditions": ["Pre, condition"],
                    "priority": "medium"
                }
            ]
        }
        result = export_to_zephyr_csv(execution_plan)
        
        # Commas should be replaced with semicolons
        assert "Test with; comma" in result
    
    def test_empty_test_cases(self):
        """Test with empty test cases."""
        execution_plan = {"test_cases": []}
        result = export_to_zephyr_csv(execution_plan)
        lines = result.split("\n")
        
        assert len(lines) == 1  # Only header


class TestExportToJiraCSV:
    """Test cases for export_to_jira_csv tool."""
    
    def test_jira_csv_header(self):
        """Test that Jira CSV has correct header."""
        execution_plan = {"test_cases": []}
        result = export_to_jira_csv(execution_plan)
        
        assert result.startswith("Summary,Description,Issue Type,Priority,Labels")
    
    def test_export_test_case(self):
        """Test exporting a test case to Jira format."""
        execution_plan = {
            "test_cases": [
                {
                    "id": "TC-001",
                    "name": "Login Test",
                    "description": "Verify login works",
                    "priority": "critical"
                }
            ]
        }
        result = export_to_jira_csv(execution_plan)
        lines = result.split("\n")
        
        assert len(lines) == 2
        assert "Login Test" in lines[1]
        assert "Critical" in lines[1]
        assert "Test" in lines[1]  # Issue type
    
    def test_labels_present(self):
        """Test that test-case label is added."""
        execution_plan = {
            "test_cases": [
                {"id": "TC-001", "name": "Test", "description": "Desc", "priority": "medium"}
            ]
        }
        result = export_to_jira_csv(execution_plan)
        
        assert "test-case" in result


class TestGeneratePlaywrightStubs:
    """Test cases for generate_playwright_stubs tool."""
    
    def test_playwright_imports(self):
        """Test that imports are correct."""
        execution_plan = {"test_cases": []}
        result = generate_playwright_stubs(execution_plan)
        
        assert "import { test, expect } from '@playwright/test'" in result
    
    def test_test_case_comment(self):
        """Test that test count comment is present."""
        execution_plan = {
            "test_cases": [
                {"id": "TC-001", "name": "Test 1", "preconditions": [], "steps": [], "expected_result": "Pass"},
                {"id": "TC-002", "name": "Test 2", "preconditions": [], "steps": [], "expected_result": "Pass"}
            ]
        }
        result = generate_playwright_stubs(execution_plan)
        
        assert "Generated test cases: 2" in result
    
    def test_test_function_structure(self):
        """Test that test functions are generated correctly."""
        execution_plan = {
            "test_cases": [
                {
                    "id": "TC-001",
                    "name": "Login Test",
                    "preconditions": ["User exists"],
                    "steps": [
                        {"step": 1, "action": "Open login page", "expected": "Page loads"}
                    ],
                    "expected_result": "Login successful"
                }
            ]
        }
        result = generate_playwright_stubs(execution_plan)
        
        assert "test('TC-001: Login Test'" in result
        assert "async ({ page })" in result
        assert "Preconditions: User exists" in result
        assert "Step 1: Open login page" in result
        assert "Expected: Page loads" in result
    
    def test_multiple_steps(self):
        """Test generating multiple steps."""
        execution_plan = {
            "test_cases": [
                {
                    "id": "TC-001",
                    "name": "Multi-step test",
                    "preconditions": [],
                    "steps": [
                        {"step": 1, "action": "Action 1", "expected": "Result 1"},
                        {"step": 2, "action": "Action 2", "expected": "Result 2"},
                        {"step": 3, "action": "Action 3", "expected": "Result 3"}
                    ],
                    "expected_result": "All pass"
                }
            ]
        }
        result = generate_playwright_stubs(execution_plan)
        
        assert "Step 1:" in result
        assert "Step 2:" in result
        assert "Step 3:" in result
    
    def test_typescript_syntax(self):
        """Test that output is valid TypeScript syntax."""
        execution_plan = {
            "test_cases": [
                {"id": "TC-001", "name": "Test", "preconditions": [], "steps": [], "expected_result": "Pass"}
            ]
        }
        result = generate_playwright_stubs(execution_plan)
        
        # Check for proper async/await syntax
        assert "async (" in result
        # Check for proper closing
        assert "});" in result


class TestGenerateToscaXML:
    """Test cases for generate_tosca_xml tool."""
    
    def test_xml_declaration(self):
        """Test that XML declaration is present."""
        execution_plan = {"test_cases": []}
        result = generate_tosca_xml(execution_plan)
        
        assert '<?xml version="1.0" encoding="UTF-8"?>' in result
    
    def test_test_module_root(self):
        """Test that TestModule root element is present."""
        execution_plan = {"test_cases": []}
        result = generate_tosca_xml(execution_plan)
        
        assert '<TestModule name="GeneratedTests">' in result
        assert '</TestModule>' in result
    
    def test_test_case_element(self):
        """Test that test cases are properly formatted."""
        execution_plan = {
            "test_cases": [
                {
                    "id": "TC-001",
                    "name": "Login Test",
                    "priority": "high",
                    "steps": [{"step": 1, "action": "Login"}]
                }
            ]
        }
        result = generate_tosca_xml(execution_plan)
        
        assert '<TestCase id="TC-001" name="Login Test">' in result
        assert '<Priority>high</Priority>' in result
        assert '</TestCase>' in result
    
    def test_steps_in_xml(self):
        """Test that steps are included in XML."""
        execution_plan = {
            "test_cases": [
                {
                    "id": "TC-001",
                    "name": "Test",
                    "priority": "medium",
                    "steps": [
                        {"step": 1, "action": "First action"},
                        {"step": 2, "action": "Second action"}
                    ]
                }
            ]
        }
        result = generate_tosca_xml(execution_plan)
        
        assert "<Steps>" in result
        assert '</Steps>' in result
        assert '<Step number="1">First action</Step>' in result
        assert '<Step number="2">Second action</Step>' in result
    
    def test_xml_escaping(self):
        """Test that special characters are escaped."""
        execution_plan = {
            "test_cases": [
                {
                    "id": "TC-001",
                    "name": "Test with <special> & chars",
                    "priority": "medium",
                    "steps": [{"step": 1, "action": "Do <something> & more"}]
                }
            ]
        }
        result = generate_tosca_xml(execution_plan)
        
        assert "&lt;" in result
        assert "&amp;" in result


class TestIntegration:
    """Integration tests for the full export flow."""
    
    def test_all_exports(self):
        """Test generating all export formats."""
        execution_plan = {
            "test_cases": [
                {
                    "id": "TC-001",
                    "name": "Create Article Test",
                    "description": "Test article creation",
                    "preconditions": ["User logged in"],
                    "steps": [
                        {"step": 1, "action": "Click create", "expected": "Form opens"},
                        {"step": 2, "action": "Fill form", "expected": "Fields populated"},
                        {"step": 3, "action": "Submit", "expected": "Article saved"}
                    ],
                    "expected_result": "Article created successfully",
                    "priority": "high"
                }
            ],
            "execution_order": ["TC-001"]
        }
        
        zephyr = export_to_zephyr_csv(execution_plan)
        jira = export_to_jira_csv(execution_plan)
        playwright = generate_playwright_stubs(execution_plan)
        tosca = generate_tosca_xml(execution_plan)
        
        # All should have content
        assert len(zephyr) > 50
        assert len(jira) > 50
        assert len(playwright) > 100
        assert len(tosca) > 100
        
        # Verify content specific to each format
        assert "Name,Objective" in zephyr
        assert "Summary,Description" in jira
        assert "test(" in playwright
        assert "<TestModule" in tosca
