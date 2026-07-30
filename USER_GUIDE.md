# Expectation-Grounded Alignment (EGA) User Guide

This guide provides a comprehensive walkthrough for configuring, compiling, and running the **Expectation-Grounded Alignment (EGA)** Engine.

---

## 1. Conceptual Framework: Expectation-Aligned Work (EAW)

EAW replaces subjective agent self-assessment with **empirical contract fulfillment**:

1. **Synthesis**: Before writing code or text, the Orchestrator generates:
   - `task_graph.json` (Atomic micro-chunked node graph)
   - `verify_static.py` (Task-specific deterministic Python script)
   - `rubric.json` (Qualitative expectation criteria schema)
2. **Worker Implementation**: The worker agent receives `tasks/task_XX_spec.md` and generates the deliverable artifact.
3. **Dual-Verification Gate**:
   - **Static Check**: Evaluates deterministic constraints (file existence, word count, syntax, links, table headers, prohibited terms).
   - **Dynamic Judge**: Spawns a fresh subagent with **zero past context** to audit the deliverable against `rubric.json`.
4. **Alignment Delta Loop**: If either gate fails, a `<node_id>_delta_report.md` is generated and fed back into the worker subagent.

---

## 2. Step-by-Step Walkthrough

### Step 1: Initialize the EGA Harness
To compile a harness for a task, run the compiler script with optional domain and persona parameters:

```bash
# Domain-aware compilation (python, node, markdown, okf, general)
python3 skills/expectation-harness/scripts/compile_ega_harness.py "Build REST API Middleware" "Builder-Coder" --domain python
```

This creates the harness directory under `.gemini/harness/EGA-<HEX4>/`:
- `.gemini/harness/EGA-A8F2/task_graph.json` (Includes topological `depends_on` DAG configuration)
- `.gemini/harness/EGA-A8F2/verify_static.py` (Domain-aware deterministic verifier)
- `.gemini/harness/EGA-A8F2/rubric.json` (Dynamic judge schema)
- `.gemini/harness/EGA-A8F2/tasks/task_01_spec.md` (Worker directive)
- `.gemini/harness/EGA-A8F2/tasks/task_01_judge_prompt.md` (Blinded Judge directive)

---

### Step 2: Customize Verifiers & Rubrics (Optional)
Depending on whether the goal is software development or technical writing, adjust `verify_static.py` or `rubric.json`:

* **Non-Coding Tasks**: Ensure section headings, word counts, link checkers, and table count assertions match the specific requirements.
* **Coding Tasks**: Add `pytest`, `py_compile`, or linter commands to `verify_static.py`.

---

### Step 3: Dispatch Worker Subagent
Launch the worker subagent passing the task spec file path as the prompt directive:

```markdown
Read `.gemini/harness/EGA-A8F2/tasks/task_01_spec.md` and implement the deliverable artifact at `.gemini/harness/EGA-A8F2/deliverable.md`.
```

---

### Step 4: Execute Dual-Verification Gate
Once the worker subagent signals completion:

1. Dispatch a fresh **Blinded Judge Subagent** passing `judge_prompt.md` and `rubric.json`.
2. Run the loop manager:
   ```bash
   python3 skills/expectation-harness/scripts/ega_loop_runner.py EGA-A8F2
   ```

If the gate passes, the task node transitions to `COMPLETED`. If it fails, open `.gemini/harness/EGA-A8F2/node_01_delta_report.md` and pass it back to the worker for the next alignment loop iteration.
