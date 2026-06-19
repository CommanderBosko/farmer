# Project State — Farmer Bot

Last updated: 2026-06-18

---

## Current Project State

The bot is now an **unlock-driven, set-and-forget** agent: it pours all effort into
whatever the next upgrade needs, and only balances resources once the tech tree is
fully maxed. The crop progression, bones farming, and the decision core were all
reworked this session and are **live-validated**. Only **3 unlocks remain**:
Polyculture (auto-leveling), The_Farmers_Remains (100M Bones — currently being farmed),
and Top_Hat (1B Hay + 10B Wood + 1B Carrot + 1B Cactus + 100M Gold — the long grind).

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
- **Tooling**: `simulate()` no-starvation bench harness; 9 project skills (see below).

**In progress (grinding toward the goal):**
- The_Farmers_Remains — bot is farming Bones toward 100M (live-confirmed steering).
- After it: Top_Hat — steering will shift to its biggest shortfall (Wood, then the rest).

**Broken / not done:**
- **Pumpkin giant-merge** not optimized — dead pumpkins are now cleared, but the per-tile
  logic doesn't aim for the giant-pumpkin area bonus. Not blocking.
- **Companion planting** (`get_companion()`) still unused for crops (lower priority now
  that the bot is unlock-steering; Polyculture's multiplier already applies to Bones).

---

## Current Goals

### Short-term (next 1–3 sessions)
1. Watch **The_Farmers_Remains** complete (Bones → 100M) and confirm the hand-off to
   **Top_Hat** steering (Wood first).
2. **Auto-trade fertilizer** — add `trade(Items.Fertilizer)` so weird substance (→ Gold
   via maze) is self-sustaining; today there's *no* trade logic, so substance only comes
   from spending the ~1.54M fertilizer stockpile.
3. Optional: companion planting (`get_companion`) for crop yield; pumpkin giant-merge take 2.

### Long-term
- Fully hands-off completion of the tech tree with no manual levers, then steady-state balance forever.
- Harness v2: config auto-tuning / A/B strategy comparison against bench `run_time`.

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
- **Stale-running-code trap** — editing `main.py` does nothing to a *running* script; it
  must be restarted. Several apparent "bugs" this session were just un-restarted old code.
- **`MAX_SUNFLOWER_SEED_COST = 6` is stale** — real cost is 1 Carrot now; harmless guard.
- **No class/OOP** — hard game constraint; all state is module-level globals.

---

## Next Steps

1. Live: confirm The_Farmers_Remains unlocks (Bones → 100M), then that steering shifts to
   Top_Hat's Wood. (`live-verify` / `output-watcher` for the `Unlocked` line.)
2. Add `trade(Items.Fertilizer)` auto-trade so the Gold/substance chain is self-sustaining.
3. Companion planting (`get_companion`) for crop yield once unlock-grinding allows.
4. Pumpkin giant-merge take 2 — change one variable, watch one field in-game.

---

## Skills (project-local, `.claude/skills/`)

`bench`, `config-set`, `farm-status`, `game-probe`, `syntax-check`, plus this session's:
`probe-sweep` (bisect a knob in-game), `output-watcher` (auto-read output.txt on run
completion), `ship-change` (syntax→bench→commit pipeline), `verify-mechanic` (confirm
game behavior via wiki/probe → memory), `diagnose-behavior` (trace `plant_decision`),
`unlock-status` (dump unlock progress), `live-verify` (restart + confirm a change took).
