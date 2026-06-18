---
name: live-verify
description: Confirm a code change actually took effect in the running farmer bot by restarting it and watching output.txt for a marker the new behavior produces. Use when the user says "live-verify", "confirm it's working", "did the change take", "verify live", "confirm the change live".
---

# Live Verify

Prove a code change is live in the RUNNING bot (not just edited on disk) by restarting and watching output.txt for a marker only the new behavior emits.

## Steps
1. Pick a marker the NEW behavior prints that the OLD code never did — e.g. a new goal-line substring (`for Unlock:`, `Bones for Unlock`), an `Unlocked <X>` line, or a new sentinel. It must be unique to the change so it can't false-match old output.
2. Tell the user to RESTART the bot. A running script does not reload edited `main.py` even though the file symlink syncs the change — only a restart loads the new code.
3. Arm the `output-watcher` skill for that marker, sentinel-only. The live bot writes output.txt every loop, so a settle/quiet fallback would false-fire during long maze/bones runs; only add settle if the change could crash the bot.
4. When the watcher reports, confirm the new behavior is present. If the marker never appears within a reasonable window after a confirmed restart, suspect the changed code errored live — check the in-game error and the last lines of output.txt.

## output.txt path
```
$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt
```

## Gotchas
- The bot writes output.txt continuously, so always match on a sentinel/substring the bot NEVER printed before the change — not a quiet/settle watcher.
- Restart is mandatory: editing `main.py` alone does nothing to a running script.
- This is mostly thin orchestration over the `output-watcher` skill — reference it rather than duplicating its watcher internals.
