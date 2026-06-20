---
name: output-watcher
description: Arm a background watcher on the game's output.txt that auto-detects when an in-game run (probe or bench) completes and feeds the result back, so you never wait for the user to say "done". Use when the user says "output-watcher", "watch output", "set up a watcher", "create the watcher", "auto-watch output.txt", "watch for the run to finish", "don't wait for me to say done", "check the output", "check output.txt", "check the output file", or "read the output" — any request to look at output.txt should arm the watcher rather than do a one-off read.
---

# Output Watcher

Replace the "tell me when you've run it" handoff with a background watcher: it polls
the game's `output.txt`, exits the moment the run completes, and that exit
auto-re-invokes you with the result. Pairs with `game-probe`, `probe-sweep`, and
`bench`, which write the `output.txt` this watches.

`OUT` is always:
`$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt`

## Steps

### 1. Pick the completion sentinel
Identify the string the in-game script prints at the very end:
- `bench` → `VERDICT`
- probes → their custom sentinel (`UNLOCKS_DONE`, `CHASE_DONE`, `SNAKE_DONE`,
  `PROBE_DONE`, `CALIB_DONE`, …)

Choose a sentinel the **live bot never prints** (e.g. `VERDICT`, `*_DONE`) so the
watcher can't false-fire on the bot's normal `Current Goal:` output.

### 2. Arm the watcher (right before telling the user to run the script)
Run with `run_in_background: true` and a generous `timeout` (e.g. `600000`). It polls
until the sentinel appears, prints the interpreted summary, and exits — the exit
re-invokes you. **Sentinel-only form** (use when the run cannot die mid-way, e.g. bench):
```bash
OUT="$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt"
until grep -q "VERDICT" "$OUT" 2>/dev/null; do sleep 3; done
echo "=== RUN COMPLETE ==="
grep -E "VERDICT|WATCH|init|loops_run|Unlocked" "$OUT"
```

### 3. Add a settle fallback for runs that can DIE without a sentinel
A bones snake can self-collide and halt with **no** sentinel; a sentinel-only watcher
would then wait until timeout. Pair the sentinel with a "file went quiet" exit so
silence isn't mistaken for "still running", then dump whatever's there (the last
per-iteration markers pin where it died):
```bash
OUT="$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt"
while true; do
  if grep -q "SNAKE_DONE" "$OUT" 2>/dev/null; then break; fi
  if [ $(( $(date +%s) - $(stat -c %Y "$OUT" 2>/dev/null || echo 0) )) -ge 15 ]; then break; fi
  sleep 3
done
echo "=== RUN ENDED (sentinel or settled) ==="
grep -E "lap |tail|bones gained|SNAKE_DONE" "$OUT" | tail -12
```

### 4. Tell the user to run it, then keep working
Tell the user to **stop the live bot** and run the script (`bench` / `probe`) in-game,
then **just continue** — the watcher reports back on its own. **Do not ask them to say
"done".**

### 5. On exit, interpret and continue
When the background command completes you're handed its stdout. Read the dumped
summary, interpret pass/fail / where it died, and continue the workflow (e.g. narrow a
`probe-sweep` value, or proceed to commit after a `bench` PASS).

## Gotchas
- **Sentinel beats settle while the bot runs.** The live bot writes `output.txt` every
  loop, so a pure settle watcher never fires until the bot is stopped. A sentinel the
  bot never prints (`VERDICT`, `*_DONE`) works even if the bot is still running.
- **Stale sentinels.** `output.txt` is overwritten each run, so a prior run's sentinel
  can false-trigger. Prefer a sentinel the most recent activity overwrote, or require
  the file to be fresh (mtime newer than when you armed it).
- **Freshness-gate EVERY break condition, not just settle.** Hard-won twice: a watcher
  fired on a leftover `Error: goto_sw...` from the previous run, and another fired on a
  stale `COMPANION chain:` marker from a prior variant — both because only the *settle*
  branch checked mtime while the sentinel/error `grep` did not. Capture `ARMED=$(date +%s)`
  and AND every break (`grep` sentinel, `grep "Error:"`, settle) with
  `[ "$(stat -c %Y "$OUT")" -gt "$ARMED" ]`. Tell: byte-identical numbers across "two"
  runs = you matched stale content. When in doubt, `cat "$OUT"` and check its mtime age
  before trusting a match.
- **Always cover failure.** If the run can die (snake collision, parse error), pair the
  sentinel wait with the settle fallback (step 3) — otherwise you wait until timeout.
- **`run_in_background`, not `Monitor`.** This is one completion = one notification, so
  use `Bash` with `run_in_background: true`. `Monitor` is for many notifications.
  `sleep` is fine inside a backgrounded command (foreground `sleep` is blocked).
- **Arm it last.** Arm the watcher right before telling the user to run the script, so
  it's listening when the run starts.
- **mtime freshness fails when the producer keeps writing across a config change.**
  Freshness-gating assumes the only thing touching `output.txt` is the run you want. But
  when measuring the live bot across config variants, the *prior* variant keeps appending
  until the restart, so the file stays fresh (`mtime > ARMED`) and the watcher fires on
  stale prior-variant lines — even with every break condition mtime-gated (hit 2026-06-19:
  the "32-drone" capture was byte-identical to the 14-drone one). When the question is
  "which RUN produced this," mtime isn't enough: have the script print a one-time startup
  marker carrying the variant's identity (e.g. `BOOT MAZE_DRONES=32`), gate on that exact
  fresh marker, and count only lines after it (`awk '/BOOT .../{f=1;next} f&&/MEASURE/{c++}'`)
  — not sample-count + mtime.
