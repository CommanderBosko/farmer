# Session Summary Archive — Farmer Bot

_Older sessions, most recent first. Active log: [session-summary.md](session-summary.md)._

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
