#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
compile_ega_harness.py - Expectation-Grounded Alignment (EGA) Compiler

Takes a user goal, generates a Short ID (EGA-<HEX4>), and compiles:
1. task_graph.json (DAG of micro-chunked atomic nodes with persona_role, grounding_concepts & depends_on)
2. verify_static.py (Domain-aware task-specific deterministic verifier script)
3. rubric.json (Expectation Rubric for Blinded LLM-as-a-Judge)
4. tasks/task_XX_spec.md (Isolated worker directives with persona role priming)
5. tasks/task_XX_judge_prompt.md (Directive for Blinded Judge subagent)
"""

import os
import sys
import json
import secrets
import argparse
from pathlib import Path

def generate_short_id():
    return f"EGA-{secrets.token_hex(2).upper()}"

def init_harness_workspace(short_id, base_dir=None):
    if base_dir is None:
        base_dir = Path.cwd()
    else:
        base_dir = Path(base_dir)

    harness_dir = base_dir / ".gemini" / "harness" / short_id
    tasks_dir = harness_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    return harness_dir, tasks_dir

def create_default_task_graph(short_id, goal_summary, domain="general", persona_role="Builder-Coder", grounding_concepts=None):
    if grounding_concepts is None:
        grounding_concepts = []

    return {
        "short_id": short_id,
        "goal_summary": goal_summary,
        "domain": domain,
        "nodes": [
            {
                "id": "node_01",
                "name": "Initial Implementation Pass",
                "persona_role": persona_role,
                "grounding_concepts": grounding_concepts,
                "depends_on": [],
                "compile_html": False,
                "spec_file": f".gemini/harness/{short_id}/tasks/task_01_spec.md",
                "judge_prompt": f".gemini/harness/{short_id}/tasks/task_01_judge_prompt.md",
                "target_artifact": f".gemini/harness/{short_id}/deliverable.md",
                "static_verifier": f".gemini/harness/{short_id}/verify_static.py",
                "dynamic_rubric": f".gemini/harness/{short_id}/rubric.json",
                "status": "PENDING",
                "retry_count": 0,
                "max_retries": 3
            }
        ]
    }

def create_domain_static_verifier(domain, target_artifact):
    """Generates domain-aware deterministic static verifiers."""
    domain_norm = domain.lower() if domain else "general"

    if domain_norm in ["python", "py"]:
        return f"""#!/usr/bin/env python3
# Copyright 2026 Google LLC
# Domain-Aware Static Verifier: Python Architecture
import sys
import json
import subprocess
import ast
from pathlib import Path

def main():
    artifact_path = Path("{target_artifact}")
    errors = []

    if not artifact_path.exists():
        print(json.dumps({{"status": "FAIL", "errors": [f"Target artifact missing: {{artifact_path}}"]}}, indent=2))
        sys.exit(1)

    # 1. Check Python syntax / AST compilation
    if artifact_path.suffix == ".py":
        try:
            code = artifact_path.read_text(encoding="utf-8")
            ast.parse(code, filename=str(artifact_path))
        except SyntaxError as e:
            errors.append(f"Python SyntaxError at line {{e.lineno}}: {{e.msg}}")
        except Exception as e:
            errors.append(f"AST Parse Error: {{str(e)}}")

        # 2. Check for prohibited placeholders
        prohibited = ["TBD", "TODO", "pass  # TODO"]
        for p in prohibited:
            if p in code:
                errors.append(f"Contains prohibited placeholder: '{{p}}'")
    else:
        # Markdown / Doc check for Python projects
        content = artifact_path.read_text(encoding="utf-8")
        if len(content.split()) < 50:
            errors.append("Document content too short (< 50 words)")

    if errors:
        print(json.dumps({{"status": "FAIL", "errors": errors}}, indent=2))
        sys.exit(1)

    print(json.dumps({{"status": "PASS"}}, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
"""
    elif domain_norm in ["node", "javascript", "js", "typescript", "ts"]:
        return f"""#!/usr/bin/env python3
# Copyright 2026 Google LLC
# Domain-Aware Static Verifier: JavaScript / Node Architecture
import sys
import json
import subprocess
from pathlib import Path

def main():
    artifact_path = Path("{target_artifact}")
    errors = []

    if not artifact_path.exists():
        print(json.dumps({{"status": "FAIL", "errors": [f"Target artifact missing: {{artifact_path}}"]}}, indent=2))
        sys.exit(1)

    if artifact_path.suffix in [".js", ".mjs", ".cjs"]:
        res = subprocess.run(["node", "-c", str(artifact_path)], capture_output=True, text=True)
        if res.returncode != 0:
            errors.append(f"Node syntax check failed: {{res.stderr or res.stdout}}")

    content = artifact_path.read_text(encoding="utf-8")
    for term in ["TBD", "TODO"]:
        if term in content:
            errors.append(f"Contains prohibited placeholder: '{{term}}'")

    if errors:
        print(json.dumps({{"status": "FAIL", "errors": errors}}, indent=2))
        sys.exit(1)

    print(json.dumps({{"status": "PASS"}}, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
"""
    elif domain_norm in ["markdown", "doc", "docs", "documentation"]:
        return f"""#!/usr/bin/env python3
# Copyright 2026 Google LLC
# Domain-Aware Static Verifier: Documentation & Specification
import sys
import json
import re
from pathlib import Path

def main():
    artifact_path = Path("{target_artifact}")
    errors = []

    if not artifact_path.exists():
        print(json.dumps({{"status": "FAIL", "errors": [f"Target artifact missing: {{artifact_path}}"]}}, indent=2))
        sys.exit(1)

    content = artifact_path.read_text(encoding="utf-8")
    words = len(content.split())
    if words < 100:
        errors.append(f"Document too short ({{words}} words, minimum is 100)")

    # Check prohibited placeholders
    prohibited = ["TBD", "TODO", "as an AI"]
    for term in prohibited:
        if re.search(rf"\\b{{re.escape(term)}}\\b", content, re.IGNORECASE):
            errors.append(f"Contains prohibited placeholder: '{{term}}'")

    # Check local markdown file links
    file_links = re.findall(r"\\[.*?\\]\\((file:///[^\\)]+)\\)", content)
    for link in file_links:
        clean_path = link.replace("file://", "").split("#")[0]
        if not Path(clean_path).exists():
            errors.append(f"Broken file link: {{link}}")

    if errors:
        print(json.dumps({{"status": "FAIL", "errors": errors}}, indent=2))
        sys.exit(1)

    print(json.dumps({{"status": "PASS"}}, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
"""
    else:
        # Default General Verifier
        return f"""#!/usr/bin/env python3
# Copyright 2026 Google LLC
# Default General Deterministic Static Verifier
import sys
import json
import re
from pathlib import Path

def main():
    artifact_path = Path("{target_artifact}")
    if not artifact_path.exists():
        print(json.dumps({{"status": "FAIL", "errors": [f"Artifact file missing: {{artifact_path}}"]}}, indent=2))
        sys.exit(1)

    content = artifact_path.read_text(encoding="utf-8")
    errors = []

    # Check minimum word count
    words = len(content.split())
    if words < 100:
        errors.append(f"Content too short ({{words}} words, minimum is 100)")

    # Check for placeholder terms
    prohibited = ["TBD", "TODO", "as an AI"]
    for term in prohibited:
        if re.search(rf"\\b{{re.escape(term)}}\\b", content, re.IGNORECASE):
            errors.append(f"Contains prohibited placeholder: '{{term}}'")

    if errors:
        print(json.dumps({{"status": "FAIL", "errors": errors}}, indent=2))
        sys.exit(1)

    print(json.dumps({{"status": "PASS"}}, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
"""

def create_default_rubric(short_id):
    return {
        "rubric_id": f"RUBRIC-{short_id}",
        "short_id": short_id,
        "criteria": [
            {
                "id": "completeness",
                "name": "Requirement Completeness",
                "description": "Does the artifact fully address all constraints specified in the user goal?",
                "threshold": 8
            },
            {
                "id": "clarity_and_structure",
                "name": "Clarity & Structural Precision",
                "description": "Is the content well-organized with clean typography, clear headings, high-contrast tables, and zero visual overlap?",
                "threshold": 8
            },
            {
                "id": "verifiability",
                "name": "Verifiability & Fact Grounding",
                "description": "Are claims supported by data, logic, or explicit source references?",
                "threshold": 8
            },
            {
                "id": "scope_and_formatting",
                "name": "Scope & Formatting Appropriateness",
                "description": "Is the deliverable format appropriate? Are internal artifacts kept in raw Markdown without unnecessary HTML file compilation or visual bloat?",
                "threshold": 8
            }
        ]
    }

def create_blinded_judge_prompt(short_id, node_id, target_artifact, rubric_path):
    return f"""# BLINDED JUDGE DIRECTIVE: EVALUATION OF {node_id} ({short_id})

You are an objective, third-party Quality Audit Judge. Your sole task is to evaluate the deliverable artifact at `{target_artifact}` against the Expectation Rubric defined at `{rubric_path}`.

## EXPLICIT CONSTRAINTS:
1. You MUST read the deliverable file from disk using `view_file`.
2. You MUST read the rubric JSON from disk using `view_file`.
3. You have NO prior context about how this document or code was generated. Evaluate it strictly as an author-blind submission.
4. Do NOT give benefit of the doubt. If a rubric criterion is unmet or partially met below the threshold, fail the criterion.

## REQUIRED OUTPUT FORMAT:
Save your verdict to `.gemini/harness/{short_id}/{node_id}_judge_verdict.json`:

```json
{{
  "status": "PASS" | "FAIL",
  "overall_score": 8.5,
  "criteria_scores": {{
    "completeness": 8,
    "clarity_and_structure": 9,
    "verifiability": 8.5
  }},
  "defects": [
    {{
      "criterion_id": "completeness",
      "issue": "Section 3 is missing required error handling documentation.",
      "remediation": "Add an explicit error handling section with code examples."
    }}
  ]
}}
```
"""

def main():
    parser = argparse.ArgumentParser(description="Expectation-Grounded Alignment (EGA) Compiler")
    parser.add_argument("goal", nargs="?", default="Build Expectation-Grounded Deliverable", help="User goal or task summary")
    parser.add_argument("persona", nargs="?", default="Builder-Coder", help="Persona role (e.g. Architect-Blueprint, Builder-Coder)")
    parser.add_argument("--domain", "-d", default="general", choices=["general", "python", "node", "javascript", "markdown", "doc", "okf"], help="Domain domain for static verifier specialization")
    parser.add_argument("--persona-role", "-p", help="Override persona role")

    args = parser.parse_args()
    goal = args.goal
    persona_role = args.persona_role if args.persona_role else args.persona
    domain = args.domain

    short_id = generate_short_id()
    harness_dir, tasks_dir = init_harness_workspace(short_id)

    # 1. Save Task Graph
    graph = create_default_task_graph(short_id, goal, domain=domain, persona_role=persona_role)
    with open(harness_dir / "task_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    # 2. Save Static Verifier Script
    target_artifact = harness_dir / "deliverable.md"
    verifier_script = create_domain_static_verifier(domain, target_artifact)
    verifier_path = harness_dir / "verify_static.py"
    with open(verifier_path, "w", encoding="utf-8") as f:
        f.write(verifier_script)
    os.chmod(verifier_path, 0o755)

    # 3. Save Dynamic Rubric JSON
    rubric = create_default_rubric(short_id)
    rubric_path = harness_dir / "rubric.json"
    with open(rubric_path, "w", encoding="utf-8") as f:
        json.dump(rubric, f, indent=2)

    # 4. Save Task 01 Spec Directive
    spec_content = f"""# TASK 01 SPECIFICATION ({short_id})

## GOAL:
{goal}

## PERSONA ROLE PRIMING:
Role: `{persona_role}`

## TARGET ARTIFACT:
`{target_artifact}`

## EXPECTATION CONTRACT:
1. Static Verifier: `{verifier_path}`
2. Dynamic Rubric: `{rubric_path}`

## INSTRUCTIONS:
Operate under the cognitive mandate of `{persona_role}`.
Execute the implementation to satisfy the goal and save your complete deliverable to `{target_artifact}`.
Ensure no placeholders ('TBD', 'TODO') are left in the artifact.
"""
    with open(tasks_dir / "task_01_spec.md", "w", encoding="utf-8") as f:
        f.write(spec_content)

    # 5. Save Blinded Judge Directive Prompt
    judge_prompt_content = create_blinded_judge_prompt(short_id, "node_01", target_artifact, rubric_path)
    with open(tasks_dir / "task_01_judge_prompt.md", "w", encoding="utf-8") as f:
        f.write(judge_prompt_content)

    print(f"SUCCESS: Compiled EGA Harness {short_id} (Domain: {domain}) at {harness_dir}")

if __name__ == "__main__":
    main()
