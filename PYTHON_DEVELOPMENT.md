# Python Development Guidance

Use this guide only for tasks that create, modify, or run Python code. Prefer the existing project structure and configuration; these are defaults, not requirements to add infrastructure to a small task.

## Environment and dependencies

- Use the project's existing environment when one is defined and relevant. If a dedicated environment is needed, use `anemoi_container_env` and the `conda-forge` channel.
- Do not install Mamba, create or modify an environment, or install packages without a clear need and the user's approval. If Mamba is unavailable and required, ask the user how to proceed.
- Prefer the standard library and already-approved dependencies. Discuss new external packages before adding them.
- Pin dependency versions in `environment.yml` when the project needs a reproducible dedicated environment. Document its setup command (`mamba env create -f environment.yml`) in project documentation when such an environment is introduced.
- Do not assume an environment exists: the project may have been copied to a fresh machine. Check for it before running code, and create it from `environment.yml` if it is missing and creation is approved.
- Assume a headless, non-interactive machine. Use non-interactive flags (for example `-y`) so installs do not stall, and check the output to confirm the channel is `conda-forge`.
- If Mamba is missing and the user approves installing it, use Miniforge from `conda-forge` only (not the paid Anaconda channels):
  ```bash
  wget -O Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
  bash Miniforge3.sh -b -p "${HOME}/conda"
  source "${HOME}/conda/etc/profile.d/mamba.sh"
  mamba shell init
  ```

## Implementation

- Write simple, idiomatic Python with type annotations where they improve clarity. Use Google-style docstrings for public or non-obvious functions and classes.
- Prefer functions over classes when object-oriented structure does not provide a clear benefit.
- Define magic constants as `ALL_CAPS` constants at the top of the file, and pass them as default arguments to functions; many default arguments are fine.
- Validate untrusted input explicitly and report invalid data with useful exceptions. Use `assert` only for internal invariants, not user or file input validation.
- Keep configuration in a separate file when it is genuinely useful; use JSON when structured configuration is needed, not by default.
- Make scripts safe to import by placing execution under an `if __name__ == "__main__":` guard. Give command-line scripts meaningful exit statuses when callers need to detect failure.
- When reproducibility matters, expose and record the random seed. Organize outputs in task-specific directories when that makes the workspace clearer.

## Logging and generated files

- Follow the logging library and conventions already used by the project. Log useful progress, parameters, warnings, and results without dumping raw inputs or sensitive data.
- Keep log entries readable and single-line where practical. Use a progress indicator for genuinely long-running loops when an approved dependency is available.
- Use UTC timestamps for generated artifacts when timestamps help distinguish runs. Avoid creating logs or intermediate files that are not useful to the user.

## Testing and checks

- Add or update focused tests for substantial or reusable behavior. Run the narrowest relevant test first, then broader checks when the change warrants them.
- Run the existing test suite when code changes could affect it; do not require a baseline test run for unrelated documentation tasks.
- Use the linters, type checkers, and formatters configured by the project. Do not install a collection of tools solely to satisfy this guide. `py_compile` can be used as a lightweight syntax check when appropriate.
- Keep complexity manageable. Investigate and simplify unusually complex code; document an intentional exception only when that context will help future maintainers.

## Figures and analysis scripts

- For requested figures, save PNG output and show it interactively only when a graphical display is available. In headless environments, save without attempting to open a window.
- Use descriptive figure names. Numbered script/cell names are appropriate when the task already follows a numbered analysis workflow, but are not required for every figure.
- Use IPython cell markers only when a script is intentionally organized for interactive cell-by-cell work.
- Use `tqdm` or another existing progress utility for long computations when helpful; do not add a dependency just for progress display.

## Running scripts and long jobs

- Do not run complicated one-off commands: write them to a file, then run the file.
- For long-running or verbose jobs, use a `.sh` script that calls the `.py` file and logs with `tee`, so output goes to both the console and a `.log` file that the user can inspect.
- Make sure logging to file is live, for example with `--no-capture-output` for `conda run` or the equivalent for other launchers.
- Monitor long jobs periodically by checking the tail of the log. If there is an error, fix it, relaunch, and monitor again.
- Run scripts one at a time and wait for completion; be aware of RAM use so the host machine does not freeze.
- For other languages in the project, apply their best practices. For Bash scripts, use safe shell practices (fail on first error, quoted variables), run `shellcheck` when available, and use the preamble from [example_preamble.sh](https://raw.githubusercontent.com/jerabaul29/config_scripts_snippets/refs/heads/main/snippets/bash/preamble/example_preamble.sh).

## After a code change

- Check that the guidelines in this file were followed, and that the README and `DOCUMENTATION.md` are up to date.
- Do a short review for clear refactoring or improvement opportunities, and implement the clear ones.
- Make sure everything works: tests, spell check, linting, type checking, and complexity checks where configured.
- Check that no secrets, credentials, or personal data were written to any file, and that the code has no security risk.
- Add a short entry to `DISCUSSIONS_LOG.md`, and update `AI_REASONING.md` if new complex reasoning was produced.
- Check that generated figures are saved correctly, and shown interactively only when a graphical display is available.

## Principles for code changes

### Think before coding

- State assumptions explicitly; if uncertain, ask.
- If several interpretations or implementations exist, present them instead of picking silently.
- If a simpler approach exists, say so and push back when warranted.
- If something is unclear, stop, name what is confusing, and ask.
- Plan before implementing so the structure is clear, not accumulated ad hoc.

### Simplicity first

- Write the minimum code that solves the problem; no features, abstractions, flexibility, or configurability that were not requested.
- Do not add error handling for impossible scenarios.
- If a solution is much longer than it needs to be, simplify it.

### Surgical changes

- Touch only what the request requires; match the existing style.
- Do not improve or refactor adjacent code that is not broken. Mention unrelated dead code instead of deleting it.
- Remove imports, variables, and functions that your own changes made unused.
- Every changed line should trace directly to the request.

### Goal-driven execution

- Define a verifiable success criterion first, for example a test that reproduces a bug and then passes.
- For multi-step tasks, state a brief plan with a check for each step.
- For refactoring, ensure tests pass before and after.
