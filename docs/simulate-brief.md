# Project Brief — `simulate()` regression/safety harness (v1)

_Status: confirmed 2026-06-14. Reviewed by an independent agent; all findings folded in._

## Goal

Use the game's `simulate()` to run `main`'s **real** strategy in a sandboxed,
high-speed simulation and prove it progresses to a reachable milestone without
deadlocking or starving a resource. This is the foundation later reused for
config auto-tuning, A/B strategy benchmarking, and runtime self-optimization.

## `simulate()` reference

```python
run_time = simulate(filename, unlocks, items, globals, seed, speedup)
```

- `filename` — script to run, e.g. `"main"` (string, no extension)
- `unlocks`  — dict `{Unlocks.X: level}` the sim starts with
- `items`    — dict `{Items.X: count}` starting inventory
- `globals`  — dict of starting global-variable values
- `seed`     — RNG seed; `-1` = random
- `speedup`  — run multiplier (e.g. `10000`)
- returns    — in-game **time the run took to finish** (the file MUST terminate)

Requires the gold-cost **Simulation** unlock. Building the dict args needs
`Lists` + `Dictionaries`; populating from live state needs `Auto_Unlock`
(`num_unlocked`) and `Costs`. No kwargs / comprehensions / ternaries anywhere.

## Finish line (the timed termination condition)

Terminate when `main` reaches a **milestone it can hit today** — default:
`num_unlocked(Unlocks.Mazes) > 0 and gold > 0` (full progression through Cactus
into Mazes with at least one treasure) — **OR** a **max-tick budget**,
whichever comes first.

The full-tree goal is **blocked-on-Bones** (Dinosaurs/Bones farming
unimplemented; Polyculture Lvl 2 needs 10,000 Bones) and is NOT a v1 target.

## No-starvation = checked throughout, not at the end

The sim records a per-resource **min-stock-seen** (Hay, Wood, Carrot, Pumpkin,
Cactus, Gold) into globals during the run. The harness inspects them after
`simulate()` returns.

- **PASS** — milestone reached AND no resource floor breached.
- **FAIL** — tick cap hit (deadlock) OR a resource collapsed, reported with which.

## Form factor

1. **`probe.py` (built + run FIRST — gates everything).** Proves the `globals`
   dict both (a) injects a readable module variable into the simulated file and
   (b) can be read back after the run. If readback doesn't exist, FAIL
   diagnostics degrade to "FAIL without reason" and we re-scope.
2. **`main.py` hook.** Declare `bench_goal = 0` at module scope (safe default →
   live bot byte-for-byte unchanged). When set, the loop checks
   milestone-or-tick-cap and returns; records min-stock-seen globals.
3. **`bench.py` harness.** Builds `unlocks`/`items` dicts `d[k]=v` line-by-line
   from a hardcoded roster shared in `config.py` (no third copy), pins a seed,
   calls `simulate("main", ...)`, prints time + PASS/FAIL + reason.
4. **`/bench` skill.** Runs the harness and interprets output.

## Prerequisite unlocks

`Simulation` (gold), `Lists`, `Dictionaries`, `Auto_Unlock`, `Costs`.

## Out of scope (v1)

Auto-tune sweeps, A/B comparison, runtime self-optimization, strategy
duplication, multi-seed robustness sweeps (pin one seed for now).

## Definition of done

`probe.py` confirms the globals channel; running `bench.py` prints a `run_time`
and a PASS when `main` reaches the milestone clean, or a FAIL naming the
deadlock/starved resource; the live bot is provably unaffected when `bench_goal`
is absent/0.

## Remaining risks

- The globals readback channel may not exist — `probe.py` decides this.
- Tick-budget value needs calibration against real sim speed.
- The `config.py` unlock roster needs hand-maintenance as unlocks are added.
