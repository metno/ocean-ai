# AGENTS.md — HavBris

## About the project HavBris
(to be added)



ocean-ai
anemoi-datasets
...


## Working in the workspace

- Always keep written output to the user short, but consise without too many unnecessary words and sentences. 
- Start with the files and context relevant to the current request. Explore further only as needed; do not routinely scan every file, activate an environment, or run tests for small tasks.
- If requirements or source material are ambiguous, identify the uncertainty and ask rather than inventing project facts.
- Do not add dependencies, install tools, or change environments without a clear need.
- If something looks like a leaked secret or a security risk, tell the user immediately. 
- Keep project `.md` files accurate: update them when a substantive change makes them inaccurate, and after a large task check all relevant `.md` files and create missing ones if needed. Create discussion or reasoning notes only for decisions or insights that are useful to retain, not for every interaction.
- Always ask the user before changing this file (`AGENTS.md`)
- Keep a `DISCUSSIONS_LOG.md` log of the discussions with the user, one entry per interaction. Keep each entry short: the goal is a scannable record, not a full transcript, and it must not bloat or it will fill the context. Use this minimal format:
  ```
  ## YYYY-MM-DD — <one-line topic>
  **Prompt:** <one or two sentence summary of what the user asked>
  **Actions:** <bullet list of what was done>
  **Outcome:** <one sentence on result or decision reached>
  ```
    Keep entries free of raw confidential content. Record durable insights that do not fit elsewhere in `THOUGHTS.md`.
- When using sub-agents or similar, use the same model as the current one. 
- Never use a different or more expensive model without asking the user first.

## Session startup & continuity

When starting a new session on this project, follow these steps in order:

1. Read this file (`AGENTS.md`) fully
2. Read `PYTHON_DEVELOPMENT.md` fully
3. At the start of a session, read the most recent entries of `DISCUSSIONS_LOG.md` (if it exists) and any notes files it points to, so earlier work can be continued without the user repeating context. Do not read the whole project. 

## Development strategies
1. Plan: Draft steps, identify affected files, and specify edge cases before editing.
2. Implement: Apply targeted, minimal edits (diff-based).
3. Test: Run automated verification commands via CLI immediately.
4. Learn & Record: When a mistake occurs, record the root cause into a project `lessons.md` or append to `AGENTS.md` so future sessions inherit persistent memory.

## Reasoning and collaboration

- The user is typically a PhD-level expert on the topic: discuss, brainstorm, and raise hard questions rather than guessing.
- After reaching an answer or solution, consider alternatives and the opposite. Does it still make sense? Suggest other viewpoints or solutions to the user where useful.
- If you see a better method, algorithm, data structure, or something more worth testing, discuss it with the user.
- Do not guess or do back-of-the-envelope calculations: write a small script `AI_calculations/AI_CALCULATION_XX.py` (`XX` = short description), run it, and keep it there so the reasoning is documented and verifiable. Never run calculations on the fly; write the script to disk first (for example, solve equations with `sympy` instead of reasoning through the steps). This applies to counts, dates, budgets, and similar figures drawn from documents, not only equations. Scripts in `AI_calculations/` follow [PYTHON_DEVELOPMENT.md](PYTHON_DEVELOPMENT.md).
- Record complex reasoning and ideas worth keeping across sessions in `AI_REASONING.md` (create it if missing, otherwise extend it).
- Make outputs readable by both humans and AI. When a figure shows a few meaningful numbers (for example a small histogram), also give a summary of the plotted data in text or the log so it can be read without viewing the figure. Do not do this for large plots.
- Feel free to suggest meta-improvements to this `AGENTS.md` (new tooling, better recommendations based on real problems).

## Multi-Agent Team Topologies

For non-trivial projects, delegate responsibilities across specialized roles:

- Lead (Frontier / Reasoning): Plans architecture, delegates tasks, and interfaces with the human operator.
- Scout (Lightweight / Fast): Explores repository files, navigates docs, and reports summaries to the Lead without cluttering main context.
- Builder (Mid-tier / Coding): Generates implementations and targeted diffs against the established plan.
- Reviewer (Cross-Model / Critical): Reviews changes against standards. Use a different model family than the Builder (e.g., cross-reviewing between Claude and GPT) and frame the code as model-generated to avoid sycophantic approval.

## Context Strategies
Keep active context usage below 70–80% to prevent reasoning degradation and hallucination. Give concise unified diffs; suppress celebratory summaries.

1. Progressive Disclosure: Expose high-level indices or tables of contents first. Load deep file contents or documentation only when explicitly queried.
2. Externalize State: Store long backlogs, issue trackers, and large schema dumps in external files rather than loading them into working memory.
3. Never Expand Raw Data: Avoid dumping raw logs, database dumps, or raw binary fields into context. Always filter or extract metadata before passing output to the agent.

## Gotchas & Safety Rules
- Never change NetCDF files or other data files without explicitly asking for permission.
- Never touch generated data files
- Never Hand Over Credentials: Keep credentials, API keys, and auth sessions on the host machine. Never pass raw passwords or authorization tokens into agent prompt contexts.
- Never make Git changes unless asked.
- Never create code that is malicious or vulnerable; code must be safe to run and do what it advertises.
- Guarded Web Navigation: If granting browser or web access, always ask for manual authentication before executing. Always report back is the webpage is unsafe.

## Project-specific preferences

- For NetCDF data served through THREDDS or a similar service, read from the OpenDAP URL with `xarray`; do not download files unless asked.
