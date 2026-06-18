---
name: ship-change
description: Validate and commit a farmer-bot code change end to end — syntax-check, regenerate the bench twin, then commit (and optionally push). Use when the user says "ship-change", "ship it", "ship the change", "validate and commit", "syntax check and commit", "commit the change".
---

# Ship Change

The edit→syntax-check→regenerate-bench-twin→commit(→push) pipeline that recurs after every main.py/config.py edit.

## Steps
1. Syntax-check the changed Python: `cd /home/bosko/projects/farmer && python -c "import ast; ast.parse(open('main.py').read()); ast.parse(open('config.py').read()); print('OK')"`. Report any SyntaxError with line number and stop.
2. Regenerate the bench twin so the sim never drifts from main.py: `python3 gen_bench_main.py && python -m py_compile bench_main.py`. Always do this after a main.py change — bench_main.py is generated from main.py; never edit it by hand.
3. For behavior changes to plant_decision / farm logic, recommend running the `bench` skill to confirm no resource starves before committing. Skip for print-only or docs changes. Note: bones farming can't be exercised in-sim (change_hat errors), so bones changes are validated live, not by bench.
4. Stage the specific changed files by name (NOT `git add -A`) and commit with a conventional-commit message — `type(scope): summary` (feat/fix/docs/chore), body focused on the WHY — ending with the trailer `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` (use a HEREDOC to preserve formatting). Do not commit `probe.py` (untracked scratch).
5. Push only if the user asked: `git push origin main`, then report the commit hash and sync state.

## Gotchas
- Pyright "X is not defined" errors for game-injected names (Items, Entities, Unlocks, move, quick_print, etc.) are EXPECTED, not real errors.
- This skill chains the existing `syntax-check`, `bench`, `git-commit`, and `git-push` skills — reference them rather than duplicating their internals.
- bench_main.py and probe.py are untracked scratch — don't stage them.
