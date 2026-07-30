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
ega_loop_runner.py - Active Control Loop Runner for Expectation-Grounded Alignment

Monitors and executes the Dual-Verification Gate (Static Check + Dynamic Judge)
for an EGA harness task graph. Handles delta feedback loops, retries, and evidence logging.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def run_static_verifier(script_path):
    if not os.path.exists(script_path):
        return False, [f"Static verifier script not found at {script_path}"]

    res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
        if data.get("status") == "PASS":
            return True, []
        return False, data.get("errors", [res.stderr or res.stdout])
    except json.JSONDecodeError:
        if res.returncode == 0:
            return True, []
        return False, [res.stderr or res.stdout or "Non-JSON exit code failure"]

def evaluate_judge_verdict(verdict_path):
    p = Path(verdict_path)
    if not p.exists():
        return False, ["Judge verdict file missing on disk."]

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        status = data.get("status", "FAIL")
        defects = data.get("defects", [])
        if status == "PASS":
            return True, []
        return False, [f"{d.get('criterion_id')}: {d.get('issue')} (Remediation: {d.get('remediation')})" for d in defects]
    except Exception as e:
        return False, [f"Failed to parse judge verdict: {str(e)}"]

def create_delta_report(node_id, static_errors, judge_errors, attempt, max_retries):
    report = f"""# EGA DUAL-VERIFICATION GATE DELTA REPORT
**Node ID**: {node_id}
**Attempt**: {attempt}/{max_retries}
**Status**: REJECTED - ALIGNMENT REQUIRED

---

## 1. STATIC VERIFIER FAILURES:
"""
    if static_errors:
        for err in static_errors:
            report += f"- [STATIC ERROR] {err}\n"
    else:
        report += "- None (Static checks passed)\n"

    report += "\n## 2. BLINDED DYNAMIC JUDGE DEFECTS:\n"
    if judge_errors:
        for err in judge_errors:
            report += f"- [JUDGE DEFECT] {err}\n"
    else:
        report += "- None (Dynamic judge passed)\n"

    report += """
---

## REQUIRED ACTION:
Re-examine the target deliverable artifact and apply exact remediations for the errors listed above.
Save your revised deliverable to disk before re-running the Dual-Verification Gate.
"""
    return report

def process_node(node, harness_dir):
    node_id = node["id"]
    static_script = node["static_verifier"]
    target_artifact = node["target_artifact"]
    judge_verdict_file = Path(harness_dir) / f"{node_id}_judge_verdict.json"

    print(f"[{node_id}] Running Dual-Verification Gate for {target_artifact}...")

    # 1. Run Deterministic Static Verifier
    static_pass, static_errors = run_static_verifier(static_script)

    # 2. Check Dynamic Blinded Judge Verdict
    judge_pass, judge_errors = evaluate_judge_verdict(judge_verdict_file)

    # Dual Gate Assertion
    if static_pass and judge_pass:
        print(f"[{node_id}] DUAL-GATE VERIFICATION PASSED SUCCESSFULLY!")
        node["status"] = "COMPLETED"
        return True, None
    else:
        node["retry_count"] += 1
        delta_report = create_delta_report(
            node_id,
            static_errors,
            judge_errors,
            node["retry_count"],
            node["max_retries"]
        )
        if node["retry_count"] >= node["max_retries"]:
            node["status"] = "FAILED_CIRCUIT_BREAKER"
            print(f"[{node_id}] CIRCUIT BREAKER TRIGGERED! Exceeded max retries ({node['max_retries']}).")
        else:
            node["status"] = "RETRY_REQUIRED"
            print(f"[{node_id}] DUAL-GATE REJECTED. Delta report generated.")

        return False, delta_report

def main():
    if len(sys.argv) < 2:
        print("Usage: ega_loop_runner.py <SHORT_ID_OR_HARNESS_DIR>")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    if not target_path.is_dir():
        target_path = Path.cwd() / ".gemini" / "harness" / sys.argv[1]

    graph_file = target_path / "task_graph.json"
    if not graph_file.exists():
        print(f"Error: task_graph.json not found in {target_path}")
        sys.exit(1)

    with open(graph_file, "r", encoding="utf-8") as f:
        graph = json.load(f)

    all_passed = True
    for node in graph["nodes"]:
        if node["status"] in ["COMPLETED", "FAILED_CIRCUIT_BREAKER"]:
            continue

        passed, delta_report = process_node(node, target_path)
        if not passed:
            all_passed = False
            # Save Delta Report to disk for the worker subagent
            delta_path = target_path / f"{node['id']}_delta_report.md"
            delta_path.write_text(delta_report, encoding="utf-8")
            print(f"Delta Report saved to: {delta_path}")
            break

    # Update Task Graph State
    with open(graph_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
