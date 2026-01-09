#!/usr/bin/env python
"""
Test Generator Agent - CI/CD Pipeline Interface
JIRA: SCRUM-85

This script wraps the test generation agents for use in the AI SDLC pipeline.
It generates tests for source files.

Usage:
    python test_generator_agent.py --source ../frontend/src/generated --output ../frontend/src/__tests__/generated
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from agents.testcase_design import design_test_cases
    from agents.playwright_implement import implement_test_case, generate_test_file
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False


# Test templates
UNIT_TEST_TEMPLATE = '''import {{ describe, it, expect, beforeEach, vi }} from 'vitest';
{imports}

describe('{test_suite_name}', () => {{
  beforeEach(() => {{
    vi.clearAllMocks();
  }});

{test_cases}
}});
'''

TEST_CASE_TEMPLATE = '''  it('{test_name}', async () => {{
    // Arrange
    {arrange}

    // Act
    {act}

    // Assert
    {assert}
  }});
'''

E2E_TEST_TEMPLATE = '''import {{ test, expect }} from '@playwright/test';

/**
 * E2E Tests for {feature_name}
 * Generated for: {ticket}
 * @generated
 */
test.describe('{feature_name}', () => {{
{test_cases}
}});
'''

E2E_CASE_TEMPLATE = '''  test('{test_name}', async ({{ page }}) => {{
    // Navigate to the feature
    await page.goto('{url}');

    // Verify page loaded
    await expect(page).toHaveTitle(/{title_pattern}/);

    // TODO: Add specific test steps
    {steps}
  }});
'''


def extract_component_info(file_path: Path) -> Dict[str, Any]:
    """Extract component information from a TypeScript/React file."""
    content = file_path.read_text()
    
    info = {
        "name": file_path.stem,
        "path": str(file_path),
        "type": "unknown",
        "exports": [],
        "imports": [],
        "props": [],
        "functions": []
    }
    
    # Detect file type
    if file_path.suffix in ['.tsx', '.jsx']:
        info["type"] = "component"
    elif 'Service' in file_path.stem:
        info["type"] = "service"
    elif file_path.suffix == '.ts':
        info["type"] = "module"
    
    # Extract exports
    export_matches = re.findall(r'export\s+(?:const|function|class|interface|type)\s+(\w+)', content)
    info["exports"] = export_matches
    
    # Extract imports
    import_matches = re.findall(r"import\s+(?:{[^}]+}|\w+)\s+from\s+['\"]([^'\"]+)['\"]", content)
    info["imports"] = import_matches
    
    # Extract interface props (for components)
    props_match = re.search(r'interface\s+\w+Props\s*{([^}]+)}', content)
    if props_match:
        props_content = props_match.group(1)
        prop_names = re.findall(r'(\w+)\s*[?:]', props_content)
        info["props"] = prop_names
    
    # Extract function names
    func_matches = re.findall(r'(?:async\s+)?(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*(?::\s*\w+)?\s*=>)', content)
    info["functions"] = [f[0] or f[1] for f in func_matches if f[0] or f[1]]
    
    return info


def generate_unit_tests_for_component(component_info: Dict[str, Any], ticket: str) -> str:
    """Generate unit tests for a React component."""
    component_name = component_info["name"]
    
    imports = f"import {{ render, screen, fireEvent }} from '@testing-library/react';\n"
    imports += f"import {{ {component_name} }} from '../generated/{component_name}';"
    
    test_cases = []
    
    # Basic render test
    test_cases.append(TEST_CASE_TEMPLATE.format(
        test_name=f"renders {component_name} without crashing",
        arrange=f"// Component: {component_name}",
        act=f"render(<{component_name} />);",
        assert=f"expect(screen.getByText(/{component_name}/i)).toBeInTheDocument();"
    ))
    
    # Props test if component has props
    if component_info.get("props"):
        props_str = ", ".join(f"{p}: 'test'" for p in component_info["props"][:3])
        test_cases.append(TEST_CASE_TEMPLATE.format(
            test_name=f"renders with props",
            arrange=f"const props = {{ {props_str} }};",
            act=f"render(<{component_name} {{...props}} />);",
            assert="expect(screen.getByText(/test/i)).toBeInTheDocument();"
        ))
    
    # Snapshot test
    test_cases.append(TEST_CASE_TEMPLATE.format(
        test_name="matches snapshot",
        arrange="",
        act=f"const {{ container }} = render(<{component_name} />);",
        assert="expect(container).toMatchSnapshot();"
    ))
    
    return UNIT_TEST_TEMPLATE.format(
        imports=imports,
        test_suite_name=component_name,
        test_cases="\n".join(test_cases)
    )


def generate_unit_tests_for_service(service_info: Dict[str, Any], ticket: str) -> str:
    """Generate unit tests for a service."""
    service_name = service_info["name"]
    
    imports = f"import {{ {service_name}Service }} from '../generated/{service_name}Service';\n"
    imports += "import pb from '../../lib/pocketbase';\n\n"
    imports += "vi.mock('../../lib/pocketbase');"
    
    test_cases = []
    
    # Test each service method
    methods = ["getAll", "getById", "create", "update", "delete"]
    
    for method in methods:
        if method == "getAll":
            test_cases.append(TEST_CASE_TEMPLATE.format(
                test_name=f"{method} returns array of records",
                arrange="const mockData = [{ id: '1' }, { id: '2' }];\n    vi.mocked(pb.collection).mockReturnValue({ getFullList: vi.fn().mockResolvedValue(mockData) } as any);",
                act=f"const result = await {service_name}Service.{method}();",
                assert="expect(result).toEqual(mockData);\n    expect(result).toHaveLength(2);"
            ))
        elif method == "getById":
            test_cases.append(TEST_CASE_TEMPLATE.format(
                test_name=f"{method} returns single record",
                arrange="const mockData = { id: '1', name: 'Test' };\n    vi.mocked(pb.collection).mockReturnValue({ getOne: vi.fn().mockResolvedValue(mockData) } as any);",
                act=f"const result = await {service_name}Service.{method}('1');",
                assert="expect(result).toEqual(mockData);"
            ))
        elif method == "create":
            test_cases.append(TEST_CASE_TEMPLATE.format(
                test_name=f"{method} creates new record",
                arrange="const newData = { name: 'New Item' };\n    const mockResult = { id: '1', ...newData };\n    vi.mocked(pb.collection).mockReturnValue({ create: vi.fn().mockResolvedValue(mockResult) } as any);",
                act=f"const result = await {service_name}Service.{method}(newData);",
                assert="expect(result.id).toBe('1');"
            ))
    
    return UNIT_TEST_TEMPLATE.format(
        imports=imports,
        test_suite_name=f"{service_name}Service",
        test_cases="\n".join(test_cases)
    )


def generate_e2e_tests(feature_name: str, ticket: str) -> str:
    """Generate E2E tests for a feature."""
    test_cases = []
    
    # Basic navigation test
    test_cases.append(E2E_CASE_TEMPLATE.format(
        test_name=f"can access {feature_name} page",
        url="/",
        title_pattern="CMS",
        steps="// TODO: Add navigation to feature\n    // await page.click('text=Feature');"
    ))
    
    # Feature interaction test
    test_cases.append(E2E_CASE_TEMPLATE.format(
        test_name=f"{feature_name} functionality works",
        url="/",
        title_pattern="CMS",
        steps=f"// TODO: Test {feature_name} specific functionality"
    ))
    
    return E2E_TEST_TEMPLATE.format(
        feature_name=feature_name,
        ticket=ticket,
        test_cases="\n".join(test_cases)
    )


def main():
    parser = argparse.ArgumentParser(description="Test Generator Agent")
    parser.add_argument("--source", "-s", required=True, help="Source directory with generated code")
    parser.add_argument("--output", "-o", required=True, help="Output directory for tests")
    parser.add_argument("--ticket", "-t", default="SCRUM-XXX", help="JIRA ticket key")
    parser.add_argument("--type", choices=["unit", "e2e", "all"], default="all", help="Test type to generate")
    
    args = parser.parse_args()
    
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "generated_tests": []
    }
    
    try:
        source_dir = Path(args.source)
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🧪 Generating tests for: {source_dir}")
        print(f"📁 Output: {output_dir}")
        
        # Find source files
        source_files = list(source_dir.glob("*.ts")) + list(source_dir.glob("*.tsx"))
        
        if not source_files:
            print("⚠️ No source files found")
            result["status"] = "warning"
            result["message"] = "No source files found"
        else:
            for source_file in source_files:
                if source_file.name.endswith('.test.ts') or source_file.name.endswith('.test.tsx'):
                    continue
                
                print(f"  📄 Processing: {source_file.name}")
                
                # Extract component info
                info = extract_component_info(source_file)
                
                # Generate appropriate tests
                if args.type in ["unit", "all"]:
                    if info["type"] == "component":
                        test_code = generate_unit_tests_for_component(info, args.ticket)
                    elif info["type"] == "service":
                        test_code = generate_unit_tests_for_service(info, args.ticket)
                    else:
                        continue
                    
                    # Write test file
                    test_file = output_dir / f"{info['name']}.test.tsx"
                    test_file.write_text(test_code)
                    
                    result["generated_tests"].append({
                        "source": str(source_file),
                        "test": str(test_file),
                        "type": "unit"
                    })
                    print(f"    ✅ Created: {test_file.name}")
            
            # Generate E2E tests
            if args.type in ["e2e", "all"] and source_files:
                feature_name = source_dir.name or "Feature"
                e2e_code = generate_e2e_tests(feature_name, args.ticket)
                
                e2e_dir = output_dir.parent.parent / "tests" / "e2e"
                e2e_dir.mkdir(parents=True, exist_ok=True)
                e2e_file = e2e_dir / f"{feature_name.lower()}.spec.ts"
                e2e_file.write_text(e2e_code)
                
                result["generated_tests"].append({
                    "source": str(source_dir),
                    "test": str(e2e_file),
                    "type": "e2e"
                })
                print(f"  ✅ E2E tests: {e2e_file}")
        
        print(f"\n✅ Test generation complete! {len(result['generated_tests'])} test files created.")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"❌ Error: {e}")
    
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
