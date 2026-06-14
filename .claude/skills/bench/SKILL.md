---
name: bench
description: Run the steady-state no-starvation simulation harness for the farmer bot. Use when the user says "bench", "run the bench", "benchmark the bot", "sim-check", or wants to verify main.py won't starve a resource. Regenerates the sim twin from main.py, has the user run it in-game, then reads and interprets the verdict.
---

# Bench Skill — steady-state no-starvation harness

Runs `main.py`'s real strategy inside the game's `simulate()` sandbox for a fixed
number of loops and reports whether any tracked resource hits zero. The bot author
plays "The Farmer Was Replaced"; the harness uses the in-game `simulate()` function.

## How it works (architecture)

- `gen_bench_main.py` generates `bench_main.py` = a terminating twin of `main.py`
  (identical strategy, only the bottom loop differs). This keeps the strategy
  single-source: ALWAYS regenerate before running so the twin can't drift.
- `bench.py` is the in-game runner: it snapshots current unlocks + items and calls
  `simulate("bench_main", ...)`. `bench_main` `quick_print`s a per-resource
  init/min/final table + verdict to `output.txt`.
- Tracked resources: hay, wood, carrot, pumpkin, cactus, gold, bones.

## Steps

1. **Regenerate + syntax-check the twin** (never edit `bench_main.py` directly —
   edit `gen_bench_main.py`):
   ```bash
   cd /home/bosko/projects/farmer && python3 gen_bench_main.py && python -m py_compile bench_main.py bench.py && echo OK
   ```

2. **Confirm the sim files are synced into the game.** `bench` and `bench_main`
   must be symlinked in the game's Save0 (see [[game-file-sync]] memory). Check:
   ```bash
   ls -la "$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/Saves/Save0/" | grep -E 'bench'
   ```
   If a symlink is missing, create it (game closed, then reload save to register a
   brand-new file): `ln -sf /home/bosko/projects/farmer/<name>.py "<Save0>/<name>.py"`.

3. **Ask the user to run `bench` in-game** and say "done". You cannot run it
   yourself. (Regenerated content auto-syncs via the symlink; no reload needed
   unless the file is brand new.)

4. **Read and interpret the result** from output.txt (grep past game warning spam):
   ```bash
   OUT="$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt"
   grep -nE "BENCH|VERDICT|WATCH|init |loops_run|outer:" "$OUT"
   ```
   - `VERDICT: PASS` — no tracked resource hit zero.
   - `VERDICT: FAIL - starved (hit zero): ...` — a resource collapsed; that's a real
     set-and-forget failure to investigate in `main.py`.
   - `WATCH (spent down, above zero): ...` — non-fatal; the bot draws down its
     highest stock to top up the lowest. Not a failure.
   - `bones` will read 0 (Bones farming is unimplemented — known gap, expected flag).

## Knobs

- `MAX_LOOPS` (in `gen_bench_main.py`, default 20) — how many full strategy passes to
  simulate. Lower = faster, higher = catches slower drains. Regenerate after changing.

## Gotchas (see [[simulate-sandbox]] memory)

- The sim is structurally **hatless** and has **no** `get_op_count`/`get_time` — the
  twin avoids them. Don't reintroduce them into the bench bottom.
- The bones item is `Items.Bone` (singular), not `Items.Bones`.
- Pyright "undefined" errors for `Items`/`Unlocks`/`simulate`/`quick_print` are
  expected (game-injected) — not real errors.
- `output.txt` is overwritten each run, so it only holds the latest run.
