# Farmer Bot

A farming automation bot for the game *Farmer Was Replaced*. Written in Python,
designed to run inside the game's scripting sandbox. Automates the full crop
progression from early Hay grinding through late-game Cactus sorting, Maze
treasure runs, Sunflower power farming, and Gold accumulation.

## Current Status

Active development. The bot is **unlock-driven**: `plant_decision()` runs an Energy
floor, then steers all effort to whatever resource the next upgrade needs (any
resource, dynamically), and only falls back to lowest-stock balancing once the tech
tree is fully maxed. It runs **32-drone monoculture** — the fast path. A `simulate()`-based
harness guards against resource-starvation regressions. Steering is toward **Top_Hat**, the
**final** unlock (crop costs met; the live bottleneck is **Gold**). The gold/maze path is
now **multi-drone** (`MAZE_DRONES` solvers around the field perimeter, default 32 — see
Features), making the previously slowest goal ~2–5× faster. With the tree nearly complete,
focus is shifting to **game achievements** (five unlocked, captured as the
`achievement-hunter` skill) and Leaderboards.

A full Polyculture **companion-farming** feature (`get_companion()`) was built this
session but **measured ~19× slower** than 32-drone monoculture (single-drone can't beat
32× parallelism even at the ×160 multiplier), so it ships **default-OFF** — kept for the
verified mechanic and a possible future multi-drone rebuild.

---

## Features

- **Full crop cycle**: Hay → Wood → Carrot → Pumpkin → Cactus → Maze, automatically
  progressing as prerequisite stock thresholds are met.
- **Prerequisite chain enforcement**: Each crop requires the previous tier's
  resources to be stocked above `MIN_PREREQ_STOCK` before advancing. Multiple
  prerequisites per crop are supported (e.g., Carrot requires both Hay and Wood).
- **Sunflower power farming**: Triggered when `Items.Power` drops below
  `MIN_POWER_STOCK`. Power doubles drone movement speed automatically. Parallelized
  across N drones via `farm_sunflower_strip()`.
- **Maze farming (parallel)**: Triggered when Gold is the resource being farmed (and
  enough `Items.Weird_Substance` is stockpiled). `MAZE_DRONES` solvers (default 32) are
  placed evenly around the field perimeter *before* the maze is grown (walls block
  placement after), then all left-hand wall-follow the one maze at once; the entry point
  nearest the treasure wins and harvests `Items.Gold`, and the rest bail the instant
  `num_items(Gold)` jumps (coordination via the live-shared inventory, since drone globals
  are copied). `MAZE_DRONES=1` is the original single-drone solve; `=4` is the four corners.
- **Gold grinding mode**: Set `MIN_GOLD_STOCK > 0` to prioritize maze runs until a
  gold target is reached (for manually purchasing gold-cost upgrades).
- **Multi-drone grid splitting**: `NUM_DRONES` (default 32) splits the grid across
  parallel drones for Hay/Wood/Carrot/Pumpkin/Cactus/Sunflower. Maze parallelism is
  controlled separately by `MAZE_DRONES` (perimeter solvers); Bones runs single-drone.
- **Auto-unlock purchasing**: `auto_unlocks()` buys the next unlock in the ordered
  progression whenever resources are sufficient.
- **Crop transition clearing**: Before any `plant()` call, if the cell holds a foreign
  entity, the bot harvests it (if ready) then tills to clear it. A `get_ground_type()`
  guard after each clearing `till()` prevents the Soil→Grassland toggle edge case.
- **Configurable pre-plant watering**: `MIN_WATER_LEVEL` (default 0.5) causes the bot
  to water any soil cell below that moisture threshold before planting (carrot, wood,
  sunflower). Pumpkin always waters to 1.0 regardless.
- **Planting guards**: All `plant()` calls are preceded by `get_entity_type()` checks
  to avoid "Didn't have required items" warnings on occupied tiles.
- **Pumpkin broken-tile recovery**: The pumpkin wait loop includes `harvest()` +
  `plant()` to recover tiles where pumpkins fail to plant or break.
- **Cactus phase state machine**: Full bubble-sort pipeline (plant → wait →
  sort rows → sort columns → harvest) for maximum cactus yield.
- **Bones farming**: `farm_bones()` wears the Dinosaur hat and runs a snake
  (Hamiltonian boustrophedon, reserved return lane) eating apples to grow a tail,
  then unequips to cash out `tail_length²` Bones. Throttled lowest-stock rotation;
  single-drone; even world size only.
- **simulate() benchmark harness**: `gen_bench_main.py` + `bench.py` run the real
  strategy in the game's `simulate()` sandbox and report per-resource
  init/min/final + PASS/FAIL, catching starvation bugs before they ship. Driven via
  the `/bench` skill.

---

## Getting Started

### Prerequisites

- *Farmer Was Replaced* (Steam) with at least the `Unlocks.Loops` and `Unlocks.Plant`
  unlocks purchased in-game.
- The game's scripting sandbox injects its own Python environment — no pip packages
  or imports are needed or allowed (beyond standard library modules the game provides).

### Installation

1. Copy `main.py` and `config.py` into the game's script directory (shown in-game).
2. Adjust `config.py` to match your current unlock level (see Configuration below).
3. Run the script from inside the game.

### Configuration

Edit `config.py` before running:

| Variable | Default | Effect |
|---|---|---|
| `FOCUS_CROP` | `None` | Force a single crop type. `None` = dynamic progression. |
| `PRINT_GOAL_INTERVAL` | `1` | Print status every N outer loops. `0`/`None` = silent. |
| `MIN_PREREQ_STOCK` | `500 000` | Minimum previous-tier stock before advancing to the next crop. |
| `MIN_POWER_STOCK` | `5 000` | Switch to sunflower farming when power drops below this. |
| `MIN_GOLD_STOCK` | `0` | Grind mazes until this much gold is accumulated (0 = inactive). |
| `MIN_WATER_LEVEL` | `0.5` | Pre-plant water threshold for soil crops (carrot, wood, sunflower). `0.0` disables. |
| `NUM_DRONES` | `32` | Parallel drones for grid farming. Capped to `world_size`. Maze uses `MAZE_DRONES`; Bones is single-drone. |
| `MAZE_DRONES` | `32` | Solver drones spread around the perimeter for a gold/maze run. `1` = single-drone; `4` = four corners. Capped to 32 and the perimeter. |
| `MIN_CARROT_FOR_PUMPKIN` | `100 000` | Carrot reserve the pumpkin path won't dip below (pumpkins cost 256 Carrot each). |
| `MIN_CACTUS_FOR_BONES` | `100 000` | Cactus reserve required before a bones run (apples cost 64 Cactus each). |
| `BONES_LOOP_INTERVAL` | `10` | Run bones at most once per this many outer loops. |
| `BONES_TARGET_TAIL` | `900` | Target snake tail length (apples eaten) per bones run; bones ≈ ~40×·tail² (≈32M at 900). |

`FOCUS_CROP` bypasses all prerequisite checks — manually pre-stock required
resources before enabling it.

### Running

```bash
python main.py
```

The script runs indefinitely. Stop it from the game's interface.

---

## Project Structure

```
farmer/
├── main.py           — All bot logic; entry point is the bottom of the file
├── config.py         — User-tunable knobs (see table above)
├── gen_bench_main.py — Generates bench_main.py (a terminating twin of main) for the harness
├── bench.py          — In-game runner for the simulate() benchmark
├── original-main.py  — Backup of the pre-refactor version (reference only)
├── CLAUDE.md         — AI coding assistant instructions and full API reference
├── docs/             — simulate-brief.md (harness design brief)
├── .claude/skills/   — 13 project skills (bench, game-probe, throughput-ab, ship-change, …)
├── session-summary.md — Running log of development sessions
└── project-state.md  — Current project snapshot and next steps
```

`bench_main.py` is generated (gitignored); regenerate it with `python3 gen_bench_main.py`.

### Key functions in main.py

| Function | Purpose |
|---|---|
| `update_amounts()` | Syncs global inventory vars from game state |
| `plant_decision()` | Selects the crop for this iteration |
| `check_stock(item)` | Walks the prerequisite chain to find the lowest-stocked crop |
| `auto_unlocks()` | Purchases the next unlock when affordable |
| `farm_grid(crop, x0, x1)` | Traverses columns x0..x1, calling farm() per cell |
| `farm(crop)` | Per-cell planting/harvesting for a given crop type |
| `farm_cactus()` | Five-phase cactus state machine |
| `farm_sunflower_strip(x0, x1)` | Column-slice sunflower traversal (called by each drone) |
| `farm_sunflower()` | N-drone dispatcher: spawns strips, waits for all drones |
| `farm_maze()` | Wall-following maze solver; harvests gold from treasure chest |
| `farm_bones()` | Dinosaur-hat snake; grows a tail eating apples, unequips for `tail²` Bones |
| `get_next_unlock()` | Returns the next unlock being worked toward and its bottleneck resource |
| `goto_sw()` | Navigates drone to origin (x=0, y=0) |

---

## Scripting Constraints

The game's Python parser enforces restrictions that differ from standard CPython:

- **No keyword arguments** — `func(key=value)` is a parse error. Use positional arguments only.
- **No classes** — OOP is not supported. All state is module-level globals.
- **No advanced comprehensions** — keep comprehensions simple; no class-scope usage.
- **No imports** — game APIs (`plant()`, `harvest()`, `Items`, `Entities`, etc.) are injected at runtime, not imported.

Violating the keyword-argument rule causes a silent script-load failure — the bot
will not start and the game gives no error message.

---

## Recent Changes

**2026-06-19 (PM) — Parallel maze gold, five achievements, `achievement-hunter` skill**

- **Parallelized the gold/maze path** (`farm_maze()`, `config.MAZE_DRONES`, default 32):
  `MAZE_DRONES` solvers are placed evenly around the field perimeter before the maze grows,
  then race the one maze; nearest-to-treasure wins and harvests, losers bail when
  `num_items(Gold)` jumps. Measured ~2× (4 drones) to ~4.7× (14) faster gold/sec. `=1`
  falls back to the original single-drone solve; `=4` is the old four corners.
- **Verified the multi-drone mechanics live first**: spawned drones start on the parent's
  tile, globals are copied per drone (coordinate via world state), drones don't block each
  other, and `num_items()` is a live shared inventory across drones.
- **Power confound caught**: 32 drones measured *slower* than 14 only because
  `FOCUS_CROP="Maze"` disables the energy floor and power hit 0 (half speed); with the floor
  active (`FOCUS_CROP=None`) 32 ties/edges 14. Default `MAZE_DRONES=32`.
- **Unlocked five game achievements** via throwaway `probe.py` scripts (5 hats on drones,
  stack overflow, healer, circular import, wrong-order cacti) and captured the workflow as
  the `achievement-hunter` skill. Hardened `throughput-ab` and `output-watcher` with the
  power-confound and stale-variant (BOOT-marker) gotchas.

**2026-06-19 — Polyculture companion farming: built, measured ~19× slower, shelved**

- Verified the `get_companion()` mechanic live (returns `(type,(x,y))`, absolute +
  wrapping coords, stable per plant, ×160 multiplier; only Grass/Bush/Tree/Carrot
  participate). Saved to project memory.
- Built companion farming in three stages, all default-OFF behind `config.COMPANION_*`:
  `farm_companion()` (triplet, single-crop), `farm_companion_chain()` (chain-random,
  mixed Hay+Wood+Carrot), and cost-driven auto-routing (`COMPANION_AUTO`).
- A timed live A/B settled it: single-drone companion ≈ 0.24M wood/sec vs 32-drone
  monoculture ≈ 4.47M wood/sec — **monoculture ~19× faster**. Reverted to monoculture
  (the ×160 per-harvest gain can't overcome 32× drone parallelism).
- Added the `throughput-ab` skill (measure resources/sec to A/B strategies); hardened
  `output-watcher` and `game-probe` with stale-content / probe-isolation gotchas.

**2026-06-18 — Pumpkin/Bones fixes, unlock-steering rework, skill toolkit**

- **Decision rework**: `plant_decision()` now steers to the next unlock's bottleneck
  resource (via `get_next_unlock()`) and farms only that until the unlock is affordable;
  lowest-stock balancing is the post-all-unlocks fallback. `auto_unlocks()` now buys any
  fully-affordable unlock (multi-resource aware), fixing a bug that stranded Polyculture.
  The goal line reads `Current Goal: <crop> for Unlock: <unlock>`.
- **Bones**: rewrote `farm_bones()` to target an apple/tail count (`BONES_TARGET_TAIL`,
  default 900 → ~32M Bones) instead of laps, counting apples via `measure()` and cashing
  out at exactly the target. Fixed a bug where an origin-offset snake ate its own tail and
  halted the whole bot. Calibrated: bones ≈ 40×tail², self-collision at tail ~1023.
- **Pumpkin**: fixed empty plots (the wait loop was re-planting living pumpkins and
  resetting growth) and hardened fertilizer/water handling; dead pumpkins are cleared by
  `plant()` (never `till()` — it poisons the soil).
- Removed the dead `MIN_WEIRD_SUBSTANCE_STOCK` knob (mazes now run when Gold is needed).
- Added 7 project skills: `probe-sweep`, `output-watcher`, `ship-change`,
  `verify-mechanic`, `diagnose-behavior`, `unlock-status`, `live-verify`.

**2026-06-14 — simulate() harness, carrot-drain fix, and Bones farming**

- Built a `simulate()` no-starvation benchmark harness (`gen_bench_main.py` generates
  a terminating twin of `main`; `bench.py` runs it; results read from `output.txt`).
- The harness reproduced a carrot-drain bug — pumpkin planting costs 256 Carrot and
  drained the buffer to 0 — fixed with a `MIN_CARROT_FOR_PUMPKIN` reserve.
- Implemented **Bones farming** (`farm_bones()`), a Dinosaur-hat snake yielding
  `tail_length²` Bones; live-validated (~16.9k bones / 8 laps). This cleared the
  Polyculture Lvl 2 blocker (10k Bones), which is now unlocked.
- Added project skills `/bench` and `/game-probe`; moved farm skills to project scope.

**2026-06-13 — Pumpkin rework explored and reverted (no net code change)**

- Investigated pumpkin farming after it ran out of carrots and left dead pumpkins on
  the grid. Documented the real mechanic (~20% of pumpkins die at maturity; a square
  only merges into a giant when every tile is grown and alive at once; planting a
  pumpkin costs carrots and auto-replaces a dead one).
- Attempted a full mega-pumpkin rework (sweep-based → dead-pumpkin handling →
  field convergence → multi-drone strips); each behaved worse in-game and was reverted.
- `main` was reset to the prior commit; the experiments are preserved on branch
  `backup/pumpkin-wip-2026-06-13`. Pumpkin still uses the original per-tile logic.

**2026-06-01 — Crop transition clearing and MIN_WATER_LEVEL watering**

- Fixed crop transition bug: when switching to a new crop, foreign entities (e.g.
  immature carrots in a sunflower strip) were not being cleared before planting. Added
  `can_harvest()` + `harvest()` + `till()` + ground-type recheck before every `plant()`
  call in the entity-clearing path. Applied to carrot, wood-tree, wood-carrot-fill,
  pumpkin, and both passes of `farm_sunflower_strip()`.
- Fixed `till()` toggle bug: an unconditional `till()` after a clearing step was
  bouncing a Soil cell back to Grassland. All `till()` calls are now guarded with
  `if get_ground_type() != Grounds.Soil`.
- Added `MIN_WATER_LEVEL = 0.5` to `config.py` and corresponding watering logic to
  carrot, wood, and sunflower branches. Pumpkin's full-water-to-1.0 loop is unchanged.

_Older sessions are summarized in `session-summary-archive.md`._

---

## Roadmap

- **Finish the tech tree**: grind Top_Hat's remaining bottleneck (Cactus, then Gold) to
  fully max the unlocks, then run steady-state balance indefinitely.
- **Fertilizer auto-trade** — add `trade(Items.Fertilizer)` so Weird Substance (→ Gold via
  maze) is self-sustaining; load-bearing now that Gold is a Top_Hat bottleneck.
- Pumpkin mega-pumpkin reliability (take 2), isolating the carrot/grid plow-thrash.
- Companion farming only becomes worthwhile via a **multi-drone (multi-strip) chain** or a
  much higher Polyculture level — revisit only if the throughput math flips (use `throughput-ab`).

---

## License

Personal project. Not affiliated with the game developers.
