# General python coding practices — TODO: Ocean AI (anemoi)

## About the project

TODO: describe the main aspects of the project

## Goal of this folder and code organization

TODO: explain how you want the project folder to be structured, what scripts and figures should be produced, etc
TODO: ideally, "### task 00: some description", then some paragraph that discusses what to do

## Session startup

When starting a new session on this project, follow these steps in order:

1. Read this file (`AGENTS.md`) fully
2. Read all `.md` files in the project root: `README.md`, `DOCUMENTATION.md`, `DISCUSSIONS_LOG.md`, `AI_REASONING.md`, `THOUGHTS.md` — skip those that do not exist yet
3. Inspect the folder structure and list all files
4. Read existing code files to understand the current state
5. Check the mamba environment (name: — see mamba section below) exists and activate it; if not and you need it, install it
6. Run existing tests (`pytest`) to confirm the baseline state before making any changes

## Code practices

- have tests to run with pytest if relevant - for self implemented serious functions but not for small scripts
- have logging with loguru; logs should contain all possibly interesting information: inputs, parameters, intermediate results, timings, warnings, and final outputs — err on the side of logging more rather than less, so that a session starting from scratch can fully understand what happened by reading the logs alone
- make sure logs look good and are not messed up with loguru, in particular, only have loguru log single line entries
- for long running commands that involve long loops (that last more than a few seconds), use `tqdm` to show progress live; remember to make this look nice with loguru
- write simple, idiomatic python code
- use typing / type annotation for the functions
- use Google-style docstrings for all functions and classes
- use formal checkers for the code (install these in the mamba environment):
  - check spelling in the code with `codespell`
  - check and lint the code with `ruff` + `pylint` + `flake8`
  - check code complexity with `complexipy`: a cognitive complexity score below 20 is acceptable; above 20, consider whether the complexity is inherent to the problem or can be reduced — document the reasoning if you decide to keep it
  - use `py_compile` to check that things are correctly written
  - use `mypy` for static type checking
  - generally, double check your code for good style, ease of understanding, good API / interface, safety and speed
- run tests after each significant code change and before returning to the user if code changes have been done
- use established packages:
  - all python standard library packages are fine to use
  - TODO: list the packages that can be used
  - no further package imports without discussing with the user first; if you think more packages are needed, ask / discuss with the user, then add these here and to the environment only if the user says yes
- code defensively: use asserts to document and check all assumptions about incoming data
- you cannot trust input data - always assume they may have errors, be corrupted, etc, and do as many checks as possible
- make sure that the asserts are really useful and not tautological - asserts should really check that the data match what is expected, i.e. check that the input from the "messy real world" match the assumptions about the structure of the file and content
- if you are in doubt, or anything is unclear or ambiguous or badly explained or defined, do not guess - ask me (the user) for more information
- if you can see several ways to implement the same thing, and you are unsure which one to choose, feel free to ask me (the user) for more information / chat together
- before doing any implementation work, think carefully and plan it - make sure you understand the whole problem and have no doubt on anything before implementing, so that the implementation is well architectured and not a spaghetti mess

## Code setup and environment management: mamba

- use mamba; it should be pre installed on the system; do not install it yourself, do not add channels, only conda-forge should be used; fail if no mamba and ask user help; there should be a "dev" default environment with default packages in it
- use an environment.yml to define the necessary packages for the mamba environment if not using the default "dev" environment; always pin package versions (e.g. `numpy=1.26.4`) for reproducibility
- use, or create if necessary, a dedicated environment for working on this, with name: "TODO: choose a good name"; use only this env for running code here
- use only conda-forge channel (this should already be set by the mamba install available); we do not want to use any paid-ToS package from anaconda inc!
- remember that installing the mamba environment may require a bit of interactivity - check the output, type -y if needed, check that the channel is well conda-forge. if not interactive / using -y , the mamba environment installation may stall.
- the DOCUMENTATION.md must say to create the mamba environment with `mamba env create -f environment.yml` if it does not already exist for human users workflows; when you AI create it, remember to use -y as said above
- remember that you may be asked to work on a project that either i) may just have been copied to a fresh new virtual machine (VM) without the environments installed, or ii) may be on a machine that has already been used to work on the project and on which the environments etc are installed. So when starting a new session, check if the environments etc needed are present yet or not, even if it is clear that the code has been run before (it may have been on another machine, and you may be on a fresh new machine); if necessary, installed environments etc as described here and in relevant project files.
- for all tasks, scripts, etc, remember that you may be running from an isolated headless VM, and things may or may not be interactive - use relevant flags as needed so things do not hang.

## Code architecture and conventions

- readability and code quality are the top priority; always use the right algorithm and data structure for the task regardless — and optimise further only if a section is identified as a hot path
- magic constants should be ALL_CAPS_CONSTANTS defined at the start to make it easy to edit
- avoid object oriented if not necessary, make the code based on simple functions
- pass the ALL_CAPS_CONSTANTS as default args, it is ok to have many default args to the functions
- make sure to use JSON config files to summarize config choices, architecture choices for neural networks if there are some, etc; make the code robust and general so that it easily supports running for example several experiments and models, doing bookkeeping to be able to analyze the results a posteriori; prefer JSON over other formats (YAML, TOML, CSV) for consistency
- make sure to log important results, tasks, script progress, etc, in logs. Have logs clearly named, typically for example "01_some_script_2026_05_13T15_25_15.log", which indicates the script that is being logged, when the script has been run.
- the work is split into independent, consecutive, self contained tasks that each correspond to a python file: run first `00_PLACEHOLDER_FOR_TASK.py`, then `01_PLACEHOLDER_FOR_ANOTHER_TASK.py`, etc...
- all scripts must use a `if __name__ == "__main__":` guard so they can be imported in tests without side effects
- for scripts that are complex or important, use explicit exit codes: `sys.exit(0)` on success, `sys.exit(1)` on failure, so that callers and headless runners can detect errors reliably
- if a script uses any randomness (`random`, `numpy.random`, etc.), set and log a seed at the very top of the script; make the seed a configurable constant (ALL_CAPS) so runs are reproducible
- for each task, consider whether a dedicated subfolder is warranted to keep the root clean: intermediate data, processed outputs, and task-specific files that are not final results should live in a subfolder named after the task (e.g. `00_task_name/`, `01_another_task/`); only final, cross-task artefacts belong in the root
- the scripts should be able to run both on a computer with graphical display possibility (then the figures should pop up for the user to interact with them), and on a computer that runs headless (the this should be detected and the figures should only be saved to disk but not pop up as they cannot); make sure to have any script automatically detect what case it is in.
- the README.md should be a quick user-friendly summary of the project and its organization
- when there are several steps in a file, separate these into logical sections with ipython cell markers (`# %%`). Make sure there is such a marker on the first line and last line of each file, so that these are ipython-friendly for users who run it this way.
- save matplotlib figures as `.png`; also show them interactively if a graphical environment is available. Scripts may run headless on servers, so check this at script startup and disable interactive plotting if needed. Name figures as `{script_number}p{cell_number}_{descriptive_name}.png` — e.g. `00p01_plot_all_trajectories.png` (1st figure of script 00), `02p03_confusion_matrix.png` (3rd figure of script 02).
- when keeping track of stuff, for example some runtime-generated logs or files, binary data about for example models etc: use as a prefix YYYY_MM_DD_HH_MM_SS_ where YMDHMS are from the UTC date and time.

## Misc

- make sure to follow all these instruction, keep track and up to date all necessary .md files, etc; create missing .md files if necessary; each time you are finished with a large task, take a good check and update all files including .md files as necessary
- generally use your knowledge of python and programming to apply best practices on all aspects of the coding
- never run "one off complicated commands": write to file, then run the file
- for long running commands that generate quite a bit of output, run from a .sh file with tee to allow console logging + logging to a file so the human can also examine with `cat` or similar
- if needed, write .sh files to call the .py files - for example to enable logging the output to a .log file if a script takes long to run and is run in the background
- when running something for a long time and logging it, monitor it periodically; for this: sleep 15 minutes, when waking up use `tail` to check for example the last 5 lines of the file; if everything looks good, just sleep and iterate but if there was an error, fix it and re-launch and re-monitor this way.
- if logging to a file, make sure that logging happens live by using for example `--no-capture-output` with `conda run`, or similar with other commands
- follow safe development practices; dont leak any sensitive data, make sure there are no malicious or vulnerable code, make sure the code is safe to run and does what it advertises and what the user expects
- at the end of each update to the code, go through the files and check that the documentation and readme are up to date; make sure all important aspects are documented in the DOCUMENTATION.md file
- when writing code, check that all guidelines present here are followed
- at the end of each code update, do a small review of the code, look for good possibilities for refactoring and improvement, and if there are clear improvement possibilities, work on implementing them
- at the end of each code update, make sure everything works - tests, spell check, linting, type checking, complexity, etc
- if you find a better way to do things, or you have an idea of possible improvement or something better to do (better method, better algorithm, better data structure to use; something more to test and try with the data to see if it can give a better result), discuss this with the user
- the user is typically a PhD level expert on the topic - dont hesitate to discuss, brainstorm, exchange etc with the user on hard questions
- keep a `DISCUSSIONS_LOG.md` log of the discussions with the user; use this minimal format, one entry per interaction, and keep each entry short — the goal is a scannable record, not a full transcript (do not bloat it or it will fill the context):
  ```
  ## YYYY-MM-DD — <one-line topic>
  **Prompt:** <one or two sentence summary of what the user asked>
  **Actions:** <bullet list of what was done>
  **Outcome:** <one sentence on result or decision reached>
  ```
- if relevant, you can keep a THOUGHTS.md of your own thoughts and things that you want to document to re use for later sessions starting from scratch - important insights etc that do not fit somewhere else
- make sure that your output is both human and ai friendly; in particular, have well formatted logs and outputs that can be read both by human and ai. produce figures to present the output to the human, and also, if relevant (for examle, the figures show or contain some key metrics that are meaninful, or are "just" a few histogram bars), print out in log the summary of the data shown in the figure so the ai can read it without needing to see the figure (this only works if there are small outputs; dont do this with a massive 2d plot, or large trajectory plots etc that contain too much data to be printed in logs).
- when running scripts, run one at a time, wait for it to complete, then run another: be aware of RAM use to not freeze and crash the host machine
- git and version control are managed by the user; do not make commits, create branches, or perform any git operations unless explicitly asked
- do not store raw prompts/data containing personal or confidential information; redact or summarize minimally, both in the README, DOCUMENTATION, AGENT, or any other file: do not leak credentials or passwords or secrets
- if you notice anything that may look like a leaked secret or a security risk, let the user know immediately
- if writing more languages in the project as a whole, also apply best practices relevant to this language; for example:
  - if writing and running bash scripts, use `shellcheck` (`mamba` installable from conda-forge) and run it on the script, and use best practices (headers to fail on first error etc)
- every time you have considered an answer or solution, consider alternatives and / or the opposite. Does the answer still make sense or should it be reconsidered? can more viewpoints be taken or alternative solutions be suggested with the human?
- whenever you are thinking about something, do not guess - calculate. For example, do not do "back of the envelope" calculation by yourself: write a small script `AI_calculations/AI_CALCULATION_XX.py` (where XX is a short description of what you are computing), run it to get the proper result, and archive it in `AI_calculations/`. This way, 1) your thinking remains documented, 2) you are formally sure, if the code is correct, that you are not making a "silly" mistake in for example a back of the envelope calculation; do not guess or do calculations by yourself that can be wrong, write code that does it formally correct! All scripts in `AI_calculations/` must follow the same coding guidelines as the rest of the project (linting, spelling, type checking, etc.)
- if you reason about some complex things that you want to keep track of, create a "AI_REASONING.md" if it does not exist already, or otherwise extend it, and document there complex reasoning and ideas you want to keep track of in the future also if a new session is started
- when starting a new session, make sure to read the whole project and to get full understanding about it - this file, all relevant .md files, AI_REASONING.md if it exists, code if it exists, etc. Follow the "Session startup" checklist above.
- also feel free to suggest meta improvements to this AGENTS.md file - for example if more automatic checks or tooling have become available, feel free to suggest adding these here, or if you see possible better recommendations based on actual problems you have to solve, you can suggest feedback to this file. meta-improvement is good!
- if using sub-agents or similar, do not use another and especially not a more expensive model than the current one without asking the user. For example, if the present model is a sonnet model, creating a sonnet sub-agent of similar is ok. But it is not ok to create an opus or fable sub-agent. By default, use the same model for new sub-agents or similar that you are, and if you want to use a different one, ask the user first if this is ok.

## Before responding to the user

After completing any code changes, run through this checklist before returning to the user:

1. [ ] All modified files pass `mypy`, `ruff`, `pylint`, `codespell`, `complexipy` (score < 20, or documented if above); `AI_calculations/` scripts included
2. [ ] All tests pass (`pytest`)
3. [ ] Figures are correctly named and saved; interactive display enabled when a graphical environment is available
4. [ ] `DOCUMENTATION.md` and `README.md` are up to date
5. [ ] `DISCUSSIONS_LOG.md` is updated with a summary of this interaction
6. [ ] `AI_REASONING.md` updated if any new complex reasoning was produced
7. [ ] Code has been reviewed for refactoring opportunities; improvements implemented if clear
8. [ ] No secrets, credentials, or personal data are present in any file
9. [ ] No security risk, malicious behavior, secret data leak, vulnerability

## Follow the rules of good AI development

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
