# Agency Agents integration for the public website

The website already runs .github/workflows/site-performance.yml and .github/workflows/scholar-pdf-audit.yml. These deterministic cloud workflows remain unchanged.

## New specialists
- AGENTS.md supplies project-level instructions to Codex and other supporting agents.
- .github/agents/site-performance.agent.md is a selectable Copilot website-performance engineer.
- .github/agents/research-publication-auditor.agent.md is a selectable read-only publication auditor.

After merge to main, check the repository's Copilot Agents picker in a supported GitHub interface. Choose the relevant profile for a task. Both have automatic model selection disabled until owner review. No new service, automatic inference schedule, external data connection or cloud server has been created.

## First proof of operation
1. Confirm the selected agent appears in the Copilot picker, subject to account access.
2. Assign a read-only performance audit of the latest site-performance run.
3. Compare its findings against GitHub Actions logs and existing baseline scripts.
4. Request a small PR fixing one confirmed problem, then run the existing checks.
5. Assign the publication auditor one completed PDF and inspect every flagged claim before distribution.

No user PC access. Publication, email, payments and production changes remain under owner control.

Role inspiration: MIT-licensed https://github.com/msitarzewski/agency-agents ; repository-specific prompts are original.
