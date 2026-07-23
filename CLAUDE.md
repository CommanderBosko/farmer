# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Scope First (Interview)

Before you do any work, use the `/interview` skill to pin down the real goal with the user — don't start building from a fuzzy or assumed understanding of the request. Surface the unknowns, confirm scope and constraints, and only proceed once the target is clear. Do this in tandem with the Verification Plan below: the interview establishes *what* we're building and how we'll know it's done, and the verification plan establishes *how we'll prove* it works. Lay out both together, up front, before starting the work.

## Verification Plan

Before you do any work, state how you'll verify it with the `/verify` skill — say up front how you'll confirm each part actually works before calling it done. Pick the checks that fit this project (build, test suite, linter, type-check, running the app, hitting the endpoint, reading the logs) and name the specific commands. Lay out the plan with the work, not after it.

## Parallelize with Sub-Agents

**This rule is your standing authorization to spawn sub-agents — you do not need to ask first.** Once scope and the verification plan are set, before starting any task with more than one independent part, stop and run a parallelization check. This is a required step, not an aspiration: ask "Can I split this into pieces that don't depend on each other's output?" If yes, spawn one sub-agent per piece in a single message and let them run concurrently.

Trigger parallelization whenever you hit any of these:
- About to research, search, or read across 2+ areas of the tree that don't depend on each other.
- About to scaffold or draft 2+ files whose *contents* don't reference each other.
- You catch yourself planning "do A, then B, then C" where B doesn't need A's result.

Reserve serial work for genuine dependencies — e.g. a new file and the line elsewhere that imports it are coupled, so keep them together. When the pieces are independent, default to fanning out breadth-first; state in your plan which pieces run in parallel and why.

## Use Existing Skills First

Before doing a task by hand, check whether an existing skill already covers it and invoke it instead of improvising. Skills encode the agreed, repeatable way to do a thing — prefer them over ad-hoc steps. If you find yourself doing the same multi-step task a second time and no skill exists, offer to create one.

## Ask via AskUserQuestion

When you need a decision, choice, or clarification from the user — not just information you can look up yourself — use the **AskUserQuestion** tool rather than asking in plain text. Phrase it as 2-4 concrete options (with a recommended one first); when the answer could be open-ended, the tool's built-in "Other" choice covers free text. This keeps answers structured, makes trade-offs explicit, and avoids an answer getting buried in prose. Reserve plain-text questions for genuinely open, generative prompts where no sensible options exist yet (e.g. "describe the project in your own words").

## Running

```bash
python main.py
```

No build, lint, or test tooling exists. This is a procedural Python script.

## Architecture

This is a farming automation bot for a game. The game injects its own API at runtime — functions like `plant()`, `harvest()`, `unlock()`, `move()`, and enums like `Items`, `Entities`, `Grounds`, `Unlocks`, `Hats` are **not defined in this repo** and must not be imported or stubbed.

### Files

- `main.py` — all logic; entry point is the bottom of the file
- `config.py` — user-tunable knobs (see below)
- `original-main.py` — backup of the pre-refactor version

### Control flow

1. Initialization: `clear()`, `change_hat()`
2. Infinite loop:
   - `update_amounts()` — sync global inventory vars from game
   - `auto_unlocks()` — buy any unlock whose full `get_cost()` is affordable (`can_afford`)
   - `plant_decision()` — pick what to farm (see below)
   - `farm_grid(crop_choice, start_x, end_x)` or multiple drones on split columns (or `farm_cactus`/`farm_maze`/`farm_sunflower`/`farm_bones` for the special goals)
   - Periodic goal status print: `Current Goal: <crop> for Unlock: <unlock>` (or `... Unlocks Complete!`)
   - Final harvest + position reset

**`plant_decision()` priority** (config `FOCUS_CROP` overrides everything):
   1. **Energy floor** — if `power < MIN_POWER_STOCK`, farm Power (sunflowers), guarded by a carrot buffer.
   2. **Unlock steering** — `get_next_unlock()` finds the next non-maxed unlock and the single cost resource it's most short of (the bottleneck); the bot farms *only* that resource until the unlock is affordable, then `auto_unlocks` buys it and the bottleneck shifts. Each resource builds its own prerequisite first: Bone→snake (cactus buffer), Gold→maze (or pumpkins to regenerate Weird_Substance), crops→`check_stock`. No throttling/balancing while unlocks remain.
   3. **Lowest-stock balance** — only once every unlock is maxed: farm whichever of Hay/Wood/Carrot/Pumpkin/Cactus/Bones/Gold is lowest (Bones throttled by `BONES_LOOP_INTERVAL`; Gold only with enough Weird_Substance).

### Key design constraints

- **Procedural only** — the game environment does not support Python classes or advanced syntax. No OOP, no dataclasses, no comprehensions that rely on class scope.
- **Global state** — resource counts (`hay`, `wood`, `carrot`, `pumpkin`, `cactus`, `weird_substance`, `fertilizer`, `water`, `power`, `gold`, `loop_counter`) are module-level globals mutated by `update_amounts()`.
- **Data-driven unlock logic** — unlock ordering and prerequisite checks use tuple/dict tables (`UNLOCK_NAMES`, `PREREQUISITES`, `FOCUS_CROP_MAP`) so new tiers can be added without touching control flow.

### config.py knobs

| Variable | Effect |
|---|---|
| `FOCUS_CROP` | Force-plant one crop type (`"Hay"`, `"Wood"`, `"Carrot"`, `"Pumpkin"`, `"Cactus"`, `"Maze"`, `"Sunflower"`, `"Bones"`, or `None` for dynamic) |
| `PRINT_GOAL_INTERVAL` | Print status every N outer loops; `0`/`None` disables |
| `MIN_PREREQ_STOCK` | Minimum prerequisite resource to hold before advancing to a higher-tier crop (default 100 000) |
| `MIN_POWER_STOCK` | Replenish sunflowers when power drops below this; power doubles drone speed (default 500) |
| `MIN_GOLD_STOCK` | When `> 0`, prioritize maze runs until this gold target is reached; set before manually buying gold-cost upgrades, reset to `0` when done (default 0) |
| `NUM_DRONES` | Number of parallel drones (1–32); capped to `world_size`; drives the Hay/Wood/Carrot/Pumpkin grid split and the Cactus/Sunflower strip functions. Maze parallelism is separate (`MAZE_DRONES`); Bones always runs single-drone. Requires Megafarm upgrade (default `32`) |
| `MAZE_DRONES` | Number of solver drones for a gold/maze run, spread evenly around the field perimeter; nearest-to-treasure wins, losers bail when `num_items(Gold)` jumps. `1` = original single-drone solve; `4` reproduces the old four-corner placement. Capped to 32 and to the perimeter; falls back to single-drone when `world_size < 2`. Measured scaling: 4→1358, 14→3136 gold/sec under `FOCUS_CROP="Maze"`; 32 ties/slightly beats 14 only with `FOCUS_CROP=None` (energy floor keeps power up — under maze-focus, 32 drains power to 0 and halves speed). Default `32` |
| `MIN_CACTUS_FOR_BONES` | Cactus reserve required before a bones run (apples cost 64 Cactus each); default 100 000 |
| `BONES_LOOP_INTERVAL` | Throttle: run bones at most once per this many outer loops (default 10) |
| `BONES_TARGET_TAIL` | Target snake tail length (= apples eaten) per bones run; `farm_bones()` counts apples via `measure()` on the safe cycle and `bones_step()` cashes out at *exactly* this length; bones ≈ ~40×·`tail²` (≈32M at 900); self-collision is live-confirmed at tail ~1023 (the 1024-tile field), so keep under ~950 — a collision halts the whole bot (default 900) |

### Crop farming strategies (inside `farm()`)

- **Hay** — harvest and maintain grassland terrain
- **Wood** — plant trees on a diagonal checkerboard; fill other cells with carrots
- **Carrot** — harvest and replant on soil
- **Pumpkin** — water → plant → fertilize (or `do_a_flip()` if no fertilizer) → wait → harvest
- **Cactus** — phase state machine in `farm_cactus()`; see Scripting gotchas below
- **Maze** — runs when **Gold** is the resource being farmed (Gold is the next unlock's bottleneck, or the lowest stock once all unlocks are maxed) and enough `Items.Weird_Substance` is stockpiled for one run; returned as `Items.Gold` from `plant_decision()` and dispatched to `farm_maze()`. With `config.MAZE_DRONES > 1` (default `32`), `farm_maze()` `clear()`s, then walks a solver to each of `MAZE_DRONES` points spread evenly around the field perimeter (`maze_perimeter_pos()`) *before* growing the maze (so they're placed on open ground — walls would block post-growth), grows the maze from the origin (perimeter index 0), and all of them left-hand wall-follow at once (`maze_solver()`): whichever entry point is nearest `Entities.Treasure` on the wall-following circuit reaches it first and harvests, and the others bail the instant `num_items(Items.Gold)` jumps (live-shared across drones — no slow-loser tail). Step-counter safety valve `world_size² × 4` per solver; `clear()` again to reset. `MAZE_DRONES == 1` (or `world_size < 2`) uses `farm_maze_single()`, the original single-drone wall-follow; `MAZE_DRONES == 4` reproduces the four corners. Single-use only (no reuse stacking). Throughput scales with drone count but **only if power keeps up** — under `FOCUS_CROP="Maze"` (energy floor disabled) 32 drones drain power to 0 and run at half speed, so 32 measured *slower* than 14; in production (`FOCUS_CROP=None`, energy floor maintains power) 32 ties/edges 14 (2026-06-19).
- **Sunflower** — `farm_sunflower()` fills the entire grid with sunflowers; Pass 1 scans for the max-petal cell, then harvests it first for the 8× power bonus (requires ≥10 sunflowers on the farm, i.e. world_size ≥ 4); Pass 2 harvests all remaining ready cells and replants
- **Bones** — `farm_bones()` wears `Hats.Dinosaur_Hat` and runs a snake (Hamiltonian boustrophedon, bottom row reserved as a return lane) eating apples (64 Cactus each) to grow a tail, then switches back to `Hats.Pumpkin_Hat` to cash out `tail_length²` `Items.Bone`. Single-drone, **even world size only**. Runs when **Bones** is the resource being farmed — i.e. an unlock's bottleneck (then it runs every loop, unthrottled, until that unlock is affordable), or the lowest stock once all unlocks are maxed (then throttled by `BONES_LOOP_INTERVAL`); always gated by a `MIN_CACTUS_FOR_BONES` buffer since apples cost Cactus. NOTE: cannot be exercised by the `simulate()` bench harness — `change_hat` errors in-sim — so bones is validated **live** (`bench_main` skips it)

### Items reference

| Item | Obtained from | Notes |
|---|---|---|
| `Items.Hay` | Harvesting grassland | Prerequisite for Wood/Carrot unlocks |
| `Items.Wood` | Harvesting bushes and trees | Diagonal checkerboard farming |
| `Items.Carrot` | Harvesting carrots | Prerequisite for Pumpkin unlocks |
| `Items.Pumpkin` | Harvesting pumpkins | Prerequisite for Cactus/Dinosaur unlocks |
| `Items.Cactus` | Harvesting sorted cacti | Phase state machine; prerequisite for Dinosaur unlock |
| `Items.Weird_Substance` | **Side-effect of `use_item(Items.Fertilizer)`** on any plant | Spent (not grown) — consumed by `farm_maze()` to enter a maze |
| `Items.Gold` | Maze treasure chest | `harvest()` at `Entities.Treasure`; gold = maze area; tracked in global `gold` and `get_amount()`; used by `MIN_GOLD_STOCK` logic |
| `Items.Fertilizer` | Trade (10 pumpkins each) | `use_item(Items.Fertilizer)` grows plant by 2s; each use also generates `Items.Weird_Substance` |
| `Items.Water` | — | `use_item(Items.Water)` waters soil before planting pumpkins |
| `Items.Power` | Harvesting sunflowers | Passive — doubles drone movement speed automatically; no `use_item()` call needed |
| `Items.Bones` | Dinosaurs (not yet implemented) | "The bones of an ancient creature" |

### Unlocks reference

`auto_unlocks()` buys any unlock whose full `get_cost()` is affordable, and `get_next_unlock()` reports the next one being worked toward (and its bottleneck resource) — both read the live `get_cost()`, so the payment-currency column below is informational only. Tier labels indicate gameplay tier, not necessarily the payment currency.

| Unlock | Paid with | What it enables |
|---|---|---|
| `Unlocks.Loops` | Hay | `while` loops; `True`/`False` |
| `Unlocks.Plant` | Hay | `plant()` function |
| `Unlocks.Hats` | Hay | `change_hat()` and hat bonuses |
| `Unlocks.Speed` | Hay | Drone speed upgrade (repeatable) |
| `Unlocks.Senses` | Hay | `get_pos_x/y()`, `num_items()`, `get_entity_type()`, `get_ground_type()` |
| `Unlocks.Grass` | Wood (Lvl 2+) | Hay yield multiplier: 100%→200%→400%+ |
| `Unlocks.Carrots` | Wood | `till()` + `plant(Entities.Carrot)` |
| `Unlocks.Fertilizer` | Wood | `trade(Items.Fertilizer)` + `use_item(Items.Fertilizer)` |
| `Unlocks.Watering` | Wood | Doubles water regen rate |
| `Unlocks.Variables` | Carrot | Variable assignment (`=`) |
| `Unlocks.Functions` | Carrot | `def` function definitions |
| `Unlocks.Import` | Carrot | `import` statement |
| `Unlocks.Lists` | Carrot | Lists and sets |
| `Unlocks.Sunflowers` | Carrot | `plant(Entities.Sunflower)` → passive `Items.Power` speed boost |
| `Unlocks.Trees` | Hay | `plant(Entities.Tree)` — 5 wood each |
| `Unlocks.Pumpkins` | Carrot | `plant(Entities.Pumpkin)` — initial cost 500 Wood + 200 Carrots |
| `Unlocks.Expand` | Pumpkin | Expands farm grid size |
| `Unlocks.Utilities` | Pumpkin | `min()`, `max()`, `abs()` |
| `Unlocks.Timing` | Pumpkin | `get_time()`, `get_tick_count()` |
| `Unlocks.Costs` | Pumpkin | `get_cost()` |
| `Unlocks.Dictionaries` | Pumpkin | Dict and set data structures |
| `Unlocks.Polyculture` | Pumpkin (Lvl 2: 10,000 Bones) | `get_companion()` — companion planting multiplier (base 5×, upgrades to 10×/20×/…) |
| `Unlocks.Auto_Unlock` | Pumpkin | `unlock()`, `get_cost()`, `num_unlocked()` |
| `Unlocks.Cactus` | Pumpkin | `plant(Entities.Cactus)`, `measure()`, `swap()` |
| `Unlocks.Dinosaurs` | Cactus | `Hats.Dinosaur_Hat` → Bones harvesting |
| `Unlocks.Mazes` | Cactus | Each level doubles maze treasure and `Items.Weird_Substance` cost |

**Wiki pages that are NOT `Unlocks.*` enum values** (tutorial concepts or removed features):
- Move, If, For, Operators — early built-in features, no corresponding enum
- Debug, Debug_2 — `print()`, `quick_print()`, breakpoints, `set_execution_speed()`
- Benchmark — redirects to Timing wiki page
- Multi_Trade — **removed from game**
- Leaderboard — competitive speed-run feature, not a purchasable unlock

### Scripting gotchas

**Grid traversal off-by-one** — `move()` does NOT wrap. Always guard the final step:
```python
for y in range(world_size):
    # ... work ...
    if y < world_size - 1:
        move(North)
```
Same applies to `move(East)` at the end of column loops. `farm_grid()` and `farm_cactus()` both implement these guards correctly.

**Cactus — phase state machine** — `farm_cactus()` advances a global `cactus_phase` (0–4):
- 0: Plant — column-by-column traversal, till to Soil, `plant(Entities.Cactus)`
- 1: Wait — advance only when all `can_harvest()`
- 2: Sort rows ascending — bubble sort each row West→East; smaller values bubble West; smallest ends at x=0
- 3: Sort columns ascending — bubble sort each column South→North; smallest ends at y=0
- 4: Harvest — `goto_sw()` to origin, single `harvest()` cascades through sorted field

Sort swap condition (ascending, smallest at SW origin): `if measure() > measure(East/North): swap(East/North)`.

`goto_sw()` navigates to origin (x=0, y=0) by moving South then West. Avoid nested `while` loops inside `farm_cactus()` — the game environment does not handle them reliably.

**No keyword arguments in function calls** — the game's Python parser rejects keyword arguments entirely. `sorted(list, reverse=True)` causes a parse error ("Expected comma or closing bracket") that prevents the whole script from starting. Use only positional arguments; replace any `sorted(..., reverse=True)` with a manual sort or a different approach. This applies to ALL function calls, not just `sorted()`.

**No ternary expressions** — `x = a if cond else b` causes a parse error ("A BRACKET_CLOSE is expected here") and silently prevents the script from starting. Use a plain `if`/`else` block instead.

**Wood — trees require Soil** — before `plant(Entities.Tree)` always check `if get_ground_type() != Grounds.Soil: till()`. Planting on Grassland fails silently.

**Pumpkin — second harvest sweep** — after the main grid traversal a second full sweep is needed to catch tiles that ripened while the drone worked other cells.

**Mega Farm — multi-drone parallelism** — `farm_grid(crop_choice, start_x, end_x)` wraps the per-cell loop. When `config.NUM_DRONES > 1`, the main loop distributes columns evenly across up to 32 drones: `base = world_size // num_drones` columns per drone, with the first `world_size % num_drones` drones getting one extra column. Spawned drones (0..N-2) handle the first N-1 slices; the main drone handles the final slice. Key constraints:
- `num_drones` is capped at `world_size` — no 0-column slices
- Each drone owns exclusive columns — no shared tiles, no race conditions
- `farm_grid()` calls `update_amounts()` at entry to sync the spawned drone's stale globals copy
- Maze parallelizes via a perimeter solve (`MAZE_DRONES`, default 32): solvers spread evenly around the field edge race the same maze, coordinating through live-shared `num_items(Items.Gold)` rather than globals (globals are *copied* per spawned drone, not shared). Cactus and Sunflower parallelize across drones via strip functions. Bones is single-drone.
- `spawn_drone()`, `wait_for()`, `has_finished()` are game-injected APIs (not defined in repo)
