# Project State — Farmer Bot

Last updated: 2026-11-20

---

## Current Project State

The bot is an **unlock-driven, set-and-forget** agent: it pours all effort into whatever
the next upgrade needs, and only balances resources once the tech tree is fully maxed. It
runs **32-drone monoculture** — the fast path. As of the 2026-06-19 session it was steering toward **Top_Hat** (live bottleneck Gold); the DLC memory notes record the base tree as fully maxed by 2026-11-12 (Top_Hat itself was not re-verified, and Gold now stands at ~24.4M). Polyculture keeps auto-leveling (now ×160).

**DLC "mining module" — the active project (2026-11-12 → 2026-11-20; `main.py` / `config.py` UNTOUCHED by design).** Goal: extend the bot so `FOCUS_CROP=None` clears every *automatable* "Miner Was Replaced" DLC unlock unattended (brief approved via /interview + brief-reviewer; standing decision 2026-11-13: finish probing every resource before writing any bot code). All work so far is throwaway `probe.py` scripts (backups in `~/farmer-save-backups/`); verified mechanics and numbers live in the Claude memory notes `reference_mining_mechanics` and `project_mining_module_status`. Measured single-drone rates (game-seconds): **Coal 2.28/s** (Ore_Boost doubles coal per dig; 0.77/s without — the earlier 1.84 was a lucky 3-sample), **Iron 1.81/s** (Ore_Boost makes veins ~×1.5), **Quartz ~0.16/s**, **Rice ~10.8/s** (8 per clay tile at Rice L4), **Mushroom** +1 per same-type merge: 1.24/s hunting only, ~0.27/s with tile uncovering, ~0.16/s including the world search (stratum exists in only ~30% of worlds, 4–6 layers, depth varies z=-38…-72), **Dynamite** = a minesweeper puzzle (+1 per dud, a safe zero flood-fill clears ~190–300 tiles in ~17–33 s; est. ~10k per fully solved board), **Bamboo** L1 ~103 per plant (L2 and multi-drone not yet measured). Unlocks bought this stretch: Ore_Boost (single level) and Dynamite L1 (next level 400 Mushroom); Mushrooms L2 (600 Gold) and the cheap levels are deliberately not bought yet. **Blocked list (user-approved 2026-11-20): Explosive_Drill** (120,000 Mushroom + 12,000,000 Dynamite). Stock: Coal 823, Iron 132, Quartz 5, Block 5002, Mushroom 5, Gold ~24.4M, Rice 627, Bamboo 112, Dynamite 488. **Paused with probe B1 (multi-drone surface Bamboo + Bamboo L2) written, mock-tested and synced into the game but NOT run** — exact resume steps are in the memory note `project_mining_module_status`.

**Previous session (2026-06-19)** parallelized the slow gold/maze path and started knocking out **game
achievements** (Achievements/Leaderboards are the new post-tree goal). Gold farming went
from a single drone wall-following one maze to **`MAZE_DRONES` solvers spread around the
field perimeter** racing the same maze — measured ~2× (4 drones) up to ~4.7× (14 drones)
faster, default now **32**. Five achievements were unlocked via throwaway `probe.py`
scripts (5 hats on drones, stack overflow, healer, circular import, wrong-order cacti) and
captured as the new `achievement-hunter` skill.

**What works:**
- **Decision core** (`plant_decision()`): `FOCUS_CROP` override → **Energy floor**
  (`power < MIN_POWER_STOCK`) → **unlock steering** → **lowest-stock balance** (only
  once all unlocks are maxed).
- **Unlock steering** (`get_next_unlock()`): finds the next non-maxed unlock and the
  single resource it's most short of (bottleneck), and farms *only* that until the
  unlock is affordable — dynamic for any resource (Bone→snake, Gold→maze/pumpkin-for-
  substance, crops→`check_stock`), shifting the bottleneck as each fills. No throttling
  or balancing while unlocks remain.
- **`auto_unlocks()`**: buys ANY unlock whose full `get_cost()` is affordable
  (`can_afford`, multi-resource aware) — fixed the old single-payment assumption that
  stranded Polyculture.
- **Bones** (`farm_bones()`): apple-targeted snake — counts apples via `measure()` on
  the safe Hamiltonian cycle and cashes out at exactly `BONES_TARGET_TAIL` (default 900
  → ~32M Bones). Live-calibrated: bones ≈ **40×tail²**, ~2.7 apples/lap, self-collision
  at tail ~1023, `move()` tick floor ~37. Origin-safe (`goto_sw()` first) + lap safety cap.
- **Pumpkin**: dead pumpkins are cleared by `plant()` (never `till()` — it poisons the
  soil); fertilizer check uses live `num_items`; water loop bounded. No more empty plots.
- Full crop cycle, multi-prerequisite chain, multi-drone column splitting (NUM_DRONES),
  sunflower, gold tracking, configurable watering.
- **Maze / Gold parallelism** (`farm_maze()`, `config.MAZE_DRONES`, default 32): places
  `MAZE_DRONES` solvers evenly around the field perimeter *before* growing the maze (walls
  block placement after), all wall-follow at once; nearest-to-treasure wins and harvests,
  losers bail the instant `num_items(Gold)` jumps (live-shared across drones — no slow
  tail). `=1` falls back to `farm_maze_single()`; `=4` reproduces the old four corners.
  Verified live: spawned drones start on the parent's tile, globals are COPIED per drone
  (coordinate via world state, not globals), drones don't block each other, walls are
  `Entities.Hedge`. **Throughput is power-bound** — see the power-confound decision below.
- Goal status line: `Current Goal: <crop> for Unlock: <unlock>` (or `Unlocks Complete!`).
- **Companion farming** (`get_companion()`/Polyculture) — fully built (triplet + chain +
  auto-routing), correct, and **committed but default OFF**. Measured ~19× slower than
  monoculture (single-drone can't beat 32-drone parallelism even at ×160); kept for the
  verified mechanic / a possible future multi-drone rebuild. NOT in use.
- **Tooling**: `simulate()` no-starvation bench harness; 13 project skills (see below).

**In progress:** the DLC mining module above (probe phase; B1 Bamboo run next). The June "grind Top_Hat" item is stale — see the first paragraph.

**Broken / not done:**
- **Pumpkin giant-merge** not optimized — dead pumpkins are now cleared, but the per-tile
  logic doesn't aim for the giant-pumpkin area bonus. Not blocking.
- **Companion farming** — RESOLVED as not-worth-running (measured slower); shelved, not a
  bug. Would need a multi-strip (multi-drone) chain or much higher Polyculture to win.

---

## Current Goals

### Short-term (next 1–3 sessions)
1. **Run probe B1** (multi-drone surface Bamboo + Bamboo L2 yield) and design the parallel Bamboo farm — Bamboo gates Mining L5, Petrified L2, Special_Soils, Debug_Place, Pyramid, Treasure_Map and the Leaderboard.
2. Optional **probe D2** (full minesweeper solve of a Dynamite board: deduction rules, edge wrapping, cash-out by hitting a known live block) — only the Underground_Leaderboard's 20,000 Dynamite needs it.
3. **Ask before buying** the cheap levels (Iron L4 {Coal 450}, Rice L5 {Block 2000}, Coal L3 {Rice 1000}, Quartz L2 {Iron 200}, Bamboo L3 {Rice 800}, Mushrooms L2 {Gold 600}, Dynamite L2 {Mushroom 400}) — Mushrooms/Dynamite L2 yield effects are untested.
4. **Then implement DLC support in `main.py`**: dispatch mining BEFORE the 32-drone `farm_grid` branch, retry loops for the random Coal/Mushroom/Dynamite strata, a time-based stall watchdog, runtime unlock enumeration, the blocked list (Explosive_Drill), base-stock floors; verify with /syntax-check, /bench, /live-verify, /unlock-status, commit via /ship-change.
5. Carried over (base game, low priority now that Gold ≈ 24M, Weird_Substance ≈ 55M, Fertilizer ≈ 120k): `trade(Items.Fertilizer)` auto-trade; pumpkin giant-merge take 2.

### Long-term
- Fully hands-off completion of the tech tree with no manual levers, then steady-state balance forever.
- Companion farming only becomes worthwhile via a **multi-strip (multi-drone) chain** or
  once Polyculture climbs many more levels — revisit only if the throughput math flips.
- Harness v2: config auto-tuning / A/B strategy comparison (now have the `throughput-ab` skill).

---

## Recent Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2026-11-20 | Explosive_Drill (120k Mushroom + 12M Dynamite) goes on the blocked list | Its Mushroom cost alone is >= 27–111 game-h single-drone (<= ~3,072 merges per stratum world, so >= 40 worlds); user approved after seeing the measured rates |
| 2026-11-20 | Parallelize surface Bamboo across the existing 32-drone column split; "no multi-drone mining" stays for underground work only | Bamboo is a surface crop and gates the most unlocks (252k+ Bamboo); single drone ~12 game-h for the Leaderboard alone, 32 drones ~25 game-min |
| 2026-11-20 | Buy Dynamite L1 (4,000 Gold + 80 Mushroom), then probe it | Dynamite gates the Leaderboard (20k) and Explosive_Drill; its production mechanic was unknown until bought (docs page unlocks with it). Gold was already ~24.4M, so no maze step was needed |
| 2026-11-20 | Measure each Mushroom tile right before use (lazy per-well uncovering) instead of surveying a whole patch first | A full survey cost ~1.2 game-s/tile and 19% of its later pushes failed on stale types; measuring seconds before use gave 43/43 merges with 0 stale readings |
| 2026-11-20 | Treat 3-sample rates as provisional; re-measure before sizing | Coal L2 read 1.84/s over 3 attempts but 0.77/s over 7 (sheets appear in ~30–50% of worlds) |
| 2026-11-13 | Finish probing every DLC resource before writing any bot code; agree the blocked list from measured run-times | Avoids building routines around guessed mechanics; every verified mechanic is saved to memory first |
| 2026-06-18 | Steer to the next unlock's bottleneck resource, not lowest-stock, while unlocks remain | User's model: pour everything into the upgrade being chased; balance only after all unlocks are maxed |
| 2026-06-18 | While steering to an unlock, no throttle/no balance fallback | Falling back to balance farmed off-task resources (e.g. Gold) that weren't needed for the unlock |
| 2026-06-18 | `auto_unlocks` buys any affordable unlock (full cost dict) | Old single-`required_item` check silently skipped bones-cost/multi-resource unlocks (Polyculture, Top_Hat, Remains) |
| 2026-06-18 | Bones target = apple count (`BONES_TARGET_TAIL`), not laps; precise cash-out; default 900 | Deterministic yield (bones=40×tail²); a snake death halts the WHOLE bot, so stay clear of the ~1023 collision |
| 2026-06-18 | `farm_bones()` goes to origin before snaking | Snake path is origin-relative; the main loop left the drone mid-field → it tangled into its tail and halted the program |
| 2026-06-18 | Never `till()` a dead pumpkin; `plant()` clears it directly | Live-probed: `till()` reverts the dead-pumpkin Soil to Grassland, after which planting silently fails |
| 2026-06-18 | Removed `MIN_WEIRD_SUBSTANCE_STOCK`; maze dispatches via `Items.Gold` | The WS-threshold auto-maze left the goal stuck on "Weird_Substance"; Gold is now just a balanced/steered resource with a clear label |
| 2026-06-19 | Built companion farming (triplet + chain-random + auto-routing), then SHELVED it (default off) | Timed live A/B: single-drone companion ~19× SLOWER than 32-drone monoculture (~0.24M vs ~4.47M wood/sec). ×160 is only ~2.8×/drone, can't beat 32× parallelism |
| 2026-06-19 | Decide farming strategy by MEASURED throughput, not per-move analysis | My per-move "2.7× faster" claim was wrong — it ignored parallelism. Only wall-clock resources/sec (same clock both variants) tells the truth → `throughput-ab` skill |
| 2026-06-19 | `get_companion()` verified: returns `(type,(x,y))`, absolute+wrapping coords, stable-per-plant, ×160 | Live probes; saved to `companion_mechanic` memory. Only Grass/Bush/Tree/Carrot participate (Cactus/Pumpkin/Sunflower → None) |
| 2026-06-19 | Parallelize gold/maze: `MAZE_DRONES` solvers around the perimeter racing one maze; default 32 | Gold was the slowest goal (single-drone wall-follow). Measured ~2× (4) → ~4.7× (14) faster; coordinate via live-shared `num_items(Gold)` since drone globals are copied not shared |
| 2026-06-19 | Power confound: benchmark drone-count scaling ONLY with the energy floor active (`FOCUS_CROP=None`) | Under `FOCUS_CROP="Maze"` the energy floor is disabled, so 32 drones drained Power to 0 and ran at HALF speed → measured *slower* than 14 (an artifact). In production (None) 32 ties/edges 14 |
| 2026-06-19 | Unlock game achievements via throwaway `probe.py` scripts; built `achievement-hunter` skill | 5 achievements done this session; the popup (user-confirmed) is the real signal, code lives only in gitignored scratch (no commit). Hardened `throughput-ab`/`output-watcher` with the power + stale-variant gotchas |
| 2026-06-14 | `MIN_CARROT_FOR_PUMPKIN` reserve | Pumpkin planting costs 256 Carrot; without a floor the pumpkin path drains carrots to 0 |

---

## Known Issues / Tech Debt

- **`main.py` has no DLC support** — with `FOCUS_CROP=None` the unlock steering meets DLC costs in unmapped resources (Block/Coal/Iron/Quartz/Mushroom/Rice/Bamboo/Dynamite) and would stall until the mining module is built.
- **DLC strata are random per world**: Mushroom stratum in ~30% of worlds (retry loop ~4 tries x ~30 game-s), Coal sheets in ~30–50% of scans, Dynamite stratum depth varies (-62 / -205 seen); the bot needs clear()/pit/check retry loops and a time-based (not loop-count) stall watchdog.
- **Unverified/unwritten**: Bamboo L2 effect and multi-drone Bamboo behaviour (probe B1 pending); Mushrooms L2 / Dynamite L2 yield effects; a Dynamite board solver (edge wrapping of `measure()` untested); whether Mushroom tile types really drift over tens of seconds.
- **Probe tooling pitfalls**: the output watcher's quiet-period fallback must be >= 450 s (the game can run slow in real time, one 150 s fallback fired early); the user sometimes re-runs the loaded probe between steps, so check `output.txt` contents/mtime before assuming a result is yours; keep probe top-level names distinct from function locals (an earlier probe died silently otherwise).
- **No fertilizer auto-trade** — weird substance (→ Gold) only regenerates from spending
  the fertilizer stockpile (~1.54M); no `trade()` exists anywhere, so if fertilizer hits
  0 the Gold/substance path stalls (the gold-steer branch falls through rather than
  deadlocking). Plenty of runway for now; real fix is an auto-trade step.
- **Pumpkin giant-merge** — per-tile logic clears dead pumpkins but doesn't form giants
  for the area bonus. Distinct from the now-fixed growth-reset/empty-plot bugs.
- **Bones not bench-testable** — `change_hat` errors in `simulate()`, so `bench_main`
  skips bones; validate live only. (Steering-to-bones loops are no-ops in-sim.)
- **Stale-running-code trap** — editing `main.py`/`config.py` does nothing to a *running*
  script; it must be restarted (`import config` is cached). Apparent "bugs" are often just
  un-restarted old code. (The bot ran on `FOCUS_CROP=None` monoculture all session; the
  prior pending companion-restart is resolved. Config is `FOCUS_CROP=None`, `MAZE_DRONES=32`.)
- **Maze throughput is power-bound** — 32 maze drones drain `Items.Power` fast; the energy
  floor (`MIN_POWER_STOCK`) maintains it in `FOCUS_CROP=None`, but under `FOCUS_CROP="Maze"`
  power hits 0 and drones halve speed. Never benchmark drone-count scaling under maze-focus.
- **Stale `output.txt` trap** — a watcher (or a manual read) can match a *prior* run's
  content; byte-identical numbers across "two" runs is the tell. Freshness-gate on mtime.
  (Now a hardened gotcha in the `output-watcher` and `game-probe` skills.)
- **Companion code is dead weight** — built, correct, but off and slower. Don't re-enable
  without the multi-drone rebuild; see `companion_mechanic` memory for the full verdict.
- **`MAX_SUNFLOWER_SEED_COST = 6` is stale** — real cost is 1 Carrot now; harmless guard.
- **No class/OOP** — hard game constraint; all state is module-level globals.

---

## Next Steps

**Session 2026-11-20 next steps:**
1. **Resume at probe B1**: confirm the game is up and the live bot is stopped, check `head -1 probe.py` says probe B1 (else `cp ~/farmer-save-backups/probe-B1-bamboo-multidrone.py probe.py`), arm the output-watcher (sentinel `BAMBOO_B1_DONE`, settle >= 450 s), have the user run `probe`, then read EXP A (Bamboo L2 fruit pattern/cap/yield vs L1's ~103 per plant), EXP B (single-drone Bamboo/game-s on a 16-plant lane), EXP C1/C2 (4 and 16 spawned drones: scaling and Power before/after).
2. Design the parallel Bamboo farm from B1's result (plant column + free lane per drone, pluck until capped, harvest, replant).
3. Optional probe D2 (Dynamite minesweeper solve) for the Leaderboard's 20,000 Dynamite; ask before buying the cheap levels listed under Goals.
4. Then build the DLC support in `main.py` and verify per the brief (blocked list = Explosive_Drill).
5. Carried over: `trade(Items.Fertilizer)` auto-trade and pumpkin giant-merge take 2 (both low priority now); achievements/Leaderboards remain the post-tree goal.

---

## Skills (project-local, `.claude/skills/`)

`bench`, `config-set`, `farm-status`, `game-probe`, `syntax-check`, `probe-sweep`
(bisect a knob in-game), `output-watcher` (auto-read output.txt on run completion),
`ship-change` (syntax→bench→commit pipeline), `verify-mechanic` (confirm game behavior via
wiki/probe → memory), `diagnose-behavior` (trace `plant_decision`), `unlock-status` (dump
unlock progress), `live-verify` (restart + confirm a change took), `throughput-ab` (measure
wall-clock resources/sec to A/B two strategies), and new this session: **`achievement-hunter`**
(force a game achievement via a self-contained `probe.py` script + confirm the popup).
`throughput-ab` + `output-watcher` were hardened with the power-confound and stale-variant
(BOOT-marker gating) gotchas.
