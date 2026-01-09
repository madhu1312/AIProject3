#!/usr/bin/env python
"""
Code Generator Agent - CI/CD Pipeline Interface
JIRA: SCRUM-85

This script wraps the code generation agents for use in the AI SDLC pipeline.
It can be called from GitHub Actions to generate code from requirements.

Usage:
    python code_generator_agent.py --ticket SCRUM-85 --summary "Add new feature" --output ../frontend/src/generated
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from agents.code_generator import (
        generate_react_component, 
        generate_service,
        generate_type_definition,
        generate_from_user_story
    )
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    print("Warning: Laddr code generator not fully available. Using template mode.")


# Templates for code generation
REACT_COMPONENT_TEMPLATE = '''import React, {{ useState }} from 'react';

interface {component_name}Props {{
  // TODO: Define props based on requirements
  className?: string;
}}

/**
 * {component_name} Component
 * 
 * Generated for: {ticket}
 * Summary: {summary}
 * 
 * @generated
 */
export const {component_name}: React.FC<{component_name}Props> = ({{ className }}) => {{
  // TODO: Implement state management
  const [isLoading, setIsLoading] = useState(false);

  // TODO: Implement handlers
  const handleAction = async () => {{
    setIsLoading(true);
    try {{
      // Implementation here
    }} finally {{
      setIsLoading(false);
    }}
  }};

  return (
    <div className={{className}}>
      {{/* TODO: Implement UI based on requirements */}}
      <h2>{component_name}</h2>
      <p>Implementation pending for: {summary}</p>
    </div>
  );
}};

export default {component_name};
'''

SERVICE_TEMPLATE = '''import pb from '../lib/pocketbase';

/**
 * {service_name} Service
 * 
 * Generated for: {ticket}
 * Summary: {summary}
 * 
 * @generated
 */

export interface {entity_name} {{
  id: string;
  // TODO: Define entity fields
  created: string;
  updated: string;
}}

export const {service_name}Service = {{
  /**
   * Get all records
   */
  async getAll(): Promise<{entity_name}[]> {{
    const records = await pb.collection('{collection}').getFullList();
    return records as {entity_name}[];
  }},

  /**
   * Get by ID
   */
  async getById(id: string): Promise<{entity_name}> {{
    return await pb.collection('{collection}').getOne(id) as {entity_name};
  }},

  /**
   * Create new record
   */
  async create(data: Partial<{entity_name}>): Promise<{entity_name}> {{
    return await pb.collection('{collection}').create(data) as {entity_name};
  }},

  /**
   * Update record
   */
  async update(id: string, data: Partial<{entity_name}>): Promise<{entity_name}> {{
    return await pb.collection('{collection}').update(id, data) as {entity_name};
  }},

  /**
   * Delete record
   */
  async delete(id: string): Promise<boolean> {{
    await pb.collection('{collection}').delete(id);
    return true;
  }},
}};
'''

TEST_TEMPLATE = '''import {{ describe, it, expect, beforeEach }} from 'vitest';
import {{ render, screen, fireEvent }} from '@testing-library/react';
import {{ {component_name} }} from './{component_name}';

/**
 * Tests for {component_name}
 * 
 * Generated for: {ticket}
 * 
 * @generated
 */
describe('{component_name}', () => {{
  beforeEach(() => {{
    // Setup before each test
  }});

  it('renders without crashing', () => {{
    render(<{component_name} />);
    expect(screen.getByText(/{component_name}/i)).toBeInTheDocument();
  }});

  it('handles user interaction', async () => {{
    render(<{component_name} />);
    // TODO: Add interaction tests
  }});

  // TODO: Add more tests based on acceptance criteria
}});
'''


def to_pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    # Remove special characters and split
    words = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text).split()
    return ''.join(word.capitalize() for word in words)


def to_camel_case(text: str) -> str:
    """Convert text to camelCase."""
    pascal = to_pascal_case(text)
    return pascal[0].lower() + pascal[1:] if pascal else ''


def generate_component_from_requirements(
    ticket: str,
    summary: str,
    output_dir: Path
) -> Dict[str, Any]:
    """Generate a React component based on requirements."""
    
    # Derive component name from summary
    component_name = to_pascal_case(summary.split()[-2:] if len(summary.split()) > 2 else summary.split())
    if not component_name:
        component_name = f"Feature{ticket.replace('-', '')}"
    
    # Generate component code
    if AGENTS_AVAILABLE:
        try:
            code = generate_react_component(
                component_name=component_name,
                description=summary,
                props=[],
                source=ticket
            )
        except Exception:
            code = REACT_COMPONENT_TEMPLATE.format(
                component_name=component_name,
                ticket=ticket,
                summary=summary
            )
    else:
        code = REACT_COMPONENT_TEMPLATE.format(
            component_name=component_name,
            ticket=ticket,
            summary=summary
        )
    
    # Write component file
    component_file = output_dir / f"{component_name}.tsx"
    component_file.write_text(code)
    
    return {
        "type": "component",
        "name": component_name,
        "path": str(component_file),
        "code_length": len(code)
    }


def generate_service_from_requirements(
    ticket: str,
    summary: str,
    output_dir: Path
) -> Dict[str, Any]:
    """Generate a service based on requirements."""
    
    # Derive service name
    service_name = to_camel_case(summary.split()[-2:] if len(summary.split()) > 2 else summary.split())
    if not service_name:
        service_name = f"feature{ticket.replace('-', '')}"
    
    entity_name = to_pascal_case(service_name)
    collection = service_name.lower() + 's'
    
    # Generate service code
    if AGENTS_AVAILABLE:
        try:
            code = generate_service(
                service_name=service_name,
                entity_name=entity_name,
                collection=collection,
                description=summary,
                source=ticket
            )
        except Exception:
            code = SERVICE_TEMPLATE.format(
                service_name=service_name,
                entity_name=entity_name,
                collection=collection,
                ticket=ticket,
                summary=summary
            )
    else:
        code = SERVICE_TEMPLATE.format(
            service_name=service_name,
            entity_name=entity_name,
            collection=collection,
            ticket=ticket,
            summary=summary
        )
    
    # Write service file
    service_file = output_dir / f"{service_name}Service.ts"
    service_file.write_text(code)
    
    return {
        "type": "service",
        "name": service_name,
        "path": str(service_file),
        "code_length": len(code)
    }


def generate_test_from_requirements(
    ticket: str,
    component_name: str,
    output_dir: Path
) -> Dict[str, Any]:
    """Generate tests for a component."""
    
    code = TEST_TEMPLATE.format(
        component_name=component_name,
        ticket=ticket
    )
    
    # Write test file
    test_file = output_dir / f"{component_name}.test.tsx"
    test_file.write_text(code)
    
    return {
        "type": "test",
        "name": f"{component_name}.test",
        "path": str(test_file),
        "code_length": len(code)
    }


def main():
    parser = argparse.ArgumentParser(description="Code Generator Agent")
    parser.add_argument("--ticket", "-t", required=True, help="JIRA ticket key")
    parser.add_argument("--summary", "-s", required=True, help="Feature summary")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--type", choices=["component", "service", "all"], default="all", 
                        help="What to generate")
    parser.add_argument("--with-tests", action="store_true", help="Also generate tests")
    
    args = parser.parse_args()
    
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "ticket": args.ticket,
        "generated_files": []
    }
    
    try:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🤖 Generating code for: {args.ticket}")
        print(f"📝 Summary: {args.summary}")
        print(f"📁 Output: {output_dir}")
        
        component_name = None
        
        # Generate component
        if args.type in ["component", "all"]:
            print("🔨 Generating React component...")
            comp_result = generate_component_from_requirements(
                args.ticket, args.summary, output_dir
            )
            result["generated_files"].append(comp_result)
            component_name = comp_result["name"]
            print(f"  ✅ Created: {comp_result['path']}")
        
        # Generate service
        if args.type in ["service", "all"]:
            print("🔨 Generating service...")
            svc_result = generate_service_from_requirements(
                args.ticket, args.summary, output_dir
            )
            result["generated_files"].append(svc_result)
            print(f"  ✅ Created: {svc_result['path']}")
        
        # Generate tests
        if args.with_tests and component_name:
            print("🧪 Generating tests...")
            test_dir = output_dir.parent / "__tests__" / "generated"
            test_dir.mkdir(parents=True, exist_ok=True)
            test_result = generate_test_from_requirements(
                args.ticket, component_name, test_dir
            )
            result["generated_files"].append(test_result)
            print(f"  ✅ Created: {test_result['path']}")
        
        # Write manifest
        manifest_file = output_dir / "generated_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n✅ Generation complete! {len(result['generated_files'])} files created.")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"❌ Error: {e}")
    
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
