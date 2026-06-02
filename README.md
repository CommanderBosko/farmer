# Farmer Bot

A farming automation bot for the game *Farmer Was Replaced*. Written in Python,
designed to run inside the game's scripting sandbox. Automates the full crop
progression from early Hay grinding through late-game Cactus sorting, Maze
treasure runs, Sunflower power farming, and Gold accumulation.

## Current Status

Active development — all core crop strategies implemented and running. Bot starts
cleanly and progresses through the full unlock chain automatically.

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
| `NUM_DRONES` | `32` | Parallel drones for farming. Capped to `world_size`. Maze always single-drone. |

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
├── original-main.py  — Backup of the pre-refactor version (reference only)
├── CLAUDE.md         — AI coding assistant instructions and full API reference
├── session-summary.md — Running log of development sessions
└── project-state.md  — Current project snapshot and next steps
```

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

- Restore sunflower 8x petal-bonus harvesting using a keyword-argument-free
  manual sort.
- Implement Dinosaur Hat / Bones farming.
- Add Polyculture companion planting support once Bones stock is available.
- Investigate Leaderboard / Simulation unlock strategies.

---

## License

Personal project. Not affiliated with the game developers.
