# Project State — Farmer Bot

Last updated: 2026-06-19

---

## Current Project State

The bot is an **unlock-driven, set-and-forget** agent: it pours all effort into whatever
the next upgrade needs, and only balances resources once the tech tree is fully maxed. It
runs **32-drone monoculture** — the fast path. This session built a full Polyculture
companion-farming feature, then **measured it ~19× slower than monoculture and shelved
it** (see decisions). Steering is now toward **Top_Hat** (1B Hay + 10B Wood + 1B Carrot +
1B Cactus + 100M Gold); as of this session the crop stocks were already at/above target
(Hay ~1.4B, Wood ~10.4B, Carrot ~1.06B), so the remaining Top_Hat bottleneck is **Cactus
and Gold**. The_Farmers_Remains (100M Bones) appears complete or further than Top_Hat
(get_next_unlock named Top_Hat as the closest unmaxed unlock). Polyculture keeps
auto-leveling (now ×160).

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
  maze/sunflower, gold tracking, configurable watering.
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
  un-restarted old code. **PENDING: the live bot still needs a restart** to drop back onto
  monoculture (it was last left on a companion test config).
- **Stale `output.txt` trap** — a watcher (or a manual read) can match a *prior* run's
  content; byte-identical numbers across "two" runs is the tell. Freshness-gate on mtime.
  (Now a hardened gotcha in the `output-watcher` and `game-probe` skills.)
- **Companion code is dead weight** — built, correct, but off and slower. Don't re-enable
  without the multi-drone rebuild; see `companion_mechanic` memory for the full verdict.
- **`MAX_SUNFLOWER_SEED_COST = 6` is stale** — real cost is 1 Carrot now; harmless guard.
- **No class/OOP** — hard game constraint; all state is module-level globals.

---

## Next Steps

1. **Restart `main.py`** to put the live bot back on monoculture (pending from this session).
2. Confirm Top_Hat's live bottleneck (`unlock-status`) — expected Cactus then Gold — and
   watch it grind / unlock. (`output-watcher` for the `Unlocked Top_Hat` line.)
3. Add `trade(Items.Fertilizer)` auto-trade so the Gold/substance chain is self-sustaining
   (now load-bearing since Gold is a remaining Top_Hat bottleneck).
4. Pumpkin giant-merge take 2 — change one variable, watch one field in-game.

---

## Skills (project-local, `.claude/skills/`)

`bench`, `config-set`, `farm-status`, `game-probe`, `syntax-check`, `probe-sweep`
(bisect a knob in-game), `output-watcher` (auto-read output.txt on run completion),
`ship-change` (syntax→bench→commit pipeline), `verify-mechanic` (confirm game behavior via
wiki/probe → memory), `diagnose-behavior` (trace `plant_decision`), `unlock-status` (dump
unlock progress), `live-verify` (restart + confirm a change took), and new this session:
`throughput-ab` (measure wall-clock resources/sec to A/B two strategies — the "is X
faster?" answer). `output-watcher` + `game-probe` were hardened with stale-content /
standalone-probe / occupied-tile gotchas.
