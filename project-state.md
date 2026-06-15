# Project State — Farmer Bot

Last updated: 2026-06-14

---

## Current Project State

The bot runs the full crop progression unattended and now **farms Bones** (the
last gating mechanic), which unblocked the tech tree. There is also a **`simulate()`
benchmark harness** for catching resource-starvation regressions before they ship.
The prerequisite chain (Hay → Wood → Carrot → Pumpkin → Cactus → Weird_Substance)
is enforced, all strategies except Maze/Bones parallelize across up to 32 drones.

**What works:**
- Full crop cycle: Hay → Wood → Carrot → Pumpkin → Cactus → Maze → Sunflower
- **Bones farming** (`farm_bones()`): dinosaur-hat snake (Hamiltonian boustrophedon,
  bottom row = return lane) eating apples (64 Cactus each) → `tail_length²` Bones.
  Live-validated (~16.9k bones / 8 laps on 32×32), single-drone, even world size only.
  Integrated as a throttled lowest-stock branch; runs unattended.
- **simulate() no-starvation harness**: `gen_bench_main.py` generates `bench_main`
  (terminating twin of `main`), `bench.py` runs it; reports per-resource init/min/final
  + PASS/FAIL (resource ended empty) to output.txt. Drove the carrot-drain fix.
- **Carrot-drain fix**: pumpkin planting costs 256 Carrot; a `MIN_CARROT_FOR_PUMPKIN`
  reserve stops the pumpkin path from draining carrots to 0.
- Multi-prerequisites per crop; multi-drone column splitting (NUM_DRONES, default 32)
- Maze farming (threshold trigger, wall-following safety valve, single-drone)
- Gold tracking / MIN_GOLD_STOCK grinding mode; auto-unlock purchasing
- Planting guards, crop-transition clearing, configurable pre-plant watering

**What is in progress / partially done:**
- **Companion planting** (`get_companion()`): NOT implemented. Polyculture is now
  Lvl 2+, so the 5×→10×→20× yield multiplier is available but unused — the biggest
  remaining throughput opportunity.
- **Pumpkin reliability**: the per-tile pumpkin logic still leaves dead pumpkins and
  doesn't reliably form mega-pumpkins (separate from the carrot-cost fix). A 2026-06-13
  rework was reverted; `main` is on the original logic.

**What is broken / known issues:**
- Pumpkin mega-pumpkin formation is inefficient (see Known Issues). Not blocking.

---

## Current Goals

### Short-term (next 1–3 sessions)
1. **Companion planting** — wire `get_companion()` into the farm loops to apply the
   Polyculture yield multiplier. Validate with the bench harness (yields up, no
   starvation regressions).
2. Observe the live bones trigger end-to-end and tune `BONES_LAPS` / `BONES_LOOP_INTERVAL`.
3. Pumpkin mega-pumpkin reliability (take 2), isolating one variable at a time.

### Long-term
- Full hands-off completion with no manual levers (`MIN_GOLD_STOCK`, `FOCUS_CROP`).
- Harness v2: config auto-tuning, A/B strategy comparison, runtime self-optimization
  (the globals-injection mechanism is already proven out).

---

## Recent Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2026-05-28 | No keyword arguments anywhere | Game parser rejects `func(key=value)` — silent load failure |
| 2026-05-31 | MIN_PREREQ_STOCK = 500 000 | 32-drone throughput accumulates prerequisites fast; large buffer keeps tiers stable |
| 2026-06-13 | Reverted all pumpkin rework to d585c32 | Experiments behaved worse in-game; preserved on `backup/pumpkin-wip-2026-06-13` |
| 2026-06-14 | Built a `simulate()` bench harness as a generated twin of `main` | simulate() runs a file that must terminate; a generated twin keeps strategy single-source vs. duplicating it |
| 2026-06-14 | Bench results come via `output.txt`, not the `globals` dict | The `globals` dict passed to simulate() is not mutated back; quick_print → output.txt is the only readback channel |
| 2026-06-14 | `MIN_CARROT_FOR_PUMPKIN` reserve (default 100k) | Pumpkin planting costs 256 Carrot; without a floor the pumpkin path drains carrots to 0 (oscillation). Found via the harness |
| 2026-06-14 | Bones = throttled lowest-stock branch, single-drone, even size | Only one dino hat; a full snake is a long blocking run, so throttle it; the Hamiltonian cycle closes cleanly only on even sizes |
| 2026-06-14 | Bones validated live, excluded from the bench | `change_hat` errors inside simulate() (hats can't be conveyed), so the sim can't exercise the bones path |

---

## Known Issues / Tech Debt

- **Companion planting unused** — `get_companion()` is available (Polyculture Lvl 2+)
  but no farm loop applies it; leaving the yield multiplier on the table.
- **Pumpkin mega-pumpkin** — original per-tile logic leaves ~20% dead pumpkins and
  doesn't aim for the giant-pumpkin area bonus. Rework attempts on
  `backup/pumpkin-wip-2026-06-13` failed in-game (likely carrot/grid plow-thrash).
  Distinct from the now-fixed carrot *cost* drain.
- **Bones not bench-testable** — the harness can't validate bones (hats error in-sim);
  bones must be checked live. `bench_main` skips it; the verdict excludes it.
- **Harness runs hatless** — the sim can't equip hats, so yields differ slightly from
  production (Pumpkin_Hat bonus absent). Acceptable for no-starvation checks.
- **`MAX_SUNFLOWER_SEED_COST = 6` is stale** — real sunflower cost is 1 Carrot in this
  version. Harmless (it's a conservative guard) but worth correcting if the sunflower
  path is touched.
- **No class/OOP** — hard game constraint; all state is module-level globals.

---

## Next Steps

1. **Companion planting:** read `get_companion()` (returns `[companion_type, x, y]`),
   and in the farm loops plant the preferred companion adjacent to satisfy the
   Polyculture multiplier. Validate via `/bench` (yields rise, PASS holds).
2. Run `main` live and confirm the bones throttle fires `farm_bones()` end-to-end;
   tune `BONES_LAPS` (bones/run vs run length) and `BONES_LOOP_INTERVAL` (frequency).
3. Pumpkin mega-pumpkin take 2 — change one thing, watch one field in-game.
4. Consider harness v2 (auto-tune config knobs against bench run_time).
