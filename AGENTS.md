# AGENTS.md — ocean-ai

## About the project

`ocean-ai` is part of met.no's FOCCUS project: it builds and analyses graph neural network (GNN)
ocean-forecasting models based on the [anemoi](https://github.com/ecmwf/anemoi-core) framework
(ECMWF's GNN weather/ocean forecasting stack), trained on NorKyst ocean data.

This repo covers the *data and analysis* side of the pipeline:
- creating and preprocessing training datasets from NorKyst (operational + hindcast) in `datasets/`
- managing atmospheric/river forcing data in `forcing/`
- building and inspecting the model graph in `graph/`
- analysing training/inference results (stats, plots, mlflow) in `plot/`
- retired approaches kept for reference in `legacy/`

**Relationship to `anemoi-core`**: the actual model architecture and training loop live in the separate
`anemoi-core` repository (sibling directory, not inside `ocean-ai`). `ocean-ai` calls into anemoi via the
`anemoi-training` / `anemoi-inference` CLI entry points (Hydra-configured) but does not modify anemoi-core
code. Do not create or edit files inside `anemoi-core` from this repo's sessions — treat it as an external
dependency/tool, referenced but out of scope here.

Because this repo does several related-but-distinct jobs (dataset creation, forcing management, graph
building, results analysis), expect the directory structure to be a bit heterogeneous rather than a single
linear pipeline — that reflects the actual project, not disorganisation to "fix".

## Session startup

When starting a new session on this project, follow these steps in order:

1. Read this file (`AGENTS.md`) fully
2. Read `STATUS.md` if it exists — it holds the current in-progress task, next step, and any HPC jobs
   that may still be running or queued (see "Resuming work" below); treat this as higher priority than
   the historical logs, since it's specifically about *unfinished* work
3. Read all `.md` files in the project root and relevant subfolders (e.g. `datasets/README.md`,
   `forcing/README.md`, `legacy/legacy_readme.md`) and `README.md`, `DOCUMENTATION.md`,
   `DISCUSSIONS_LOG.md`, `AI_REASONING.md`, `THOUGHTS.md` — skip those that do not exist yet
4. Read `copilot-conversation.log` (raw running chat transcript) if present, for recent context
5. Inspect the folder structure and list all files
6. Read existing code files to understand the current state
7. If `STATUS.md` mentions a submitted HPC job, or you're otherwise unsure whether a previous session
   left something running, check the local job scheduler (e.g. `squeue --me` on SLURM clusters like
   LUMI, `qstat -u $USER` on the met.no Grid Engine cluster) before assuming a clean slate — a session
   may have been interrupted while a job was still running or queued
8. Check whether the Python virtual environment for this task already exists (see "Environment
   management" below) and activate it; if not, and you need it, create it
9. Run existing tests (`pytest`) to confirm the baseline state before making any changes

## Environment management: venv/pip, and multiple HPC clusters

- The standard approach is a plain `venv` + `pip install -r requirements.txt`. Do not introduce
  mamba/conda — an earlier version of this file assumed conda/mamba, but that is not how this project
  actually manages environments.
- Different machines may already have a differently-named venv set up (e.g. job scripts on the met.no
  cluster activate `$DIR/python-envs/new-anemoi-env`) — check existing shell scripts for the actual
  activation path before creating a new environment; don't assume a fresh venv is needed just because
  you don't see one at the repo root.
- This project runs across several HPC clusters over time (met.no's own cluster, LUMI, etc.), each with
  its own job scheduler and module system. **Do not assume SLURM or SGE by default** — check the existing
  job scripts in this repo first:
  - `ppi_train.sh` / `ppi_infer.sh` use **Grid Engine (SGE)** syntax (`#$ -N`, `#$ -l h_data=...`,
    `#$ -q gpu-r8.q`) for the met.no PPI cluster, activating `new-anemoi-env` and running
    `anemoi-training` / `anemoi-inference` with Hydra config-dir/config-name.
  - `monitor_interactive.sh` uses **SLURM** (`squeue`, `srun`, `module load`) for monitoring jobs on LUMI.
  - When writing a new job script, copy the pattern from whichever existing script matches the target
    cluster, rather than guessing scheduler syntax.
- Sessions may start on a fresh machine (nothing installed) or a machine that already has environments
  set up from before — always check before (re)installing anything.
- Installing packages may require interactivity (e.g. confirming installs) — use non-interactive flags
  (`-y`, `--no-input`, etc.) so the process doesn't hang in an unattended/headless session.

## Data & storage

- Real input data, configs, and outputs live outside this repo on `/lustre/storeB/project/fou/hi/foccus`
  (met.no's Lustre storage) — this repo holds code, not data. Never commit data files: `.zarr`, `.nc`,
  `.npz`, checkpoints, logs and outputs are already gitignored — keep it that way, don't work around it.
- `forcing/get_forcings_daily.sh` runs as a cron job from a deployed copy on Lustre storage, **not** directly
  from this git checkout. If you edit any forcing script, remind the user that the deployed copy on Lustre
  must be updated manually — a git push/pull alone will not update the running cron job.
- Never hardcode a specific person's username or home directory path in new code; prefer environment
  variables or a config value that both defaults sensibly and is easy to override per machine/user.

## Config & experiment tracking

- Model/training configuration is Hydra-based (`--config-dir=... --config-name=...` passed to
  `anemoi-training` / `anemoi-inference`); this repo mostly consumes/produces those configs rather than
  defining the framework itself.
- Experiment tracking uses **mlflow** (see `plot/mlflow/`), but usage is currently basic/informal — don't
  build out a sophisticated mlflow integration unprompted; keep additions simple and ask before adding
  new tracked metrics/artifacts conventions.
- For non-Hydra, non-mlflow config (e.g. small script parameters, architecture choices you define
  yourself), prefer JSON config files for consistency and easy diffing/bookkeeping across experiments.

## Code practices

- Have tests to run with `pytest` if relevant — for self-implemented, non-trivial functions, but not
  required for small one-off scripts.
- Log with `loguru`; logs should contain all potentially useful information: inputs, parameters,
  intermediate results, timings, warnings, and final outputs — err on the side of logging more rather
  than less, so a session starting from scratch can understand what happened by reading the logs alone.
  Keep loguru output to single-line entries so logs stay parseable.
- For long-running loops (more than a few seconds), use `tqdm` for live progress, formatted to play
  nicely with loguru.
- Write simple, idiomatic Python; use type annotations for functions; use Google-style docstrings for
  functions and classes.
- Use formal checkers before considering work done: `codespell` (spelling), `ruff` + `pylint` + `flake8`
  (lint), `complexipy` (cognitive complexity; keep scores under 20, or document why a higher score is
  justified), `py_compile`, and `mypy` (static typing).
- Run tests after each significant code change and before returning to the user.
- Only import established packages already used in this project (numpy/xarray/zarr/anemoi-* ecosystem,
  loguru, tqdm, pytest, mlflow, standard library, etc.); ask the user before adding a new dependency, and
  only add it to `requirements.txt` once they agree.
- Code defensively: assert real assumptions about incoming data (not tautological checks) — never trust
  that NorKyst/forcing input files are well-formed; validate structure/content explicitly.
- If anything is unclear, ambiguous, or you see multiple reasonable approaches, ask the user rather than
  guessing — this project has a lot of institutional/domain context that isn't all written down.
- Think through and plan non-trivial work before implementing it.

## Code architecture and conventions

- Readability first; use the appropriate algorithm/data structure regardless, and only optimise further
  once a hot path is actually identified.
- Magic constants: `ALL_CAPS_CONSTANTS` defined near the top of the file, passed as default args.
- Prefer simple functions over classes/OOP unless there's a clear need for state/polymorphism.
- Scripts that form a numbered pipeline (dataset creation, preprocessing, etc.) should be named
  `00_description.py`, `01_description.py`, ... and each use an `if __name__ == "__main__":` guard so
  they remain importable in tests without side effects.
- For complex/important scripts, use explicit exit codes (`sys.exit(0)`/`sys.exit(1)`) so job scripts and
  headless runners can detect failures reliably.
- If a script uses randomness, set and log a seed as a configurable `ALL_CAPS` constant at the top, for
  reproducibility.
- Give each pipeline step its own subfolder for intermediate/task-specific outputs when it keeps the repo
  root cleaner; only cross-task, final artefacts belong at the root of a given subproject.
- Scripts should detect whether a graphical display is available and only pop up matplotlib figures
  interactively in that case — always save figures to `.png` regardless, since many runs are headless on
  HPC. Name figures `{script_number}p{cell_number}_{descriptive_name}.png`.
- Use `# %%` ipython cell markers (including as the first and last line of a file) for scripts with
  multiple logical steps, so they remain easy to run interactively.
- Timestamp runtime-generated files with a `YYYY_MM_DD_HH_MM_SS_` prefix (UTC).
- `README.md` should stay a quick, human-friendly summary of the project and its organization.

## Resuming work: STATUS.md

A Copilot session can be killed or interrupted mid-task (e.g. right after submitting an HPC job, or
mid-edit). `STATUS.md` exists purely to make resuming cheap and reliable — including from a *different*
machine, since laptop and HPC are separate git clones synced only via GitHub push/pull.

- Unlike `DISCUSSIONS_LOG.md` (append-only history), `STATUS.md` is **overwritten** each time — it only
  ever holds the *current* state, not a log.
- Keep it short: current task, next concrete step, and any HPC jobs you submitted that might still be
  running (cluster, job ID, log file path, what it's for). Example:
  ```markdown
  # STATUS

  **Current task:** Rewriting AGENTS.md for resumability.
  **Next step:** Add STATUS.md template and wire it into session startup checklist.
  **Running jobs:** none
  ```
  or, with a job in flight:
  ```markdown
  **Running jobs:**
  - LUMI, job 123456, log at /scratch/.../OUT_ocean-training.123456, training run for experiment X
  ```
- Update `STATUS.md` whenever you finish a turn that leaves something unfinished (a job still running, a
  half-done edit, a next step the user hasn't confirmed yet) — not just at the very end of a session.
- Since git commits/pushes are user-managed (see "Misc" below), remind the user to commit and push
  `STATUS.md` before ending a session if there's anything in flight that they might resume from another
  machine — otherwise the other clone won't see the update.
- When a task is fully done and nothing is outstanding, set `STATUS.md` to say so explicitly (e.g.
  "Nothing in progress.") rather than leaving stale information in it.

## Documentation to keep up to date

- `README.md` — quick human-friendly project summary
- `STATUS.md` — current in-progress task / next step / any running HPC jobs (see "Resuming work" above)
- `DOCUMENTATION.md` — fuller documentation of setup and usage, if it exists
- `DISCUSSIONS_LOG.md` — short, scannable log of user/agent discussions, one entry per interaction:
  ```
  ## YYYY-MM-DD — <one-line topic>
  **Prompt:** <one or two sentence summary of what the user asked>
  **Actions:** <bullet list of what was done>
  **Outcome:** <one sentence on result or decision reached>
  ```
- `copilot-conversation.log` — raw, append-only chat transcript kept at repo root (separate from and
  more verbose than `DISCUSSIONS_LOG.md`, which stays a curated summary); keep appending to it across a
  session rather than replacing it
- `THOUGHTS.md` — optional free-form notes/insights worth carrying into future sessions
- `AI_REASONING.md` — complex reasoning or design decisions worth remembering for later sessions
- Update the relevant files above whenever you finish a non-trivial piece of work

## Misc

- Never run "one-off complicated commands" directly in the shell — write a file, then run it.
- For long-running commands with substantial output, run via a `.sh` script with `tee` so output is both
  visible live and logged to a file.
- When monitoring a long-running job, poll periodically (e.g. sleep, then `tail` the log) rather than
  blocking continuously; if something looks wrong, fix and relaunch.
- Ensure logging to file happens live (e.g. unbuffered output), not only after a process exits.
- Follow safe development practices: no malicious/vulnerable code, no leaked secrets or personal data.
- Review your own code for refactoring opportunities at the end of a task, and implement clear
  improvements.
- Run all checks (tests, spelling, lint, typing, complexity) before considering a code change complete.
- Discuss ideas for better methods/algorithms/data structures with the user rather than silently
  implementing large changes.
- The user is a PhD-level domain expert — don't hesitate to brainstorm or push back on hard questions.
- Git and version control are managed by the user; do not make commits, create branches, or perform any
  git operations unless explicitly asked.
- Do not store raw prompts or data containing personal or confidential information in any file; redact
  or summarize. Flag anything that looks like a leaked secret or security risk immediately.
- Apply best practices for any other language used here too — e.g. run `shellcheck` on bash scripts.
- When reasoning about a calculation, don't do it "by hand" — write a small script under
  `AI_calculations/AI_CALCULATION_XX.py`, run it, and keep it archived there; these scripts follow the
  same coding guidelines as the rest of the project (linting, typing, etc.).
- Feel free to suggest meta-improvements to this AGENTS.md file itself if you spot a better convention or
  new tooling worth adopting.
- Do not spin up sub-agents on a more expensive model than the current one without asking the user first.

## Before responding to the user

After completing any code changes, run through this checklist:

1. [ ] Modified files pass `mypy`, `ruff`, `pylint`, `codespell`, `complexipy` (score < 20, or documented
       if above); `AI_calculations/` scripts included
2. [ ] All tests pass (`pytest`)
3. [ ] Figures are correctly named and saved; interactive display only when a graphical environment exists
4. [ ] `DOCUMENTATION.md` and `README.md` are up to date
5. [ ] `STATUS.md` reflects current reality — updated if a task is unfinished or a job is still running,
       or explicitly cleared if nothing is outstanding
6. [ ] `DISCUSSIONS_LOG.md` is updated with a summary of this interaction
7. [ ] `AI_REASONING.md` updated if any new complex reasoning was produced
8. [ ] Code reviewed for clear refactoring opportunities; implemented if straightforward
9. [ ] No secrets, credentials, or personal data present in any file
10. [ ] No security risk, malicious behavior, secret leak, or vulnerability introduced

## Rules of good AI development

### 1. Think before coding
Don't assume, don't hide confusion, surface tradeoffs. State assumptions explicitly; if uncertain, ask.
Present multiple interpretations rather than silently picking one. Push back if a simpler approach exists.

### 2. Simplicity first
Minimum code that solves the problem — nothing speculative. No unrequested features, abstractions, or
"flexibility". If you write 200 lines that could be 50, rewrite it.

### 3. Surgical changes
Touch only what you must; clean up only your own mess. Don't "improve" unrelated adjacent code or
refactor things that aren't broken. Match existing style. Remove imports/variables your own changes made
unused; don't remove pre-existing dead code unless asked.

### 4. Goal-driven execution
Turn tasks into verifiable goals ("fix the bug" → "write a failing test, then make it pass"). For
multi-step tasks, state a brief plan with a verification step for each part, then loop until it's
actually verified — not just "looks done".
