---
name: syntax-check
description: Check main.py for syntax errors and common farming bot bugs. Use before committing, when debugging unexpected bot behavior, or after making code changes.
---

# Syntax Check Skill

Validate `/home/bosko/projects/farmer/main.py` for syntax errors and project-specific pitfalls.

## Steps

1. **Python syntax check** — run:
   ```bash
   cd /home/bosko/projects/farmer && python -c "import ast; ast.parse(open('main.py').read()); print('Syntax OK')"
   ```
   Report any SyntaxError with the line number.

2. **Project-specific checks** — grep for known pitfall patterns:

   a. `plant(Entities.Tree)` without a preceding `till()` guard:
   ```bash
   grep -n "plant(Entities.Tree)" main.py
   ```
   For each match, check the surrounding lines (within the same elif/if block) for `till()`. Flag any `plant(Entities.Tree)` that isn't guarded.

   b. Unguarded `move()` at end of loops — look for `move(North)` or `move(East)` inside for-loops that aren't wrapped in an `if` guard:
   ```bash
   grep -n "move(North)\|move(East)\|move(South)\|move(West)" main.py
   ```
   Flag any bare `move()` that appears to be the last statement in a loop body without an `if y < ...` or `if x < ...` guard.

   c. Missing `global` declarations — check that `update_amounts()` declares all globals it assigns to:
   ```bash
   grep -A 20 "def update_amounts" main.py
   ```

3. **Report results** — one section per check:
   - ✓ if clean
   - ✗ with line number and description if an issue is found
   - Note: Pyright errors about `Items`, `Entities`, `Grounds`, `Unlocks`, `Hats` being undefined are **expected** — these are game-injected APIs and are not false positives.

## Rules

- Do not modify any files
- Only report issues that are actual bugs or known pitfalls, not style preferences
- Keep the report concise — one line per finding
