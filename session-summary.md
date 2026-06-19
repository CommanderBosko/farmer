_Older entries are in [session-summary-archive.md](session-summary-archive.md)._

## Session: 2026-06-18 — Pumpkin/bones fixes, unlock-steering rework, skill toolkit

**Focus**: Fix pumpkin & bones farming, rebuild `plant_decision()` to steer toward unlocks, and capture the recurring workflows as skills.

### What changed (and why)
- **Pumpkin**: stopped the wait loop from re-planting *living* pumpkins (that resets growth → empty plots); fixed a stale `get_amount` fertilizer check (caused a warning flood + crawl) → live `num_items`; bounded the water loop. Probe-confirmed: `plant()` clears a dead pumpkin directly, and you must **never `till()`** one (it reverts Soil→Grassland and breaks planting).
- **Bones**: rewrote `farm_bones()` to target an apple count (`BONES_TARGET_TAIL`, default 900) instead of laps — counts apples via `measure()` on the safe Hamiltonian cycle and cashes out at *exactly* the target. Fixed a bot-killing bug: the snake path is origin-relative, but the main loop left the drone mid-field, so it tangled into its own tail and halted the whole program — fixed by `goto_sw()` first. Live-calibrated: bones ≈ **40×tail²** (Polyculture multiplier), tail ~2.7/lap, self-collision at tail ~1023, `move()` tick floor ~37.
- **Decision rework**: `auto_unlocks()` now buys ANY fully-affordable unlock (`can_afford`, multi-resource) — fixed the single-payment assumption that stranded Polyculture. `plant_decision()` now **steers to the next unlock's bottleneck resource** (any resource, via `get_next_unlock()`), farming only that with no throttle/balance until the unlock lands; lowest-stock balancing is the post-all-unlocks fallback. Removed the `MIN_WEIRD_SUBSTANCE_STOCK` auto-maze trigger; maze dispatches via `Items.Gold` (goal reads "Gold"). Goal line now shows `Current Goal: <crop> for Unlock: <unlock>` (or `Unlocks Complete!`).
- **Skills**: added 7 — `probe-sweep`, `output-watcher`, `ship-change`, `verify-mechanic`, `diagnose-behavior`, `unlock-status`, `live-verify` (last 5 built in parallel via subagents).

### Decisions
- Steer to the next unlock's needed resource, **not** lowest-stock, while unlocks remain (user's explicit model); balance only once everything is maxed.
- Bones target = apples not laps (deterministic yield); precise cash-out + 900 default keep clear of the ~1023 collision — **a snake death halts the entire bot**.
- Never `till()` a dead pumpkin; `plant()` clears it.

### Issues / surprises
- A snake death halts the **entire** program — both an origin offset and over-long runs caused it. Fixed via `goto_sw()`, precise stop, and a lap safety cap.
- **No `trade()` logic exists** — weird substance (→ gold via maze) only comes from spending the fertilizer stockpile (~1.54M). If it ever depletes, the gold path stalls (flagged for a future auto-trade).
- Many "bugs" were just the live bot running **un-restarted old code** — check that first.

### Next session
- Watch The_Farmers_Remains complete (bones → 100M) and the hand-off to Top_Hat steering (Wood).
- Optional: auto-trade fertilizer for self-sufficiency; companion planting (`get_companion`) for crop yield; pumpkin giant-merge take 2.

**Commits**: `e02aed5..7cdb1f4` (16 commits)

---

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

