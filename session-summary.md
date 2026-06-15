## Session: 2026-06-14 — simulate() harness, carrot-drain fix, and bone farming (project blocker cleared)

**Duration Estimate**: Long, multi-arc session
**Session Focus**: Implement the new `simulate()` function as a benchmark harness, then use it to find/fix a starvation bug, then implement Dinosaur/Bones farming — clearing the long-standing Polyculture Lvl 2 blocker.

### What Was Accomplished
- **Built a `simulate()` no-starvation bench harness.** `gen_bench_main.py` generates `bench_main` (a terminating twin of `main`, strategy single-source); `bench.py` runs it via `simulate()`; results read off `output.txt`. Reports per-resource init/min/final + PASS/FAIL.
- **Reverse-engineered the simulate() sandbox** via in-game probes: `globals` injection works only for *undeclared* names and is *not* read back (dict not mutated); `quick_print` inside a sim DOES reach `output.txt` (the readback channel); hats and `get_op_count`/`get_time` error in-sim; `Items.Bone` not `Items.Bones`.
- **Discovered the repo↔game file sync**: `Save0/main.py` & `config.py` are symlinks to the repo; new files need a Save0 symlink + save reload to register. (Two subagents nailed this down.)
- **Found and fixed a carrot-drain bug** the harness reproduced cold: pumpkin planting costs 256 Carrot, and the bot drained the carrot buffer to 0 chasing pumpkin-cost upgrades (oscillating 0↔600k). Fix: a `MIN_CARROT_FOR_PUMPKIN` reserve. Re-benched: carrot floors at the reserve.
- **Implemented Bones farming** (`farm_bones()`): dinosaur-hat snake (Hamiltonian boustrophedon, reserved bottom row) eating apples (64 Cactus each) → `tail_length²` Bones. Live-validated at ~16.9k bones / 8 laps. Wired as a throttled lowest-stock branch; `bones` is now a tracked global. **User confirmed it farms live and bought Polyculture Lvl 2** — the project blocker is cleared.
- **Moved farm skills to project scope** and added two: `/bench` (run the harness) and `/game-probe` (the in-game diagnostic loop); upgraded `/bench` after bones made its guidance stale.

### Files Changed
- `gen_bench_main.py`, `bench.py` — new bench harness (generator + runner).
- `docs/simulate-brief.md` — confirmed scoping brief for the harness.
- `main.py` — `MIN_CARROT_FOR_PUMPKIN` guards; `farm_bones()`; bones as tracked resource (globals, `update_amounts`, `get_amount`, `plant_decision` throttled branch, dispatch).
- `config.py` — `MIN_CARROT_FOR_PUMPKIN`, `MIN_CACTUS_FOR_BONES`, `BONES_LOOP_INTERVAL`, `BONES_LAPS`.
- `CLAUDE.md` — bones strategy + config knobs documented.
- `.claude/skills/` — `bench`, `game-probe` added (+ `config-set`/`farm-status`/`syntax-check` moved to project scope).
- `.gitignore` — ignore generated `bench_main.py` and throwaway probe scratch files.

### Commits This Session
- `8703065` — Add simulate() no-starvation harness + carrot-reserve fix
- `1f8edd4` — Add bone farming (dinosaur snake) as a tracked resource
- `4a25cf2` — Add game-probe skill
- `8487313` — Update bench skill: bones is live-validated, not bench-testable

### Decisions Made
- Generated twin (not a refactor/import) keeps the bench's strategy single-source while letting it terminate.
- Bones is validated **live** and excluded from the bench (hats error in-sim); `bench_main` skips it.
- Bones runs single-drone, even world size only, throttled (one dino hat; long blocking run; cycle closes only on even sizes).

### Issues Encountered
- New files don't appear in-game until symlinked into Save0 + save reloaded (big detour, now solved).
- The bench sim is hatless and lacks `get_op_count`/`get_time` — budget loops with a plain counter; bones can't be sim-tested.
- The web wiki was wrong (apples cost Cactus, not pumpkins); the in-game `get_cost` probe was authoritative.

### Remaining / Next Session
- **Companion planting** (`get_companion()`) for the Polyculture multiplier — biggest open win.
- Observe the live bones trigger end-to-end; tune `BONES_LAPS` / `BONES_LOOP_INTERVAL`.
- Pumpkin mega-pumpkin reliability, take 2.

---

## Session: 2026-06-13 — Pumpkin rework explored and reverted (net: no main change)

**Duration Estimate**: Single session, exploratory
**Session Focus**: Started toward Dinosaurs/Bones, pivoted to fixing pumpkin farming after observing it ran out of carrots and left dead pumpkins; attempted a full mega-pumpkin rework, then reverted everything to start-of-day after it behaved worse in-game.

### What Was Accomplished
- Diagnosed the carrot-shortage-during-pumpkin-planting bug and shipped a guard (`MIN_CARROT_FOR_PUMPKIN`) — later reverted with everything else.
- Researched and documented the **real pumpkin mechanic** (wiki + community): ~20% of pumpkins die the instant they finish growing; a square only merges into a giant when EVERY tile is fully grown AND alive simultaneously; `plant(Entities.Pumpkin)` auto-replaces a dead/ungrown pumpkin (no harvest/till first); planting pumpkins costs Carrots; `Entities.Dead_Pumpkin` is the dead-tile entity.
- Iterated through four pumpkin designs (sweep-based non-blocking → dead-pumpkin replant loop → mega-pumpkin field convergence → multi-drone strips). Each was tested in-game and rejected.
- Identified the likely root failure of the rework: **pumpkin and carrot share the grid**, so when carrots dip below `MIN_PREREQ_STOCK` mid-grow, `plant_decision()` switches to carrots and plows the in-progress pumpkin field — restart-forever thrash.
- **Reverted `main` to start-of-day (`d585c32`)** at the user's request ("that was closer than we are now"). Preserved the full day's work on branch `backup/pumpkin-wip-2026-06-13`.

### Files Changed
- **None on `main`** — `main` was reset to `d585c32`; working tree clean. (This commit only touches the session docs.)
- Backup branch `backup/pumpkin-wip-2026-06-13` holds the reverted experiments (main.py, config.py, CLAUDE.md) for reference/recovery.

### Commits This Session
- `7475cb3` — Guard pumpkin planting against carrot shortage (committed, then reverted off `main`; lives on backup branch)
- `920414a` — WIP backup: pumpkin mega-pumpkin + multi-drone experiments (backup branch only)

### Decisions Made
- **Reverted rather than kept iterating** — four pumpkin designs each performed worse in-game than the original per-tile logic; the original is the better baseline to build on next time.
- **Preserved work on a branch instead of discarding** — the mechanic research and the convergence/multi-drone code are worth keeping for a future, smaller attempt.

### Issues Encountered
- Repeated in-game regressions from each pumpkin redesign (carrot drain → dead pumpkins left behind → field never converging / "1 drone, 1 column, keeps restarting").
- Could not validate any change against the live game from the dev environment — every iteration depended on the user observing behavior, which lengthened the loop.

### Remaining / Next Session
- Decide pumpkin direction: minimal dead-pumpkin fix on the original logic vs. a properly-isolated mega-pumpkin retry that first solves the carrot/grid plow-thrash. Change one variable, watch one field.
- Then resume the original goal: implement `farm_dinosaur()` / Bones farming (gates Polyculture Lvl 2).

---

## Session: 2026-06-01 — Crop transition clearing and MIN_WATER_LEVEL watering

**Duration Estimate**: Single session (one commit batch)
**Session Focus**: Harden crop transitions by clearing foreign entities before planting, fix a `till()` toggle bug that was producing Grassland instead of Soil, and add configurable pre-plant watering to all soil-based crop branches.

### What Was Accomplished

- Added harvest-if-ready + till + Soil-recheck pattern before every `plant()` call in the entity-clearing path — ensures any foreign crop occupying a cell is cleared before the new entity is planted.
- Fixed the `till()` toggle bug: `till()` alternates between Soil and Grassland. An unconditional `till()` after a clearing step was bouncing a Soil cell back to Grassland. Added `if get_ground_type() != Grounds.Soil: till()` after the clearing till in every affected branch.
- Applied the entity-clearing fix uniformly to: carrot branch, wood-tree diagonal, wood-carrot fill, pumpkin branch, and both passes of `farm_sunflower_strip()`.
- Added `MIN_WATER_LEVEL = 0.5` to `config.py` — a new tunable threshold for pre-plant watering.
- Added watering logic to carrot, wood-tree, wood-carrot-fill, and both `farm_sunflower_strip()` passes: after ensuring Soil, if `get_water() < config.MIN_WATER_LEVEL` and `Items.Water` is in inventory, call `use_item(Items.Water)`. Pumpkin's existing full-water-to-1.0 loop is left unchanged.

### Files Changed

- `main.py` — entity-clearing and water-check logic added to carrot, wood, pumpkin, and sunflower-strip branches.
- `config.py` — added `MIN_WATER_LEVEL = 0.5` with explanatory comment.

### Commits This Session

- `fcb1269` — Fix crop transition clearing and add MIN_WATER_LEVEL watering for soil-based crops

### Decisions Made

- **Clearing pattern is harvest-if-ready + till + ground-recheck** — using `can_harvest()` before the clearing `till()` avoids discarding a harvestable yield; the ground-recheck after the clearing till handles the toggle edge case without assuming the cell's prior state.
- **Pumpkin's water logic is untouched** — pumpkin requires a full 1.0 water level and already has a dedicated `while get_water() < 1: use_item(Items.Water)` loop; applying `MIN_WATER_LEVEL` to it would be a regression.
- **MIN_WATER_LEVEL = 0.5 default** — a moderate default that waters about half-dry cells without burning water inventory on cells that are already reasonably moist.

### Issues Encountered

- The `till()` toggle was a subtle interaction: the first `till()` converts Grassland→Soil in preparation for planting, but a second unconditional `till()` (the entity-clearing step) could flip it back. The fix is to guard every `till()` with a ground type check.

### Remaining / Next Session

- Implement selection-sort inside `farm_sunflower_strip()` to restore max-petal-first harvesting without keyword arguments.
- Run the bot from a fresh game save to verify the full prerequisite chain and the crop transition clearing in action.
- Add `farm_dinosaur()` and wire it into `plant_decision()` once Cactus farming is confirmed stable at scale.
- Consider whether `MIN_WATER_LEVEL` should also apply to a future Dinosaur/Bones crop branch.

---

## Session: 2026-05-31 — Sunflower parallelization, MIN_PREREQ_STOCK bump, doc cleanup

**Duration Estimate**: Short session (inferred from three tightly related commits)
**Session Focus**: Extend the 32-drone parallelism pattern to Sunflower farming, raise the prerequisite safety buffer to match 32-drone throughput, and correct stale comments that misidentified Sunflower and Cactus as single-drone.

### What Was Accomplished

- Added `farm_sunflower_strip(start_x, end_x)` — a column-slice variant of the sunflower traversal using the same odd/even column logic as the original `farm_sunflower()`, but operating only over its assigned column range.
- Rewrote `farm_sunflower()` as a dispatcher: computes per-drone column widths (same base + remainder logic as `farm_grid()`), spawns N-1 drones each calling `farm_sunflower_strip`, runs the final slice inline, then `wait_for()` all spawned drones.
- Raised `MIN_PREREQ_STOCK` from 200 000 to 500 000 in `config.py` — 32 drones accumulate prerequisites fast enough that the smaller buffer was too thin to prevent premature tier advancement.
- Corrected the CLAUDE.md Multi-drone section: the bullet that listed "Cactus, Maze, and Sunflower remain single-drone" now accurately states only Maze is single-drone.
- Corrected the `config.py` NUM_DRONES comment with the same fix.

### Files Changed

- `main.py` — added `farm_sunflower_strip(start_x, end_x)`; refactored `farm_sunflower()` as N-drone dispatcher.
- `config.py` — `MIN_PREREQ_STOCK` 200 000 → 500 000; corrected NUM_DRONES comment.
- `CLAUDE.md` — updated multi-drone bullet: Maze is the only remaining single-drone strategy.

### Commits This Session

- `612b43d` — Parallelize all cactus farming phases across 32 drones *(carried from prior session, pushed today)*
- `c6e03bd` — Double MIN_PREREQ_STOCK to 200000
- `8bacd9d` — Scale to 32 drones now that Megafarm is maxed out
- `5cef53d` — Parallelize sunflower farming across 32 drones; raise MIN_PREREQ_STOCK to 500000; fix stale single-drone comments

### Decisions Made

- **farm_sunflower_strip() mirrors farm_cactus strip pattern** — keeping the same column-slice and spawn/wait structure across all parallelized crops makes it easy to add future strips or adjust NUM_DRONES without touching control flow.
- **MIN_PREREQ_STOCK = 500 000** — at 32-drone throughput the bot fills lower-tier inventory faster; a larger buffer keeps the crop ladder stable without over-farming prerequisites.
- **Maze stays single-drone** — wall-following is inherently sequential and there is no natural column split for a maze. Confirmed as the only remaining single-drone strategy.

### Issues Encountered

- None. The strip pattern was already established by cactus parallelization; applying it to sunflowers was straightforward.

### Remaining / Next Session

- Implement selection-sort inside `farm_sunflower_strip()` to restore max-petal-first harvesting (the 8x petal bonus) without using keyword arguments.
- Run the bot from a fresh game save to verify the full prerequisite chain at 32-drone throughput.
- Add `farm_dinosaur()` and wire it into `plant_decision()` once cactus farming is confirmed stable at scale.

---

## Session: 2026-05-28 — Bug-fix blitz: bot-won't-start, planting guards, prereq chain

**Duration Estimate**: ~11 hours (14:45 – 22:27 EDT, inferred from commit timestamps)
**Session Focus**: Diagnose and fix a silent parse error preventing the bot from loading, then audit and harden planting logic and the prerequisite chain.

### What Was Accomplished

- Diagnosed and fixed the root cause of the "bot won't start" bug: `sorted(harvestable, reverse=True)` in `farm_sunflower()` — the game's Python parser rejects all keyword arguments in function calls, causing a silent script-load failure.
- Rewrote `farm_sunflower()` as a simple single-pass snake traversal eliminating all `sorted()` / keyword-arg usage, restoring bot startup reliability.
- Added `get_entity_type()` pre-checks before every `plant()` call in Carrot, Wood (trees and carrot fill-in), and Pumpkin branches, eliminating "Didn't have required items to plant" spam on occupied tiles.
- Added `till()` guard before `plant(Entities.Tree)` in the Wood branch (documented in CLAUDE.md scripting gotchas).
- Restored `harvest()` + `plant(Entities.Pumpkin)` inside the pumpkin wait loop — these were mistakenly removed in a prior cleanup; they are the recovery path for pumpkins that fail to plant or break.
- Fixed the prerequisite chain: `PREREQUISITES` dict values changed from single tuples to lists of tuples, allowing multiple prerequisites per crop. `check_stock()` updated to loop through all prerequisites.
- Fixed Carrot prerequisites specifically: now requires both Hay >= MIN_PREREQ_STOCK AND Wood >= MIN_PREREQ_STOCK (previously only Hay, causing premature carrot planting with zero wood stock).
- Completed the full prerequisite chain: Hay → Wood → Carrot → Pumpkin → Cactus → Weird_Substance.
- Added `Items.Cactus: [(Items.Pumpkin, config.MIN_PREREQ_STOCK)]` to PREREQUISITES.
- Lowered `MIN_POWER_STOCK` from 50 000 to 5 000 to reduce sunflower detour frequency.
- Documented the game's keyword-argument restriction in CLAUDE.md Scripting gotchas.

Earlier in the session (same day, carried into this summary for completeness):

- Added sunflower farming (`farm_sunflower()`) with 8x power-bonus harvesting.
- Added maze farming trigger: threshold-based (`MIN_WEIRD_SUBSTANCE_STOCK`) instead of lowest-stock, with wall-following safety valve (`world_size² × 4` steps).
- Added gold tracking and `MIN_GOLD_STOCK` config knob for manual gold-cost upgrade grinding.
- Fixed `plant_decision()` priority order: power → gold target → unlock goals → opportunistic maze → fallback.
- Added Mega Farm multi-drone support (`farm_grid()` with column splitting, `USE_MULTIPLE_DRONES` config knob).
- Fixed `get_next_unlock_goal()` min-cost sentinel bug that was silently ignoring repeatable upgrades.
- Fixed Wood farming: snake traversal (alternating column direction) and removed rogue `clear()` that was destroying freshly planted trees.
- Fixed sunflower 8x bonus logic (prior pass-2 approach lost the bonus on all but the first harvest).
- Documented all game Items, all 26 Unlocks.* enum values, and maze/cactus crop strategies in CLAUDE.md.

### Files Changed

- `main.py` — primary logic file; all farming, planting guard, prerequisite, sunflower, maze, and multi-drone changes.
- `config.py` — added `MIN_POWER_STOCK`, `MIN_WEIRD_SUBSTANCE_STOCK`, `MIN_GOLD_STOCK`, `USE_MULTIPLE_DRONES`; lowered `MIN_POWER_STOCK` to 5 000.
- `CLAUDE.md` — added Items reference table, full Unlocks reference, keyword-argument scripting gotcha, maze/cactus strategy docs, multi-drone architecture notes.

### Commits This Session

- `233cf10` — Support multiple prerequisites per crop; Carrot requires both Hay and Wood
- `fa285e7` — Fix prerequisite chain: Carrot requires Wood, not Hay
- `b504710` — Lower MIN_POWER_STOCK from 50000 to 5000
- `88eaca9` — Restore broken-pumpkin recovery in pumpkin wait loop
- `a64a187` — Document game Python parser restriction: no keyword arguments
- `b07ba27` — Fix farm_sunflower: remove sorted() with keyword arg (parse error)
- `4d520b5` — Fix planting guards and complete prerequisite chain
- `3505e93` — Fix sunflower farming to trigger 8x power bonus on every harvest
- `419f34f` — Fix Wood farming: snake traversal and remove farm-clearing position reset
- `7c8044f` — Add Mega Farm multi-drone support and fix late-game unlock goal detection
- `86dd78d` — Correct plant_decision() priority: gold target before unlock goals
- `ee0e53f` — Track gold and add MIN_GOLD_STOCK target for manual upgrade grinding
- `c129ae2` — Fix maze farming trigger and add safety valve to wall-following
- `42cfcde` — Add sunflower farming to maintain power stock for 2x speed boost
- `0529206` — Add full unlocks reference to docs; fix Mazes and Expand tier bugs
- `78a2332` — Document all game items and fix stale CLAUDE.md entries
- `9d375d7` — Revert main.py to working state; fix CLAUDE.md cactus sort docs

### Decisions Made

- **Keyword arguments are banned** — the game's Python parser rejects any `func(..., key=value)` call. This is now documented in CLAUDE.md and must be respected in all future edits to `main.py`.
- **`farm_sunflower()` simplified** — the 8x petal-bonus optimization using `sorted()` was removed because `sorted(..., reverse=True)` requires a keyword argument. The simpler snake traversal is reliable; the power bonus is still obtained on each harvest because the replanted seedling always has the lowest petal count.
- **Multiple prerequisites per crop** — changing PREREQUISITES values to lists of tuples is a clean data-structure decision. It avoids any control-flow changes when a future crop needs more than two prerequisites.
- **MIN_POWER_STOCK = 5 000** — 50 000 was overly conservative and caused excessive sunflower detours. 5 000 is sufficient to keep speed doubled during normal farming.

### Issues Encountered

- The game's keyword-argument restriction is not documented anywhere in the game itself; it was discovered by process of elimination after the bot silently refused to start.
- The pumpkin broken-pumpkin recovery was removed by mistake in a prior session cleanup and had to be restored — this is a non-obvious API pattern (empty-cell `harvest()` + `plant()` as a recovery mechanism).

### Remaining / Next Session

- Re-evaluate whether the sunflower 8x bonus pass can be recovered without keyword arguments (e.g., a manual selection-sort over a pre-built list rather than `sorted()`).
- Test the full prerequisite chain end-to-end from a fresh game start.
- Consider adding Dinosaur Hat / Bones farming once the Cactus prerequisites are stable.
- Evaluate whether `USE_MULTIPLE_DRONES = True` causes any issues with the current Pumpkin farming strategy (the second harvest sweep timing with a split grid).

---
