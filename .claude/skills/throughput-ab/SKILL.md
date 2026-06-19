---
name: throughput-ab
description: Empirically compare the wall-clock THROUGHPUT (resources/second) of two farmer-bot strategy variants live in-game, so "is X actually faster than Y?" is settled with data, not analysis. Use when the user says "throughput-ab", "which is faster", "is X faster than Y", "measure resources per second", "A/B the strategies", "perf compare", "compare monoculture vs companion", or doubts a speed claim. Complements `bench` (which checks no-starvation, NOT speed).
---

# Throughput A/B

Settle a "which farming strategy is faster?" question by **measuring** wall-clock
resources/second for each variant live, instead of reasoning about it. Built because
per-move / per-harvest efficiency analysis is a TRAP: it ignores drone parallelism. A
single-drone ×160 strategy looked like a win on paper and measured ~19× SLOWER than
32-drone monoculture, because 32 parallel drones beat a 2.8×-per-drone multiplier. Only
wall-clock throughput, measured the same way for both variants, tells the truth.

`OUT` is always:
`$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt`

## The core idea
Add a temporary per-loop print of the in-game clock + the resource stocks. Then for each
variant (a config setting), run the bot a while and read how much the resource grew per
second from consecutive lines. Same goal, same clock, same field → a fair comparison.

## Steps

### 1. Add temporary instrumentation
At the TOP of the `while True:` loop in `main.py` (right after `loop_counter += 1`), add
one sample line. `get_time()` returns game run-time in seconds (Timing unlock; works live,
unlike `get_op_count`). Capture every resource that matters — include all of a mixed
strategy's outputs (e.g. a companion chain makes Hay+Wood+Carrot), so you can compare both
per-target and total:
```python
	quick_print("MEASURE t=" + str(get_time()) + " wood=" + str(num_items(Items.Wood)) + " hay=" + str(num_items(Items.Hay)) + " carrot=" + str(num_items(Items.Carrot)))
```
Syntax-check (`python -c "import ast; ast.parse(open('main.py').read())"`). Do NOT commit
this; it's working-tree-only and removed at the end. The game runs the symlinked
working-tree `main.py`, so no regen needed for the measurement.

### 2. Force the SAME goal for both variants
Pin the goal so both variants farm the identical resource — usually `FOCUS_CROP="<Crop>"`
in `config.py`. Apples-to-apples requires the same goal, same world size, same power state.

### 3. Measure variant A
Set A's config (e.g. `COMPANION_AUTO=False` for 32-drone monoculture). Arm a
**freshness-gated** watcher (see Gotchas — break only on `mtime > ARMED` so leftover
MEASURE lines from a prior variant can't false-fire), tell the user to **restart main.py**,
and collect N samples. Fast multi-drone variants emit a MEASURE line every few seconds
(get ~8). Slow single-drone variants emit one per sweep (get ≥3 = 2 full sweeps):
```bash
OUT="$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt"
ARMED=$(date +%s)
while true; do
  N=$(grep -c "MEASURE t=" "$OUT" 2>/dev/null)
  MT=$(stat -c %Y "$OUT" 2>/dev/null || echo 0)
  if [ "${N:-0}" -ge 8 ] && [ "$MT" -gt "$ARMED" ]; then break; fi
  if grep -q "Error:" "$OUT" 2>/dev/null && [ "$MT" -gt "$ARMED" ]; then break; fi
  sleep 4
done
echo "=== VARIANT A SAMPLES ==="; grep -E "MEASURE t=|Error:" "$OUT" | tail -14
```

### 4. Measure variant B
Set B's config (e.g. `COMPANION_AUTO=True`), re-arm the same freshness-gated watcher,
have the user restart again, collect samples. Keep `FOCUS_CROP` the same as A.

### 5. Compute and compare
For each variant, rate = Δresource / Δt across consecutive samples. **Skip the first
sample** (planting transient — a resource can briefly DIP as seeds are paid). Average the
rest. Present a table of `resource/sec` per variant (and total/sec for mixed strategies),
state the ratio, and recommend the winner. Sanity-check intervals are consistent.

### 6. Clean up and lock in the winner
Remove the MEASURE line from `main.py`, set the winning config, then run `ship-change`
(syntax-check + regen bench twin + commit). Correct any stale "X is faster" claims in
config comments / memory with the measured numbers — wrong perf claims are worse than none.

## Gotchas
- **Throughput ≠ per-move efficiency.** The whole reason this skill exists: a strategy can
  win per-drone and lose massively on wall-clock because of parallelism (32 drones vs 1).
  Never conclude "faster" from moves/harvest — only from measured resource/second.
- **Freshness-gate the watcher.** Gate EVERY break condition on `mtime > ARMED`. Variant
  A's MEASURE lines (and any stale `Error:`) sit in `output.txt` until variant B's restart
  truncates it — an un-gated grep fires on the leftovers and you compare A against A.
- **Skip the first sample.** Wood/Carrot can dip on the first loop as tree/carrot seeds are
  paid; including it skews the rate.
- **Single-drone variants are slow.** One MEASURE per sweep, and a sweep can be ~10+ min —
  budget ≥2 sweeps (≥3 samples) and a generous watcher timeout; don't mistake "still
  sweeping" for "hung".
- **Config reloads only on restart.** `import config` is cached in the running script;
  each variant needs a main.py restart to take effect (the user does this).
- **Same goal both runs.** Different `FOCUS_CROP` between variants invalidates the A/B.
