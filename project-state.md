# Project State — Farmer Bot

Last updated: 2026-06-13

---

## Current Project State

The bot starts cleanly and runs the full crop progression without warnings. All
primary farming strategies (Hay, Wood, Carrot, Pumpkin, Cactus, Maze, Sunflower)
are implemented and all of them except Maze now parallelize across up to 32 drones.
The prerequisite chain (Hay → Wood → Carrot → Pumpkin → Cactus → Weird_Substance)
is enforced correctly. MIN_PREREQ_STOCK is set to 500 000 to keep buffers healthy
at 32-drone accumulation rates.

**What works:**
- Full crop cycle: Hay → Wood → Carrot → Pumpkin → Cactus → Maze
- Multi-prerequisites per crop (PREREQUISITES dict is a list of tuples)
- Sunflower farming parallelized across N drones via farm_sunflower_strip()
- Cactus farming parallelized across N drones via strip helper functions
- Maze farming with threshold trigger and wall-following safety valve (single-drone)
- Gold tracking and MIN_GOLD_STOCK grinding mode
- Multi-drone column splitting for Hay/Wood/Carrot/Pumpkin (NUM_DRONES, default 32)
- Planting guards on all plant() calls (no occupied-tile spam)
- Crop transition clearing: foreign entities harvested and tilled before replanting
- till() toggle guard: Soil/Grassland ground type re-checked after every clearing till
- Configurable pre-plant watering (MIN_WATER_LEVEL) for carrot, wood, and sunflower branches
- Broken-pumpkin recovery in the pumpkin wait loop
- Auto-unlock purchasing and ordered unlock goal detection

**What is in progress / partially done:**
- Dinosaur farming: not yet implemented (Bones item documented but no farm_dinosaur()).
- Pumpkin reliability: the original per-tile pumpkin logic (water → plant → flip → wait → harvest) leaves dead pumpkins on the grid. A full mega-pumpkin rework was attempted on 2026-06-13 but reverted (see below); `main` is back on the original logic.

**What is broken / known issues:**
- Pumpkin farming leaves dead pumpkins behind and does not reliably form mega-pumpkins. Not blocking the unlock chain (it still produces some pumpkins), but inefficient. See Known Issues.

---

## Current Goals

### Short-term (next 1–3 sessions)
1. Recover the sunflower 8x petal bonus using a keyword-argument-free sort (manual selection-sort over a list) — strip parallelism is now in place so this optimization can be layered on top.
2. End-to-end test the prerequisite chain from a fresh game state at 32-drone speed.
3. Implement Dinosaur Hat / Bones farming once Cactus prerequisites are confirmed stable.

### Long-term
- Full automation through all game tiers including Polyculture companion planting.
- Investigate Leaderboard / Simulation unlocks once gold is farmed.

---

## Recent Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2026-05-28 | No keyword arguments anywhere in main.py | Game parser rejects `func(key=value)` — causes silent script-load failure |
| 2026-05-28 | PREREQUISITES values are lists of tuples | Allows multiple prerequisites per crop without control-flow changes |
| 2026-05-28 | MIN_POWER_STOCK = 5 000 | 50 000 caused excessive sunflower detours; 5 000 is sufficient |
| 2026-05-28 | farm_sunflower() uses snake traversal only | Removed sorted(reverse=True) to comply with keyword-arg restriction |
| 2026-05-31 | farm_sunflower() parallelized via farm_sunflower_strip() | Same column-slice pattern as cactus strips; dispatches N drones with spawn_drone/wait_for |
| 2026-05-31 | MIN_PREREQ_STOCK raised to 500 000 | At 32-drone throughput the bot accumulates prerequisites much faster; larger buffer keeps tier advancement stable |
| 2026-05-31 | Maze is the only remaining single-drone strategy | Maze requires sequential wall-following; all other crops (including Sunflower) now parallelize |
| 2026-06-01 | Clearing pattern: can_harvest() + till() + ground-recheck | Handles both occupied-entity clearing and the till() toggle edge case (Soil→Grassland) in a single, consistent pattern |
| 2026-06-01 | MIN_WATER_LEVEL = 0.5; pumpkin branch untouched | Pumpkin already waters to 1.0 unconditionally; applying MIN_WATER_LEVEL would be a regression. Other soil crops benefit from light pre-plant moisture. |
| 2026-06-13 | Reverted all pumpkin rework; `main` back at d585c32 | A day of pumpkin experiments (sweep-based → dead-pumpkin handling → mega-pumpkin convergence → multi-drone strips) all behaved worse in-game than the original. Reset `main` to start-of-day; work preserved on branch `backup/pumpkin-wip-2026-06-13`. |
| 2026-06-13 | Documented the real pumpkin mechanic (from wiki/community) | ~20% of pumpkins die the instant they finish growing; a square only merges into a giant when EVERY tile is fully grown AND alive simultaneously; `plant(Entities.Pumpkin)` auto-replaces a dead/ungrown pumpkin; planting pumpkins costs Carrots. |

---

## Known Issues / Tech Debt

- **Sunflower 8x bonus lost** — `sorted(harvestable, reverse=True)` was the mechanism; removed because `reverse=True` is a keyword argument. A manual selection-sort would restore the behavior without violating the parser constraint. The strip parallelism is now in place as a foundation.
- **No Dinosaur farming** — `Unlocks.Dinosaurs` is purchased via auto_unlocks() but `farm_dinosaur()` does not exist. The bot has no strategy for harvesting Bones.
- **Pumpkin leaves dead pumpkins / no mega-pumpkin** — the original logic plants/harvests pumpkins per-tile and does not handle the ~20% that die at maturity well, nor does it aim for the giant-pumpkin area bonus. The 2026-06-13 rework attempts (preserved on `backup/pumpkin-wip-2026-06-13`) failed in-game for reasons not fully diagnosed — likely a combination of: (a) pumpkin/carrot share the same grid, so when carrots dip below `MIN_PREREQ_STOCK` mid-grow the bot switches to carrots and **plows the in-progress pumpkin field** (restart-forever thrash); (b) convergence timing vs. growth was never validated live. Next attempt should isolate one variable at a time and watch a single field in-game.
- **Pumpkin split-grid timing** — with N drones farming independent columns, the second pumpkin harvest sweep runs sequentially after all drones finish. This is correct but could miss pumpkins that ripen during the inter-drone delay on large grids.
- **No class/OOP** — the game environment forbids Python classes. All state is module-level globals. This is a hard constraint, not debt.
- **MIN_WATER_LEVEL not validated end-to-end** — the watering logic is in place but has not been observed running in a live session with a depleted water level across all affected branches.

---

## Next Steps

1. **Pumpkin, take 2 (smaller, validated):** decide first whether to (a) just make the *original* per-tile logic clear dead pumpkins reliably (modest, low-risk), or (b) retry the mega-pumpkin only after solving the carrot/grid plow-thrash (e.g. don't let `plant_decision()` switch off pumpkin mid-field, or dedicate a separate region). Change ONE thing, watch one field in-game before iterating. Reference: `backup/pumpkin-wip-2026-06-13`.
2. Implement selection-sort inside `farm_sunflower_strip()` to restore max-petal-first harvesting without keyword arguments (foundation is now in place).
3. Run the bot from a fresh game save — verify the full prerequisite chain at 32-drone throughput and observe crop transitions in action.
4. Add `farm_dinosaur()` stub and wire it into `plant_decision()` once Cactus farming is confirmed stable at scale (the day's original goal: Dinosaurs/Bones gate Polyculture Lvl 2).
5. Consider adding a `MIN_BONES_STOCK` config knob in preparation for Polyculture (needs Bones for Polyculture Lvl 2).
