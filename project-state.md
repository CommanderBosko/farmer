# Project State — Farmer Bot

Last updated: 2026-06-19

---

## Current Project State

The bot is an **unlock-driven, set-and-forget** agent: it pours all effort into whatever
the next upgrade needs, and only balances resources once the tech tree is fully maxed. It
runs **32-drone monoculture** — the fast path. Steering is toward **Top_Hat** — the **final
upgrade** in the tree (1B Hay + 10B Wood + 1B Carrot + 1B Cactus + 100M Gold); crop stocks
are at/above target, so the live bottleneck is **Gold** (the bot was last seen "Current
Goal: Gold for Unlock: Top_Hat"). Polyculture keeps auto-leveling (now ×160).

**This session** parallelized the slow gold/maze path and started knocking out **game
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

**In progress (grinding toward the goal):**
- **Top_Hat** — the active steer. Crop costs (Hay/Wood/Carrot) appear met; remaining
  shortfall is **Cactus (1B)** and **Gold (100M)**, so steering should be running cactus
  and maze. Confirm the live bottleneck next session (`unlock-status`).

**Broken / not done:**
- **Pumpkin giant-merge** not optimized — dead pumpkins are now cleared, but the per-tile
  logic doesn't aim for the giant-pumpkin area bonus. Not blocking.
- **Companion farming** — RESOLVED as not-worth-running (measured slower); shelved, not a
  bug. Would need a multi-strip (multi-drone) chain or much higher Polyculture to win.

---

## Current Goals

### Short-term (next 1–3 sessions)
1. Confirm Top_Hat's remaining bottleneck live (`unlock-status`) — expected **Cactus**
   then **Gold** — and that steering is grinding them. Then watch Top_Hat unlock.
2. **Auto-trade fertilizer** — add `trade(Items.Fertilizer)` so weird substance (→ Gold
   via maze) is self-sustaining; today there's *no* trade logic, so substance only comes
   from spending the ~1.54M fertilizer stockpile. Matters now that Gold is a bottleneck.
3. Optional: pumpkin giant-merge take 2.

### Long-term
- Fully hands-off completion of the tech tree with no manual levers, then steady-state balance forever.
- Companion farming only becomes worthwhile via a **multi-strip (multi-drone) chain** or
  once Polyculture climbs many more levels — revisit only if the throughput math flips.
- Harness v2: config auto-tuning / A/B strategy comparison (now have the `throughput-ab` skill).

---

## Recent Decisions

| Date | Decision | Rationale |
|---|---|---|
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

1. Watch **Top_Hat** (the final upgrade) unlock — Gold is the live bottleneck and the maze
   path is now ~2–5× faster. (`output-watcher` for the `Unlocked Top_Hat` line.)
2. Keep working through **achievements** (use the new `achievement-hunter` skill) and look
   at **Leaderboards** — the post-tree goal.
3. Add `trade(Items.Fertilizer)` auto-trade so the Gold/substance chain is self-sustaining
   (load-bearing since Gold is the remaining Top_Hat bottleneck).
4. Pumpkin giant-merge take 2 — change one variable, watch one field in-game.

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
