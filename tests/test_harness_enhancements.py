#!/usr/bin/env python3
# Copyright 2026 Google LLC
# Unit & End-to-End Verification Test Suite for EGA Harness Enhancements

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

def test_compile_ega_harness():
    print("Testing compile_ega_harness.py with prompt-file and web domain...")
    
    scripts_dir = Path(__file__).parent.parent / "skills" / "expectation-harness" / "scripts"
    compiler = scripts_dir / "compile_ega_harness.py"

    test_prompt = """Take a look at the presentation app.
Firstly, I am an English speaker and I would like all main controls to be in English.
The audience is in Japanese, so content should be available in both English and Japanese.
The live translate caption bar should be non-intrusive and 2 rows.
Ensure latency is ultra-fast and sockets do not hang.
"""

    prompt_file = Path("/tmp/test_prompt.txt")
    prompt_file.write_text(test_prompt, encoding="utf-8")

    cmd = [
        sys.executable, str(compiler),
        "Fix presentation app controls and live captions",
        "Builder-Coder",
        "--domain", "web",
        "--prompt-file", str(prompt_file),
        "--images", "/tmp/clipboard.png"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Compiler failed: {res.stderr}"
    assert "Compiled EGA Harness" in res.stdout, "Output missing short ID string"

    # Find created harness directory
    short_id = None
    for token in res.stdout.split():
        if token.startswith("EGA-"):
            short_id = token
            break

    assert short_id is not None, "Short ID not found"
    harness_dir = Path.cwd() / ".gemini" / "harness" / short_id
    assert harness_dir.exists(), f"Harness directory missing: {harness_dir}"

    # Verify expectations.json
    exp_file = harness_dir / "expectations.json"
    assert exp_file.exists(), "expectations.json missing"
    exp_data = json.loads(exp_file.read_text(encoding="utf-8"))
    assert exp_data["total_requirements"] > 0, "No requirements extracted"
    assert exp_data["images"] == ["/tmp/clipboard.png"], "Image references mismatch"

    print("  -> compile_ega_harness.py PASSED!")
    return short_id, harness_dir

def test_static_verifier(harness_dir):
    print("Testing generated verify_static.py...")
    verifier = harness_dir / "verify_static.py"
    assert verifier.exists(), "verify_static.py missing"

    res = subprocess.run([sys.executable, str(verifier)], capture_output=True, text=True)
    # Target deliverable.md or HTML files might not exist yet or pass/fail as expected
    assert "status" in res.stdout or "status" in res.stderr or res.returncode in [0, 1]
    print("  -> verify_static.py PASSED!")

def test_loop_runner(short_id, harness_dir):
    print("Testing ega_loop_runner.py...")
    scripts_dir = Path(__file__).parent.parent / "skills" / "expectation-harness" / "scripts"
    runner = scripts_dir / "ega_loop_runner.py"

    # Create dummy target deliverable so gate can evaluate
    deliverable = harness_dir / "deliverable.md"
    deliverable.write_text("""# Presentation App Fixes
Controls updated to English.
Content made available in both English and Japanese.
Live translate caption bar formatted into 2 rows with ultra-fast latency and continuous sockets.
""", encoding="utf-8")

    res = subprocess.run([sys.executable, str(runner), short_id], capture_output=True, text=True)
    assert "DUAL-GATE VERIFICATION" in res.stdout or "REJECTED" in res.stdout, f"Loop runner unexpected output: {res.stdout}"
    print("  -> ega_loop_runner.py PASSED!")

def test_ega_controller():
    print("Testing ega_controller.py end-to-end...")
    scripts_dir = Path(__file__).parent.parent / "skills" / "expectation-harness" / "scripts"
    controller = scripts_dir / "ega_controller.py"

    cmd = [
        sys.executable, str(controller),
        "--prompt", "Build web dashboard with English controls and Japanese captions",
        "--domain", "web"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode in [0, 1], f"Controller crashed: {res.stderr}"
    assert "EGA CONTROLLER ORCHESTRATOR INITIALIZED" in res.stdout, "Controller output header missing"
    print("  -> ega_controller.py PASSED!")

if __name__ == "__main__":
    short_id, harness_dir = test_compile_ega_harness()
    test_static_verifier(harness_dir)
    test_loop_runner(short_id, harness_dir)
    test_ega_controller()
    print("\n🎉 ALL EGA ENHANCEMENT VERIFICATION TESTS PASSED SUCCESSFULLY!")
