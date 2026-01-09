#!/usr/bin/env python
"""
SDLC Pipeline Runner - CI/CD Entry Point
JIRA: SCRUM-85

This is the main entry point for running SDLC pipeline from CI/CD.
It orchestrates the AI agents based on the pipeline phase.

Usage:
    python run_pipeline.py --phase requirements --ticket SCRUM-85 --description "Feature description"
    python run_pipeline.py --phase code_generation --ticket SCRUM-85 --description "Feature description"
    python run_pipeline.py --phase all --ticket SCRUM-85 --description "Feature description"
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

# Phase definitions
PHASES = {
    "requirements": {
        "name": "Requirements Analysis",
        "agent": "requirements_agent.py",
        "description": "Analyze JIRA ticket and extract requirements"
    },
    "code_generation": {
        "name": "Code Generation",
        "agent": "code_generator_agent.py",
        "description": "Generate code from requirements"
    },
    "test_generation": {
        "name": "Test Generation",
        "agent": "test_generator_agent.py",
        "description": "Generate tests for generated code"
    },
    "code_review": {
        "name": "Code Review",
        "agent": "code_reviewer_agent.py",
        "description": "Review code for quality and security"
    }
}


def run_agent(agent_name: str, args: List[str]) -> Dict[str, Any]:
    """Run an agent script and return results."""
    agent_path = Path(__file__).parent / "agents" / agent_name
    
    if not agent_path.exists():
        return {"status": "error", "error": f"Agent not found: {agent_name}"}
    
    cmd = [sys.executable, str(agent_path)] + args
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "Agent execution timed out"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_pipeline(
    phases: List[str],
    ticket: str,
    description: str,
    output_dir: str
) -> Dict[str, Any]:
    """Run the specified pipeline phases."""
    
    results = {
        "ticket": ticket,
        "timestamp": datetime.now().isoformat(),
        "phases": {},
        "status": "success"
    }
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print(f"🚀 SDLC Pipeline - {ticket}")
    print("=" * 60)
    
    for phase in phases:
        if phase not in PHASES:
            print(f"⚠️ Unknown phase: {phase}")
            continue
        
        phase_info = PHASES[phase]
        print(f"\n{'─' * 60}")
        print(f"📋 Phase: {phase_info['name']}")
        print(f"{'─' * 60}")
        
        # Build agent arguments
        agent_args = []
        
        if phase == "requirements":
            agent_args = [
                "--ticket", ticket,
                "--output", str(output_path / "requirements.json")
            ]
            if description:
                agent_args.extend(["--description", description])
        
        elif phase == "code_generation":
            agent_args = [
                "--ticket", ticket,
                "--summary", description or "Feature implementation",
                "--output", str(output_path / "generated"),
                "--with-tests"
            ]
        
        elif phase == "test_generation":
            agent_args = [
                "--source", str(output_path / "generated"),
                "--output", str(output_path / "tests"),
                "--ticket", ticket
            ]
        
        elif phase == "code_review":
            agent_args = [
                "--source", str(output_path / "generated"),
                "--output", str(output_path / "review_report.md")
            ]
        
        # Run the agent
        result = run_agent(phase_info["agent"], agent_args)
        results["phases"][phase] = result
        
        if result["status"] == "success":
            print(f"✅ {phase_info['name']} completed")
        else:
            print(f"❌ {phase_info['name']} failed: {result.get('error', result.get('stderr', 'Unknown error'))}")
            results["status"] = "failed"
            
            # Stop on failure unless continuing
            if phase in ["requirements", "code_generation"]:
                break
    
    # Write summary
    summary_file = output_path / "pipeline_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"📊 Pipeline {'Completed' if results['status'] == 'success' else 'Failed'}")
    print(f"📁 Output: {output_path}")
    print(f"{'=' * 60}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="SDLC Pipeline Runner")
    parser.add_argument("--phase", "-p", 
                        choices=list(PHASES.keys()) + ["all"],
                        default="all",
                        help="Pipeline phase to run")
    parser.add_argument("--ticket", "-t", required=True, help="JIRA ticket key")
    parser.add_argument("--description", "-d", default="", help="Feature description")
    parser.add_argument("--output", "-o", default="./output/pipeline", help="Output directory")
    
    args = parser.parse_args()
    
    # Determine phases to run
    if args.phase == "all":
        phases = list(PHASES.keys())
    else:
        phases = [args.phase]
    
    # Run pipeline
    results = run_pipeline(
        phases=phases,
        ticket=args.ticket,
        description=args.description,
        output_dir=args.output
    )
    
    return 0 if results["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
