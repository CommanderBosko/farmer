# Farmer Bot

A farming automation bot for the game *Farmer Was Replaced*. Written in Python,
designed to run inside the game's scripting sandbox. Automates the full crop
progression from early Hay grinding through late-game Cactus sorting, Maze
treasure runs, Sunflower power farming, and Gold accumulation.

## Current Status

Active development. All core crop strategies run unattended, the tech-tree blocker
is cleared (Bones farming works and Polyculture Lvl 2 is unlocked), and a
`simulate()`-based benchmark harness guards against resource-starvation regressions.

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
- **Maze farming**: Triggered when `Items.Weird_Substance` reaches
  `MIN_WEIRD_SUBSTANCE_STOCK`. Left-hand wall-following with a step-counter safety
  valve; harvests `Items.Gold` from the treasure chest. Runs single-drone (sequential
  wall-following cannot be split).
- **Gold grinding mode**: Set `MIN_GOLD_STOCK > 0` to prioritize maze runs until a
  gold target is reached (for manually purchasing gold-cost upgrades).
- **Multi-drone grid splitting**: `NUM_DRONES` (default 32) splits the grid across
  parallel drones for Hay/Wood/Carrot/Pumpkin/Cactus/Sunflower. Maze is the only
  single-drone strategy.
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
| `MIN_WEIRD_SUBSTANCE_STOCK` | `500` | Run a maze when WS reaches this level. |
| `MIN_GOLD_STOCK` | `0` | Grind mazes until this much gold is accumulated (0 = inactive). |
| `MIN_WATER_LEVEL` | `0.5` | Pre-plant water threshold for soil crops (carrot, wood, sunflower). `0.0` disables. |
| `NUM_DRONES` | `32` | Parallel drones for farming. Capped to `world_size`. Maze/Bones always single-drone. |
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
├── .claude/skills/   — Project skills: bench, game-probe, config-set, farm-status, syntax-check
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
| `get_next_unlock_goal()` | Returns the next unlock the bot should save toward |
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

**2026-05-31 — Sunflower parallelization and prerequisite buffer increase**

- Parallelized sunflower farming: added `farm_sunflower_strip(start_x, end_x)` and
  rewrote `farm_sunflower()` as an N-drone dispatcher (same column-slice pattern as
  cactus and the standard grid split).
- Raised `MIN_PREREQ_STOCK` from 200 000 to 500 000 — 32 drones accumulate
  prerequisites fast enough that the smaller buffer was insufficient.
- Corrected stale comments in `config.py` and `CLAUDE.md` that listed Sunflower and
  Cactus as single-drone; only Maze remains single-drone.

**2026-05-28 — Bug-fix session**

- Fixed bot-won't-start: `sorted(..., reverse=True)` in `farm_sunflower()` was a
  keyword-argument parse error preventing the entire script from loading.
- Fixed planting guards: all `plant()` calls now pre-check `get_entity_type()`.
- Fixed prerequisite chain: Carrot now requires both Hay AND Wood; PREREQUISITES
  dict supports multiple prerequisites per crop (list of tuples).
- Restored pumpkin broken-tile recovery in the pumpkin wait loop.
- Scaled to 32-drone parallel farming; added `NUM_DRONES` config knob.
- Added multi-drone support, maze safety valve, gold grinding, sunflower farming,
  and comprehensive CLAUDE.md documentation.

---

## Roadmap

- **Companion planting** — apply the Polyculture `get_companion()` yield multiplier
  (5×→10×→20×), now that Polyculture Lvl 2 is unlocked.
- Pumpkin mega-pumpkin reliability (take 2), isolating the carrot/grid plow-thrash.
- Restore the sunflower max-petal bonus using a keyword-argument-free manual sort.
- Harness v2: config auto-tuning / A-B strategy comparison against bench `run_time`.

---

## License

Personal project. Not affiliated with the game developers.
