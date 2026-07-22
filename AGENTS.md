# AGENTS.md

## Purpose
This file defines the working rules for the terminal agent in this project.

## Operating rules
- Read `CONTEXT.md` before starting work.
- Read `tasks/TASK.md` before implementing anything.
- Write progress and outcome into `tasks/REPORT.md`.
- Keep `PROJECT_LOG.md` append-only.
- Do not make unrelated changes.
- Prefer the smallest correct change.
- Use UTF-8 for files.
- Use ASCII in terminal output unless the environment is known to handle UTF-8 reliably.
- **Python imports in `app/`:** always use package-qualified imports (`from app.module import X`), not bare relative imports (`from module import X`). The entry point is `python -m app`, which runs from the project root.
- **Always run `python -m app` after changes** to verify the code works end-to-end. Do not report "completed" without a successful test run.

## Workflow
1. Read context.
2. Execute the task.
3. Validate the result.
4. Update the report.
5. Leave the repo in a clean, explainable state.
