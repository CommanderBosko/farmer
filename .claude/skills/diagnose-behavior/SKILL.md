---
name: diagnose-behavior
description: Explain why the farmer bot is doing what it's doing by reading its live goal and tracing the decision logic. Use when the user says "diagnose-behavior", "why is it doing X", "why is it farming X", "diagnose the bot", "what is the bot doing", "why is it stuck".
---

# Diagnose Bot Behavior

Trace the farmer bot's live goal and decision logic to give a definitive answer for "why is it farming X / why is it stuck on X" instead of a guess.

## Steps
1. Read the live goal from output.txt — the line `Current Goal: <crop> for Unlock: <unlock>` (grep for "Current Goal"). The file lives at `$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt`. If a fresh read is needed while the bot runs, arm the `output-watcher` skill.
2. Trace `plant_decision()` in main.py in priority order to find which branch produced that goal:
   a. `FOCUS_CROP` override (config.py) — bypasses everything if set.
   b. Energy floor — `power < MIN_POWER_STOCK` returns Power.
   c. Unlock steering — `get_next_unlock()` finds the next unlock's bottleneck resource and farms only that (Bone → snake, Gold → maze/pumpkin-for-substance, crops → check_stock).
   d. Lowest-stock balance — only when all unlocks are maxed.
3. Cross-check config (FOCUS_CROP and the MIN_* thresholds) and live state (resource amounts; unlock costs via the `game-probe` or `unlock-status` skill) to confirm the cause.
4. State the root cause plainly and, if the behavior is unintended, recommend the fix.

## Gotchas
- FIRST check whether the running bot is on stale code — a script that wasn't restarted after an edit keeps running the OLD logic. This was the actual cause of multiple "bugs" in this project (e.g. a stale FOCUS_CROP and the old maze/goal labels). The file symlink syncs, but a running script does not reload until restarted.
- output.txt is overwritten each run; it only holds the latest run.
- Leans on `output-watcher`, `game-probe`, and `unlock-status` — reference them rather than duplicating their logic here.
