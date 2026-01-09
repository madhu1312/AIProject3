#!/usr/bin/env python
"""
Code Reviewer Agent - CI/CD Pipeline Interface
JIRA: SCRUM-85

This script wraps the code review agents for use in the AI SDLC pipeline.
It performs automated code review on generated/modified files.

Usage:
    python code_reviewer_agent.py --source ../frontend/src/generated --output review_report.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from agents.code_review import (
        review_code_security, 
        review_code_quality,
        review_react_patterns, 
        full_code_review
    )
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False


# Review patterns
SECURITY_PATTERNS = {
    "sql_injection": {
        "pattern": r"(query|exec|execute)\s*\(\s*[\"'`].*\+|(\$\{|\%s)",
        "severity": "critical",
        "message": "Potential SQL injection vulnerability. Use parameterized queries."
    },
    "xss_vulnerability": {
        "pattern": r"dangerouslySetInnerHTML|innerHTML\s*=|document\.write",
        "severity": "high",
        "message": "Potential XSS vulnerability. Sanitize user input before rendering."
    },
    "hardcoded_secrets": {
        "pattern": r"(password|secret|api_key|apikey|token)\s*=\s*[\"'][^\"']{8,}[\"']",
        "severity": "critical",
        "message": "Hardcoded secret detected. Use environment variables."
    },
    "eval_usage": {
        "pattern": r"\beval\s*\(|new\s+Function\s*\(",
        "severity": "high",
        "message": "Dangerous eval() or Function() usage detected."
    },
    "console_log": {
        "pattern": r"console\.(log|debug|info)\s*\(",
        "severity": "low",
        "message": "Console statement found. Remove before production."
    }
}

QUALITY_PATTERNS = {
    "any_type": {
        "pattern": r":\s*any\b",
        "severity": "medium",
        "message": "Using 'any' type defeats TypeScript's purpose."
    },
    "empty_catch": {
        "pattern": r"catch\s*\([^)]*\)\s*\{\s*\}",
        "severity": "medium",
        "message": "Empty catch block. Handle or log the error."
    },
    "todo_comment": {
        "pattern": r"//\s*TODO|/\*\s*TODO",
        "severity": "info",
        "message": "TODO comment found. Address before release."
    },
    "magic_numbers": {
        "pattern": r"(?<![.\w\-])\b\d{3,}\b(?![.\w])",
        "severity": "low",
        "message": "Magic number detected. Consider using named constants."
    },
    "long_line": {
        "pattern": r".{120,}",
        "severity": "info",
        "message": "Line exceeds 120 characters."
    }
}

REACT_PATTERNS = {
    "missing_key": {
        "pattern": r"\.map\s*\([^)]+\)\s*=>\s*\(\s*<(?!.*\bkey\s*=)",
        "severity": "medium",
        "message": "List rendering may be missing 'key' prop."
    },
    "direct_state_mutation": {
        "pattern": r"useState\(\)\[0\]\s*\.\w+\s*=|\.push\(|\.pop\(|\.shift\(",
        "severity": "high",
        "message": "Potential direct state mutation. Use spread operator or setState."
    },
    "missing_dependency": {
        "pattern": r"useEffect\s*\(\s*\(\s*\)\s*=>\s*\{[^}]*\b(props|state)\b[^}]*\}\s*,\s*\[\s*\]\s*\)",
        "severity": "medium",
        "message": "useEffect may have missing dependencies."
    }
}


def analyze_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single file for issues."""
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')
    
    issues = []
    
    # Check security patterns
    for name, pattern_info in SECURITY_PATTERNS.items():
        matches = list(re.finditer(pattern_info["pattern"], content, re.IGNORECASE))
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                "type": "security",
                "name": name,
                "severity": pattern_info["severity"],
                "message": pattern_info["message"],
                "line": line_num,
                "snippet": lines[line_num - 1].strip()[:80] if line_num <= len(lines) else ""
            })
    
    # Check quality patterns
    for name, pattern_info in QUALITY_PATTERNS.items():
        if name == "long_line":
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    issues.append({
                        "type": "quality",
                        "name": name,
                        "severity": pattern_info["severity"],
                        "message": pattern_info["message"],
                        "line": i,
                        "snippet": line[:50] + "..."
                    })
        else:
            matches = list(re.finditer(pattern_info["pattern"], content))
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "quality",
                    "name": name,
                    "severity": pattern_info["severity"],
                    "message": pattern_info["message"],
                    "line": line_num,
                    "snippet": lines[line_num - 1].strip()[:80] if line_num <= len(lines) else ""
                })
    
    # Check React patterns (for .tsx files)
    if file_path.suffix == '.tsx':
        for name, pattern_info in REACT_PATTERNS.items():
            matches = list(re.finditer(pattern_info["pattern"], content))
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "react",
                    "name": name,
                    "severity": pattern_info["severity"],
                    "message": pattern_info["message"],
                    "line": line_num,
                    "snippet": lines[line_num - 1].strip()[:80] if line_num <= len(lines) else ""
                })
    
    return {
        "file": str(file_path),
        "lines": len(lines),
        "issues": issues,
        "issue_count": len(issues)
    }


def calculate_score(issues: List[Dict]) -> Tuple[int, str]:
    """Calculate overall code quality score."""
    score = 100
    
    severity_weights = {
        "critical": 25,
        "high": 15,
        "medium": 8,
        "low": 3,
        "info": 1
    }
    
    for issue in issues:
        score -= severity_weights.get(issue.get("severity", "info"), 1)
    
    score = max(0, score)
    
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    return score, grade


def generate_markdown_report(results: List[Dict], output_path: Path) -> None:
    """Generate a markdown report from review results."""
    all_issues = []
    for r in results:
        all_issues.extend(r.get("issues", []))
    
    score, grade = calculate_score(all_issues)
    
    report = f"""# 📝 Code Review Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Files Reviewed:** {len(results)}
**Total Issues:** {len(all_issues)}
**Quality Score:** {score}/100 ({grade})

---

## 📊 Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | {sum(1 for i in all_issues if i.get('severity') == 'critical')} |
| 🟠 High | {sum(1 for i in all_issues if i.get('severity') == 'high')} |
| 🟡 Medium | {sum(1 for i in all_issues if i.get('severity') == 'medium')} |
| 🔵 Low | {sum(1 for i in all_issues if i.get('severity') == 'low')} |
| ⚪ Info | {sum(1 for i in all_issues if i.get('severity') == 'info')} |

---

## 📁 File Details

"""
    
    for result in results:
        file_name = Path(result["file"]).name
        issue_count = result.get("issue_count", 0)
        
        if issue_count == 0:
            report += f"### ✅ {file_name}\n\nNo issues found.\n\n"
        else:
            report += f"### {'⚠️' if issue_count < 5 else '❌'} {file_name}\n\n"
            report += f"**Lines:** {result.get('lines', 0)} | **Issues:** {issue_count}\n\n"
            
            for issue in result.get("issues", []):
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵",
                    "info": "⚪"
                }.get(issue.get("severity", "info"), "⚪")
                
                report += f"- {severity_emoji} **Line {issue.get('line', '?')}:** {issue.get('message', 'Unknown issue')}\n"
                if issue.get("snippet"):
                    report += f"  ```\n  {issue['snippet']}\n  ```\n"
            
            report += "\n"
    
    report += """---

## 🔧 Recommendations

"""
    
    if any(i.get("severity") == "critical" for i in all_issues):
        report += "1. **Fix all critical issues immediately** - Security vulnerabilities detected.\n"
    if any(i.get("name") == "any_type" for i in all_issues):
        report += "2. **Replace `any` types** with specific TypeScript types.\n"
    if any(i.get("name") == "todo_comment" for i in all_issues):
        report += "3. **Address TODO comments** before production deployment.\n"
    if any(i.get("name") == "console_log" for i in all_issues):
        report += "4. **Remove console statements** or replace with proper logging.\n"
    
    report += "\n---\n*Generated by Code Reviewer Agent*\n"
    
    output_path.write_text(report)


def main():
    parser = argparse.ArgumentParser(description="Code Reviewer Agent")
    parser.add_argument("--source", "-s", required=True, help="Source directory or file to review")
    parser.add_argument("--output", "-o", required=True, help="Output report file (markdown)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--fail-on", choices=["critical", "high", "medium", "low", "none"], 
                        default="critical", help="Fail if issues of this severity or higher are found")
    
    args = parser.parse_args()
    
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "files_reviewed": [],
        "total_issues": 0
    }
    
    try:
        source_path = Path(args.source)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"📝 Reviewing code in: {source_path}")
        
        # Find files to review
        if source_path.is_file():
            files = [source_path]
        else:
            files = list(source_path.glob("**/*.ts")) + list(source_path.glob("**/*.tsx"))
            # Exclude test files and node_modules
            files = [f for f in files if 'node_modules' not in str(f) and '.test.' not in str(f)]
        
        if not files:
            print("⚠️ No files to review")
            result["message"] = "No files found"
        else:
            review_results = []
            
            for file_path in files:
                print(f"  📄 Reviewing: {file_path.name}")
                file_result = analyze_file(file_path)
                review_results.append(file_result)
                result["total_issues"] += file_result["issue_count"]
                
                if file_result["issue_count"] > 0:
                    print(f"    ⚠️ {file_result['issue_count']} issues found")
                else:
                    print(f"    ✅ No issues")
            
            result["files_reviewed"] = review_results
            
            # Generate report
            if args.format == "markdown":
                generate_markdown_report(review_results, output_path)
            else:
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2)
            
            print(f"\n📊 Review complete!")
            print(f"   Files: {len(files)}")
            print(f"   Issues: {result['total_issues']}")
            print(f"   Report: {output_path}")
            
            # Check fail condition
            all_issues = []
            for r in review_results:
                all_issues.extend(r.get("issues", []))
            
            severity_levels = ["critical", "high", "medium", "low"]
            if args.fail_on != "none":
                fail_severities = severity_levels[:severity_levels.index(args.fail_on) + 1]
                blocking_issues = [i for i in all_issues if i.get("severity") in fail_severities]
                
                if blocking_issues:
                    result["status"] = "failed"
                    result["blocking_issues"] = len(blocking_issues)
                    print(f"\n❌ Review failed: {len(blocking_issues)} blocking issues")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"❌ Error: {e}")
    
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
