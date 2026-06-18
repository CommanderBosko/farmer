---
name: unlock-status
description: Show the farmer bot's unlock progress — every Unlocks level, its next-level cost, what's left, and which unlock (and bottleneck resource) the bot is steering toward. Use when the user says "unlock-status", "what's left to unlock", "unlock progress", "what is it working toward", "dump the unlocks".
---

# Unlock Status

Probe the game for every Unlocks level and its next cost, then report what's left and what the bot is steering toward next.

## Steps

1. Write this probe to `/home/bosko/projects/farmer/probe.py` (it iterates the Unlocks enum and prints each level plus its next cost). The file auto-syncs into the game via a Save0 symlink:

   ```python
   for u in Unlocks:
       quick_print(str(u) + " | unlocked=" + str(num_unlocked(u)) + " | next_cost=" + str(get_cost(u)))
   quick_print("UNLOCKS_DONE")
   ```

2. Syntax-check the probe:

   ```bash
   cd /home/bosko/projects/farmer && python -c "import ast; ast.parse(open('probe.py').read()); print('OK')"
   ```

3. Arm the `output-watcher` skill for the `UNLOCKS_DONE` sentinel, then have the user stop the bot and run `probe` in-game. (You cannot run it yourself.)

4. Read and interpret the output from `$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt`. List the non-maxed unlocks (those with a non-empty `next_cost`), their cost resources, and identify the one closest to affordable — smallest bottleneck shortfall, i.e. the largest single-resource gap. That is what the bot steers toward next. Note that `next_cost={}` means the unlock is maxed.

## Gotchas

- Game Python dialect: no keyword args, no ternary, no comprehensions, and `global` takes one name per line. This probe uses none of those.
- Pyright errors for `Unlocks`, `num_unlocked`, `get_cost`, and `quick_print` not being defined are EXPECTED — they are game-injected.
- Leans on `game-probe` (probe mechanics + Save0 symlink) and `output-watcher` (auto-read on completion) — reference them rather than duplicating their logic here.
