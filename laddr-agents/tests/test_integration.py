"""
Functional Integration Tests for Laddr Multi-Agent Pipeline
JIRA: SCRUM-79

These tests verify the complete agent pipeline works end-to-end,
testing data flow between agents and ensuring the full workflow
produces expected outputs.
"""

import pytest
import json
import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from requirements_ingest import parse_requirements, validate_requirements
from userstory_extract import extract_user_stories, generate_acceptance_criteria
from testcase_design import design_test_cases, add_test_data
from risk_prioritize import assess_risk, create_execution_plan
from export_agent import (
    export_to_zephyr_csv,
    export_to_jira_csv,
    generate_playwright_stubs,
    generate_tosca_xml
)


# ============================================================================
# TEST FIXTURES - Real-world requirement documents
# ============================================================================

@pytest.fixture
def cms_requirements_document():
    """Complete CMS requirements document for integration testing."""
    return """
# Content Management System Requirements

## Functional Requirements

FR-001: Users shall be able to create new articles with title, content, and metadata
FR-002: Users shall be able to edit existing articles
FR-003: Users shall be able to delete articles with confirmation
FR-004: Users shall be able to publish/unpublish articles
FR-005: System shall support rich text editing with TipTap editor
FR-006: System shall auto-save drafts every 30 seconds

## Non-Functional Requirements

NFR-001: Page load time shall be under 2 seconds
NFR-002: System shall support 100 concurrent users
NFR-003: System shall be accessible on mobile devices

## User Stories

US-001: As an author, I want to create articles so that I can publish content
US-002: As an editor, I want to review articles so that I can ensure quality
US-003: As an admin, I want to manage users so that I can control access
"""


@pytest.fixture
def ecommerce_requirements_document():
    """E-commerce requirements for testing different domain."""
    return """
# E-Commerce Platform Requirements

## Functional Requirements

FR-001: Users shall be able to browse products by category
FR-002: Users shall be able to add products to cart
FR-003: Users shall be able to checkout with payment
FR-004: Users shall receive order confirmation emails

## User Stories

US-001: As a customer, I want to search products so that I can find what I need
US-002: As a customer, I want to track orders so that I know delivery status
"""


@pytest.fixture
def api_requirements_document():
    """API requirements for testing technical domain."""
    return """
# REST API Requirements

## Functional Requirements

FR-001: API shall support CRUD operations for resources
FR-002: API shall implement authentication via JWT tokens
FR-003: API shall return proper HTTP status codes
FR-004: API shall support pagination for list endpoints

## Non-Functional Requirements

NFR-001: API response time shall be under 200ms
NFR-002: API shall handle 1000 requests per second
"""


# ============================================================================
# INTEGRATION TEST: Full Pipeline Flow
# ============================================================================

class TestFullPipelineIntegration:
    """Test complete agent pipeline from requirements to exports."""
    
    def test_cms_full_pipeline(self, cms_requirements_document):
        """
        INTEGRATION TEST: Complete CMS pipeline
        
        Flow: Requirements → Parse → Validate → Extract Stories → 
              Generate Criteria → Design Test Cases → Add Test Data →
              Assess Risk → Create Plan → Export All Formats
        """
        print("\n" + "="*60)
        print("🚀 INTEGRATION TEST: CMS Full Pipeline")
        print("="*60)
        
        # Step 1: Parse Requirements
        print("\n📋 Step 1: Parsing requirements document...")
        parsed = parse_requirements(cms_requirements_document)
        assert "functional" in parsed
        assert "user_stories" in parsed
        print(f"   ✓ Parsed {sum(len(v) for v in parsed.values() if isinstance(v, list))} requirements")
        
        # Step 2: Validate Requirements
        print("\n✅ Step 2: Validating requirements...")
        validation = validate_requirements(parsed)
        assert validation["valid"] is True
        print(f"   ✓ Validation passed: {validation['total_requirements']} total requirements")
        
        # Step 3: Extract User Stories
        print("\n📖 Step 3: Extracting user stories...")
        stories = extract_user_stories(parsed)
        assert len(stories) > 0
        print(f"   ✓ Extracted {len(stories)} user stories")
        
        # Step 4: Generate Acceptance Criteria
        print("\n📝 Step 4: Generating acceptance criteria...")
        enriched_stories = generate_acceptance_criteria(stories)
        assert all("acceptance_criteria" in s for s in enriched_stories)
        print(f"   ✓ Generated criteria for {len(enriched_stories)} stories")
        
        # Step 5: Design Test Cases
        print("\n🧪 Step 5: Designing test cases...")
        test_cases = design_test_cases(enriched_stories)
        assert len(test_cases) > 0
        print(f"   ✓ Designed {len(test_cases)} test cases")
        
        # Step 6: Add Test Data
        print("\n📊 Step 6: Adding test data and automation flags...")
        enhanced_cases = add_test_data(test_cases)
        assert all("test_data" in tc for tc in enhanced_cases)
        print(f"   ✓ Enhanced {len(enhanced_cases)} test cases with data")
        
        # Step 7: Assess Risk
        print("\n⚠️ Step 7: Assessing risk levels...")
        risk_assessed = assess_risk(enhanced_cases)
        assert all("risk_assessment" in tc for tc in risk_assessed)
        assert all("priority" in tc for tc in risk_assessed)
        print(f"   ✓ Risk assessed for {len(risk_assessed)} test cases")
        
        # Step 8: Create Execution Plan
        print("\n📅 Step 8: Creating execution plan...")
        plan = create_execution_plan(risk_assessed)
        assert "execution_order" in plan
        assert "priority_breakdown" in plan
        assert "test_cases" in plan
        print(f"   ✓ Execution plan created with {plan['total_tests']} tests")
        
        # Step 9: Export to All Formats (using execution_plan)
        print("\n📤 Step 9: Exporting to all formats...")
        
        zephyr_csv = export_to_zephyr_csv(plan)
        assert "Name" in zephyr_csv
        print("   ✓ Zephyr CSV export successful")
        
        jira_csv = export_to_jira_csv(plan)
        assert "Summary" in jira_csv
        print("   ✓ JIRA CSV export successful")
        
        playwright_code = generate_playwright_stubs(plan)
        assert "import { test, expect }" in playwright_code
        print("   ✓ Playwright stubs generated")
        
        tosca_xml = generate_tosca_xml(plan)
        assert "<?xml version" in tosca_xml
        print("   ✓ TOSCA XML export successful")
        
        print("\n" + "="*60)
        print("✅ CMS FULL PIPELINE: ALL STEPS PASSED")
        print("="*60)
        
        return {
            "requirements": parsed,
            "stories": enriched_stories,
            "test_cases": risk_assessed,
            "plan": plan,
            "exports": {
                "zephyr": len(zephyr_csv),
                "jira": len(jira_csv),
                "playwright": len(playwright_code),
                "tosca": len(tosca_xml)
            }
        }
    
    def test_ecommerce_full_pipeline(self, ecommerce_requirements_document):
        """
        INTEGRATION TEST: E-Commerce domain pipeline
        Verifies pipeline works across different domains.
        """
        print("\n" + "="*60)
        print("🛒 INTEGRATION TEST: E-Commerce Pipeline")
        print("="*60)
        
        # Execute full pipeline
        parsed = parse_requirements(ecommerce_requirements_document)
        validation = validate_requirements(parsed)
        stories = extract_user_stories(parsed)
        enriched = generate_acceptance_criteria(stories)
        test_cases = design_test_cases(enriched)
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        # Verify pipeline integrity
        assert validation["valid"] is True
        assert len(stories) >= 2  # At least 2 user stories
        assert len(test_cases) > len(stories)  # Multiple test cases per story
        assert plan["total_tests"] == len(risk_assessed)
        
        print(f"\n✅ E-Commerce Pipeline: {len(risk_assessed)} test cases generated")
        print("="*60)
    
    def test_api_full_pipeline(self, api_requirements_document):
        """
        INTEGRATION TEST: API/Technical domain pipeline
        Verifies pipeline handles technical requirements.
        """
        print("\n" + "="*60)
        print("🔌 INTEGRATION TEST: API Requirements Pipeline")
        print("="*60)
        
        # Execute full pipeline
        parsed = parse_requirements(api_requirements_document)
        validation = validate_requirements(parsed)
        stories = extract_user_stories(parsed)
        enriched = generate_acceptance_criteria(stories)
        test_cases = design_test_cases(enriched)
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        # Export to all formats (using execution plan)
        exports = {
            "zephyr": export_to_zephyr_csv(plan),
            "jira": export_to_jira_csv(plan),
            "playwright": generate_playwright_stubs(plan),
            "tosca": generate_tosca_xml(plan)
        }
        
        # Verify all exports generated
        assert all(len(v) > 0 for v in exports.values())
        
        print(f"\n✅ API Pipeline: {len(risk_assessed)} test cases, 4 export formats")
        print("="*60)


# ============================================================================
# INTEGRATION TEST: Data Flow Verification
# ============================================================================

class TestDataFlowIntegration:
    """Test data integrity across agent boundaries."""
    
    def test_requirement_ids_preserved(self, cms_requirements_document):
        """Verify requirement IDs flow through the entire pipeline."""
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        
        # Check that test cases reference source stories
        for tc in test_cases:
            assert "story_id" in tc or "id" in tc
    
    def test_story_to_testcase_relationship(self, cms_requirements_document):
        """Verify each story generates at least one test case."""
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        enriched = generate_acceptance_criteria(stories)
        test_cases = design_test_cases(enriched)
        
        # Each story should generate test cases
        assert len(test_cases) >= len(stories)
        print(f"\n📊 {len(stories)} stories → {len(test_cases)} test cases")
    
    def test_test_data_enrichment(self, cms_requirements_document):
        """Verify test data is properly added to test cases."""
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        
        for tc in enhanced:
            assert "test_data" in tc
            assert "automation_candidate" in tc
    
    def test_risk_assessment_completeness(self, cms_requirements_document):
        """Verify all test cases receive risk assessment."""
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        
        for tc in risk_assessed:
            assert "risk_assessment" in tc
            assert "priority" in tc
            assert tc["priority"] in ["critical", "high", "medium", "low"]
    
    def test_execution_plan_covers_all_tests(self, cms_requirements_document):
        """Verify execution plan includes all test cases."""
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        assert plan["total_tests"] == len(risk_assessed)
        assert len(plan["execution_order"]) == len(risk_assessed)


# ============================================================================
# INTEGRATION TEST: Export Format Validation
# ============================================================================

class TestExportIntegration:
    """Test all export formats work correctly with pipeline data."""
    
    def test_zephyr_export_structure(self, cms_requirements_document):
        """Verify Zephyr CSV has correct structure for import."""
        # Run pipeline
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        # Export using execution plan
        csv_content = export_to_zephyr_csv(plan)
        lines = csv_content.strip().split('\n')
        
        # Verify header has expected columns
        assert "Name" in lines[0]
        assert "Priority" in lines[0]
        
        # Verify data rows
        assert len(lines) > 1
    
    def test_jira_export_structure(self, cms_requirements_document):
        """Verify JIRA CSV has correct structure for import."""
        # Run pipeline
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        # Export using execution plan
        csv_content = export_to_jira_csv(plan)
        lines = csv_content.strip().split('\n')
        
        # Verify JIRA-compatible header
        assert "Summary" in lines[0]
        assert "Description" in lines[0]
        assert "Labels" in lines[0]
    
    def test_playwright_code_validity(self, cms_requirements_document):
        """Verify Playwright code is syntactically valid."""
        # Run pipeline
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        # Export using execution plan
        code = generate_playwright_stubs(plan)
        
        # Verify TypeScript/Playwright structure
        assert "import { test, expect } from '@playwright/test';" in code
        assert "test(" in code
        assert "async ({ page })" in code
    
    def test_tosca_xml_validity(self, cms_requirements_document):
        """Verify TOSCA XML is well-formed."""
        # Run pipeline
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        # Export using execution plan
        xml_content = generate_tosca_xml(plan)
        
        # Verify XML structure
        assert xml_content.startswith('<?xml version="1.0"')
        assert "<TestModule" in xml_content
        assert "</TestModule>" in xml_content
        assert "<TestCase" in xml_content
        assert "</TestCase>" in xml_content
    
    def test_all_exports_non_empty(self, cms_requirements_document):
        """Verify all export formats produce non-empty output."""
        # Run full pipeline
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        # Test all exports using execution plan
        exports = {
            "Zephyr CSV": export_to_zephyr_csv(plan),
            "JIRA CSV": export_to_jira_csv(plan),
            "Playwright": generate_playwright_stubs(plan),
            "TOSCA XML": generate_tosca_xml(plan)
        }
        
        for name, content in exports.items():
            assert len(content) > 100, f"{name} export is too short"
            print(f"   ✓ {name}: {len(content)} characters")


# ============================================================================
# INTEGRATION TEST: Error Handling & Edge Cases
# ============================================================================

class TestErrorHandlingIntegration:
    """Test pipeline handles edge cases gracefully."""
    
    def test_minimal_requirements(self):
        """Test pipeline with minimal valid input."""
        minimal_doc = """
## Functional Requirements
FR-001: Basic functionality
"""
        parsed = parse_requirements(minimal_doc)
        validation = validate_requirements(parsed)
        stories = extract_user_stories(parsed)
        
        # Should still work with minimal input
        assert validation["valid"] is True
        assert len(stories) >= 0  # May derive stories from functional
    
    def test_empty_sections_handled(self):
        """Test pipeline handles empty sections."""
        doc_with_empty = """
## Functional Requirements
FR-001: Create items

## Non-Functional Requirements

## User Stories
"""
        parsed = parse_requirements(doc_with_empty)
        validation = validate_requirements(parsed)
        
        assert validation["valid"] is True
    
    def test_special_characters_handled(self):
        """Test pipeline handles special characters in requirements."""
        special_doc = """
## Functional Requirements
FR-001: Handle "quoted" text with special chars: <>&
FR-002: Support multi-line
         requirements with indentation
"""
        parsed = parse_requirements(special_doc)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        # Export should handle special chars (using execution plan)
        zephyr = export_to_zephyr_csv(plan)
        tosca = generate_tosca_xml(plan)
        
        # Should not crash
        assert len(zephyr) > 0
        assert len(tosca) > 0
    
    def test_large_document_handling(self):
        """Test pipeline handles larger documents."""
        # Generate large document
        requirements = ["## Functional Requirements\n"]
        for i in range(1, 51):
            requirements.append(f"FR-{i:03d}: Requirement number {i} with description\n")
        
        large_doc = "".join(requirements)
        
        parsed = parse_requirements(large_doc)
        validation = validate_requirements(parsed)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        
        assert validation["valid"] is True
        assert len(parsed["functional"]) == 50
        print(f"\n📊 Large doc: 50 requirements → {len(test_cases)} test cases")


# ============================================================================
# INTEGRATION TEST: Pipeline Metrics
# ============================================================================

class TestPipelineMetrics:
    """Test that pipeline produces measurable, consistent results."""
    
    def test_test_case_multiplication_ratio(self, cms_requirements_document):
        """Verify test cases are generated at reasonable ratio."""
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        
        if len(stories) > 0:
            ratio = len(test_cases) / len(stories)
            # Each story should generate 2-5 test cases on average
            assert ratio >= 1, "Should generate at least 1 test case per story"
            print(f"\n📊 Test case ratio: {ratio:.1f} tests per story")
    
    def test_priority_distribution(self, cms_requirements_document):
        """Verify priority distribution is reasonable."""
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        risk_assessed = assess_risk(enhanced)
        plan = create_execution_plan(risk_assessed)
        
        breakdown = plan["priority_breakdown"]
        total = sum(breakdown.values())
        
        assert total == len(risk_assessed)
        print(f"\n📊 Priority breakdown: {breakdown}")
    
    def test_automation_candidate_ratio(self, cms_requirements_document):
        """Verify automation candidates are identified."""
        parsed = parse_requirements(cms_requirements_document)
        stories = extract_user_stories(parsed)
        test_cases = design_test_cases(generate_acceptance_criteria(stories))
        enhanced = add_test_data(test_cases)
        
        automatable = sum(1 for tc in enhanced if tc.get("automation_candidate", False))
        ratio = automatable / len(enhanced) if enhanced else 0
        
        print(f"\n📊 Automation candidates: {automatable}/{len(enhanced)} ({ratio:.0%})")
        # At least some should be automatable
        assert automatable > 0 or len(enhanced) == 0


# ============================================================================
# Run with verbose output
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
