# Expectation-Grounded Alignment (EGA) Harness Engine

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Framework: Antigravity](https://img.shields.io/badge/Framework-Google_Antigravity-orange.svg)](https://antigravity.google)

The **Expectation-Grounded Alignment (EGA)** Harness Engine (invoked via `/ega` or `/harness`) is a production-grade agentic controller skill for Google Antigravity and Gemini. It introduces **Expectation-Aligned Work (EAW)**—a paradigm that synthesizes machine-verifiable contracts (deterministic static verifier scripts + blinded dynamic LLM-as-a-Judge rubrics) **before** work begins, then enforces a dual-verification control loop until all expectation gates pass with zero defects.

---

## 🌟 Key Features

* 🎯 **Pre-Execution Contract Synthesis**: Generates task-specific verifiers (`verify_static.py`) and judge rubrics (`rubric.json`) prior to worker dispatch.
* 🛡️ **Dual-Verification Gate**: Enforces a strict two-stage quality gate combining fast local script execution with fresh-context, blinded LLM-as-a-Judge evaluations.
* ⚡ **Non-Coding & Coding Support**: Native verifiers for both software development (syntax, linters, tests) and non-coding domains (research dossiers, strategy documents, architecture specs).
* 🔄 **Pinpointed Delta Feedback Loops**: Automatically converts static check errors and judge defect lists into concise delta reports (`<node_id>_delta_report.md`) for iterative worker refinement.
* 🧩 **Fixed-Model Calibration**: Employs context slicing and disk scratchpad state persistence to maximize reliability across uniform model environments.

---

## 🚀 Quick Start

### 1. Compile Harness for a Goal
```bash
python3 skills/expectation-harness/scripts/compile_ega_harness.py "Design an enterprise security architecture for multi-cloud deployment"
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
        │   ├── static_verifiers.md    # Coding & non-coding deterministic verifiers
        │   ├── dynamic_judges.md      # Blinded LLM-as-a-Judge architecture
        │   └── model_calibration.md   # Context slicing & single-model optimization
        └── scripts/
            ├── compile_ega_harness.py # Harness & contract compiler
            └── ega_loop_runner.py     # Active control loop & Dual Gate manager
```

---

## ⚠️ Disclaimer

This is not an officially supported Google product.

## 📄 License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
