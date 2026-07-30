# Expectation-Grounded Alignment (EGA) Harness Engine

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Framework: Google Antigravity](https://img.shields.io/badge/Framework-Google_Antigravity-orange.svg)](https://antigravity.google)

The **Expectation-Grounded Alignment (EGA)** Harness Engine (invoked via `/ega` or `/harness`) is a production-grade agentic controller skill for Google Antigravity and Gemini. It introduces **Expectation-Aligned Work (EAW)**—a paradigm that synthesizes machine-verifiable contracts (deterministic static verifier scripts + blinded dynamic LLM-as-a-Judge rubrics) **before** work begins, then enforces a dual-verification control loop until all expectation gates pass with zero defects.

---

## 🌟 Key Features

* 🎯 **Pre-Execution Contract Synthesis**: Generates domain-aware verifiers (`verify_static.py`), blinded judge prompts (`task_01_judge_prompt.md`), and rubrics (`rubric.json`) prior to worker dispatch.
* 🎭 **6-Persona Role Assignments**: Assigns specialized cognitive persona roles (`Scout-Researcher`, `Analyst-Inquirer`, `Architect-Blueprint`, `Builder-Coder`, `Sentry-Gatekeeper`, `Mentor-Educator`) to task graph nodes without document overhead.
* 🌿 **Topological Task Graph Execution**: Resolves node dependency trees (`depends_on: ["node_01"]`) so dependent tasks only execute after parent nodes pass both verification gates.
* 🧠 **Selective Knowledge Grounding**: Hydrates worker subagent context on demand using Google's Open Knowledge Format (OKF) index (`.gemini/knowledge/index.md`) and deterministic OKF verifiers (`verify_okf.py`).
* 🛡️ **Dual-Verification Gate**: Enforces a strict two-stage quality gate combining fast local script execution with fresh-context, blinded LLM-as-a-Judge evaluations.
* ⚡ **Domain-Aware Verification**: Specialized native verifiers for Python AST compilation, Node syntax checks, Markdown links/word bounds, and OKF concept compliance.
* 🔒 **Domain-Aware Full Closure Protocol**: Automatically executes git status inspection, conventional commit formatting (`feat(<short_id>): ...`), and remote push upon verification signoff.
* 🌌 **Recursive Self-Improvement (RSI) & Dream Sequence**: Post-execution reflection loop that harvests defects, updates central learning registries (`rsi_learnings_registry.json`), and fortifies future verifiers.
* 🔄 **Pinpointed Delta Feedback Loops**: Automatically converts static check errors and judge defect lists into concise delta reports (`<node_id>_delta_report.md`) for iterative worker refinement.
* 🧩 **Fixed-Model Calibration**: Employs context slicing and disk scratchpad state persistence to maximize reliability across uniform model environments.

---

## 🚀 Quick Start

### 1. Compile Harness for a Goal & Persona
```bash
python3 skills/expectation-harness/scripts/compile_ega_harness.py "Design an enterprise security architecture for multi-cloud deployment" "Architect-Blueprint"
```

### 2. Dispatch Worker Subagent
Pass `.gemini/harness/<SHORT_ID>/tasks/task_01_spec.md` as the directive to the worker subagent.

### 3. Run Dual-Verification Gate
```bash
python3 skills/expectation-harness/scripts/ega_loop_runner.py <SHORT_ID>
```

---

## 📂 Repository Layout

```
skills-expectation-harness/
├── README.md                          # Repository overview
├── USER_GUIDE.md                      # Detailed usage instructions
├── LICENSE                            # Apache 2.0 License
├── CONTRIBUTING.md                    # Contribution guidelines
├── CODE_OF_CONDUCT.md                 # Code of conduct
├── .agents/
│   └── AGENTS.md                      # Workspace rulebook
└── skills/
    ├── ega/                           # Skill alias for /ega
    │   └── SKILL.md
    ├── harness/                       # Skill alias for /harness
    │   └── SKILL.md
    └── expectation-harness/
        ├── SKILL.md                   # Primary custom skill entrypoint
        ├── references/
        │   ├── ega_paradigm.md        # EAW & EGA conceptual foundations
        │   ├── persona_roles.md       # 6-Persona Role Assignments & Primers
        │   ├── knowledge_grounding.md # Selective Context Grounding via OKF
        │   ├── static_verifiers.md    # Coding & non-coding deterministic verifiers
        │   ├── dynamic_judges.md      # Blinded LLM-as-a-Judge architecture
        │   ├── model_calibration.md   # Context slicing & single-model optimization
        │   └── rsi_and_closure_protocol.md # Domain Closure & RSI Dream Sequence Protocol
        └── scripts/
            ├── compile_ega_harness.py # Harness & contract compiler
            ├── ega_loop_runner.py     # Active control loop & Dual Gate manager
            ├── ega_closure_engine.py  # Domain-Aware Full Closure Engine
            ├── rsi_dream_engine.py    # Recursive Self-Improvement Reflection Engine
            └── verify_okf.py          # Deterministic OKF Concept Verifier
```

---

## ⚠️ Disclaimer

This is not an officially supported Google product.

## 📄 License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
