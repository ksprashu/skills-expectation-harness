# Global Agent Rulebook (AGENTS.md)

This file defines the global guidelines, style rules, and structural constraints that all AI agents MUST follow when operating in this workspace.

---

## 1. Document Design & Typography

* **Exact Spelling & Casing**: Ensure official branding is spelled with complete precision. Specifically, **Encyclopaedia** (with 'ae' spelling and capitalized). Avoid generic tags like "manual" or "wiki" in title paths.
* **Navigation Architecture**: Group navigation menus semantically (e.g., separating theoretical "Chapters" from practical "Project Artifacts"). Align desktop lists and mobile `<select>` elements with `<optgroup>` groupings.

---

## 2. Responsive Table Formatting (Column Wraps)

* **Preventing Awkward Word-Wraps**: Comparative tables containing short package names, codes, or keys in their first column must remain on a single line.
* **Inner Tag Resets**: Standard HTML `<code>` blocks often carry `white-space: pre-wrap !important` and `word-break: break-word !important`. To prevent first-column wrap issues, always apply:
  ```css
  th:first-child, td:first-child {
      white-space: nowrap;
  }
  td:first-child code {
      white-space: nowrap !important;
      word-break: normal !important;
  }
  ```

---

## 3. Modular Compilation & HTML Tag Symmetry

* **Balancing Container Closures**: In compiled single-page applications, unbalanced closing tags (specifically `</div>`) inside modular sub-files are catastrophic. They will close the main `<main>` container block prematurely, causing the browser to render subsequent page content completely blank.
* **Clean Build Synchronization**: Ensure compilation scripts are automatically executed after editing any modular chapter files to keep the final production-ready page perfectly synchronized.

---

## 4. Documentation Themes & Compiler Specifications

* All raw Markdown documentation sheets (e.g., in `docs/`) must include standard YAML frontmatter selecting one of the four premium **Stitch** presentation themes:
  - `technical` (Light theme for developer engineering guides)
  - `obsidian` (Dark theme for executive showcase walkthroughs)
  - `proscript` (Light theme for formal operations sheets)
  - `dynamics` (Dark theme for dense telemetry logs)
