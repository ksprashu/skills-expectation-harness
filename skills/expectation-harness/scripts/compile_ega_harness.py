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
1. task_graph.json (DAG of micro-chunked atomic nodes with optional persona_role & grounding_concepts)
2. verify_static.py (Task-specific deterministic Python verifier script)
3. rubric.json (Expectation Rubric for Blinded LLM-as-a-Judge)
4. tasks/task_XX_spec.md (Isolated worker directives with persona role priming)
"""

import os
import sys
import json
import secrets
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
                "spec_file": f".gemini/harness/{short_id}/tasks/task_01_spec.md",
                "target_artifact": f".gemini/harness/{short_id}/deliverable.md",
                "static_verifier": f".gemini/harness/{short_id}/verify_static.py",
                "dynamic_rubric": f".gemini/harness/{short_id}/rubric.json",
                "status": "PENDING",
                "retry_count": 0,
                "max_retries": 3
            }
        ]
    }

def create_default_static_verifier(target_artifact):
    return f"""#!/usr/bin/env python3
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
                "description": "Is the content well-organized with clear headings, tables, or code blocks?",
                "threshold": 8
            },
            {
                "id": "verifiability",
                "name": "Verifiability & Fact Grounding",
                "description": "Are claims supported by data, logic, or explicit source references?",
                "threshold": 8
            }
        ]
    }

def main():
    goal = sys.argv[1] if len(sys.argv) > 1 else "Build Expectation-Grounded Deliverable"
    persona_role = sys.argv[2] if len(sys.argv) > 2 else "Builder-Coder"
    
    short_id = generate_short_id()
    harness_dir, tasks_dir = init_harness_workspace(short_id)

    # 1. Save Task Graph
    graph = create_default_task_graph(short_id, goal, persona_role=persona_role)
    with open(harness_dir / "task_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    # 2. Save Static Verifier Script
    target_artifact = harness_dir / "deliverable.md"
    verifier_script = create_default_static_verifier(target_artifact)
    verifier_path = harness_dir / "verify_static.py"
    with open(verifier_path, "w", encoding="utf-8") as f:
        f.write(verifier_script)
    os.chmod(verifier_path, 0o755)

    # 3. Save Dynamic Rubric JSON
    rubric = create_default_rubric(short_id)
    with open(harness_dir / "rubric.json", "w", encoding="utf-8") as f:
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
2. Dynamic Rubric: `{harness_dir / 'rubric.json'}`

## INSTRUCTIONS:
Operate under the cognitive mandate of `{persona_role}`.
Execute the implementation to satisfy the goal and save your complete deliverable to `{target_artifact}`.
Ensure no placeholders ('TBD', 'TODO') are left in the artifact.
"""
    with open(tasks_dir / "task_01_spec.md", "w", encoding="utf-8") as f:
        f.write(spec_content)

    print(f"SUCCESS: Compiled EGA Harness {short_id} at {harness_dir}")

if __name__ == "__main__":
    main()
