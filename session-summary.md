_Older entries are in [session-summary-archive.md](session-summary-archive.md)._

## Session: 2026-11-20 — DLC mining probes: coal/iron/mushroom/dynamite characterised, Dynamite bought, Bamboo probe staged

**Focus**: Resume the DLC "mining module" probe project (paused 2026-11-15) and measure every remaining resource so the blocked list can be agreed before any bot code is written.

### What changed (and why)
- **Only repo change: `257c70b`** — CLAUDE.md's "move() does NOT wrap" gotcha corrected (Probe F showed it wraps; surface behaviour unverified). `main.py`/`config.py` untouched on purpose (2026-11-13 decision: finish probing first). Everything else was throwaway `probe.py` runs; results, mechanics and the exact resume point are in the Claude memory notes (`reference_mining_mechanics`, `project_mining_module_status`), probes in `~/farmer-save-backups/`.
- **Coal/Iron:** Coal L2 re-measured at 0.77/s (n=7; the earlier 1.84 was a lucky 3-sample). Bought **Ore_Boost** (200 Coal/100 Iron/20 Quartz, single level): it doubles coal per dig (2.28/s) and makes iron veins ~×1.5 (1.81/s).
- **Mushrooms (5 probes):** the stratum exists in only ~30% of worlds, is 4–6 blocks thick, depth varies (z=-38…-72); a push that stacks two same-type blocks = +1 Mushroom and exposes the next layer. A "well" solver reached 1.24/s hunting-only but ~0.16/s overall. M3's 19% failed pushes were stale surveyed types — measuring each tile right before use gave 43/43 merges. `place(Grounds.Dirt)` works (1 Block). Gold turned out to be ~24.4M, so no maze step was needed.
- **Dynamite:** bought L1 (4,000 Gold + 80 Mushroom; next level 400 Mushroom). The docs page showed it's a **minesweeper** (soot `measure()` = live neighbours); a safe zero flood-fill cleared 188–300 tiles in 17–33 s at +1 per dud, 0 explosions; estimate ~10k Dynamite per fully solved board (squared live-block bonus).
- **Close-out tooling:** `session-closer` found no project `secret-scan` skill, so one was generated with `create-secret-scan` (no dedicated scheme, full-history scan on); it is the scan used for this close.
- **Bamboo:** wrote and mock-tested probe **B1** (one plant at L2, then one drone and 4/16 spawned drones on 16/8-plant lanes), synced into the game but **not run** — the user ended the day.

### Decisions
- **Explosive_Drill (120k Mushroom + 12M Dynamite) → blocked list**, user-approved: its Mushroom cost alone is >= 27–111 game-hours single-drone.
- **Parallelize surface Bamboo** over the existing 32-drone column split (Bamboo gates the most unlocks); underground work stays single-drone.
- Buy Dynamite then probe it; ask before buying the cheap levels (Mushrooms/Dynamite L2 yield effects untested).

### Issues / surprises
- The 1.84 coal/s figure and M3's survey-based types were both artifacts of small or stale samples; the output watcher's 150 s quiet fallback fired during a slow-real-time stretch (use >= 450 s); the user re-ran the loaded probe twice between steps (extra free data, but check output.txt before assuming a result is mine).
- One memory edit batch failed atomically on a wrong anchor (redone); a mock bug (z not changing during the pit) briefly looked like a probe bug.

### Next session
- Resume at probe B1 (steps in `project_mining_module_status` memory and `project-state.md` Next Steps), design the parallel Bamboo farm, optional Dynamite solver probe D2, then build DLC support in `main.py`.

**Commits**: `257c70b` (1 commit this session; the baseline range `21e262b..257c70b` also spans 3 earlier unclosed commits, e.g. the 2026-11-15 Save0 sync fix, not narrated here)

Secret-scan: clean (tree + 78 commits via the new project-local `secret-scan` skill; encrypted-secret pass skipped — no scheme; `.gitignore` is missing `.env`, `*.pem`, `*.key` — informational only).

---

## Session: 2026-06-19 (PM) — Parallel maze gold (MAZE_DRONES), 5 achievements, achievement-hunter skill

**Focus**: Make the slow gold/maze path multi-drone, then start unlocking game achievements.

### What changed (and why)
- **Parallel perimeter maze** (`farm_maze()`, `config.MAZE_DRONES`, default 32): replaced single-drone wall-following with `MAZE_DRONES` solvers spread evenly around the field edge — placed on open ground *before* the maze grows (walls block placement after), all racing the one maze; nearest-to-treasure wins and harvests, losers bail the instant `num_items(Gold)` jumps. `=1` single-drone fallback, `=4` = old four corners. Measured ~2× (4 drones) → ~4.7× (14) faster gold/sec.
- **Verified the multi-drone mechanics live first** (4 probe rounds → `drone_mechanics` memory): spawned drones start on the parent's tile; globals are COPIED per drone (coordinate via world state, not globals); drones don't block each other; walls are `Entities.Hedge`; `num_items()` is a live shared inventory across drones (the loser-bail signal).
- **5 achievements unlocked** via throwaway `probe.py` scripts: 5 hats on drones, stack overflow, healer (infect+cure with Weird_Substance), circular import (two scratch files importing each other), wrong-order cacti (full field sorted descending, 32-drone parallel).
- **Skills**: built `achievement-hunter`; hardened `throughput-ab` + `output-watcher` with the power-confound and stale-variant (BOOT-marker) gotchas.

### Decisions
- Default `MAZE_DRONES=32` — the "32 slower than 14" result was a **power confound**: `FOCUS_CROP="Maze"` disables the energy floor, so 32 drones drained Power to 0 and ran at half speed. In production (`FOCUS_CROP=None`, floor active) 32 ties/edges 14. Benchmark drone-count scaling only with power maintained.
- Achievement code stays in gitignored scratch (no commit); the user-confirmed popup is the real success signal, not the script's sentinel.

### Issues / surprises
- The "32 slower" false result — caught by the user (energy ran out mid-test). → `throughput-ab` gotcha.
- Stale-variant contamination: the watcher fired on leftover 14-drone MEASURE lines (bot keeps writing across a config change that only reloads on restart). Fixed with a per-run `BOOT MAZE_DRONES=N` marker, count samples after it. → `output-watcher` gotcha.

### Next session
- Watch **Top_Hat** (the final upgrade) unlock — Gold is the bottleneck and the maze path is now faster.
- Keep hunting achievements (`achievement-hunter`) + look at Leaderboards; add `trade(Items.Fertilizer)` auto-trade.

**Commits**: `9ee5068..120e619` (4 commits, + this session close)

---

## Session: 2026-06-19 — Polyculture companion farming: built, measured ~19x slower, shelved

**Focus**: Implement Polyculture/`get_companion()` companion farming for crop yield, then decide whether it actually beats 32-drone monoculture.

### What changed (and why)
- **Verified `get_companion()` live** (probes): returns `(type,(x,y))` or `None`; coords are ABSOLUTE and WRAP at grid edges; preference is known at plant time and STABLE per plant; only Grass/Bush/Tree/Carrot participate (Cactus/Pumpkin/Sunflower -> None); bonus ×160 now (5×2^level), applied if the companion exists at harvest. Saved to `companion_mechanic` memory.
- **Built companion farming in 3 stages** (all default OFF, gated by `config.COMPANION_*`): `farm_companion()` (Stage 1 triplet, single-crop), `farm_companion_chain()` (Stage 2 chain-random, mixed Hay+Wood+Carrot), and auto-routing in the crop dispatch (`COMPANION_AUTO` + cost-driven triplet-vs-chain). Helpers: `goto_xy()` (wrap-aware), `place()`, `cmove()`.
- **Measured it — and it LOST.** Timed live A/B on Wood, same `get_time()` clock: 32-drone monoculture ~4.47M wood/sec vs single-drone chain ~0.24M wood/sec -> **monoculture ~19x faster**. Reverted `COMPANION_AUTO=False`; bot stays on monoculture. Companion code kept (off) for the verified mechanic / a future multi-drone rebuild.
- **Skills**: added `throughput-ab` (measure resources/sec to A/B strategies); hardened `output-watcher` (freshness-gate every break condition) and `game-probe` (standalone probes; clear occupied tiles before planting).

### Decisions
- Single-drone companion can't beat 32-drone parallelism at ×160 (multiplier ~2.8x/drone vs 32x parallel) — SHELVED, not deleted.
- Decide strategy by MEASURED throughput, not per-move analysis — the "2.7x faster" claim was wrong because it ignored parallelism.

### Issues / surprises
- Initial throughput analysis over-claimed companion (twice); only the timed A/B settled it. -> `throughput-ab` skill.
- Watcher false-fired on STALE `output.txt` twice (a leftover error, a leftover marker) — freshness-gate on mtime. -> `output-watcher` gotcha.
- Probe bugs cost iterations: probes can't call main.py helpers; `plant()` silently no-ops on an occupied tile. -> `game-probe` gotchas.

### Next session
- **Restart `main.py`** to drop the live bot back to monoculture (pending).
- Confirm Top_Hat's remaining bottleneck (Cactus then Gold) and grind it; add `trade(Items.Fertilizer)` auto-trade (Gold is now load-bearing).

**Commits**: `239bfb7..0c94962` (7 commits)

---

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

