---
name: achievement-hunter
description: Trigger a "The Farmer Was Replaced" achievement by writing a self-contained probe.py snippet that forces the condition, then confirm the popup live. Use when the user says "get the X achievement", "the next achievement is X", "unlock X achievement", "achievement-hunter", or "let's grab an achievement".
---

# Achievement Hunter

Unlock a "The Farmer Was Replaced" achievement by running a tiny self-contained
script in-game that forces the achievement's condition, then confirming the popup.
You can't run the game — the user does — so the real success signal is the
achievement popup on their screen; the script's `*_DONE` sentinel only proves it
ran without crashing.

## Key paths (baked in)

- Probe script (edit this): `/home/bosko/projects/farmer/probe.py` — symlinked into
  the game's `Save0/`, so writing it **auto-syncs into the game** (no copy/paste).
- Two already-registered scratch target files (for multi-file achievements like an
  import cycle): `/home/bosko/projects/farmer/probe_target_a.py` and
  `/home/bosko/projects/farmer/sim_probe_target.py`.
- Game output (read this): `$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt`

## Steps

1. **Get the spec.** Ask the user for the achievement name and its in-game mechanic
   hint (usually a tooltip), unless they already gave it.

2. **Write a SELF-CONTAINED snippet** to `/home/bosko/projects/farmer/probe.py`.
   - `probe.py` **cannot call `main.py` functions** (errors `"<name> has never been
     defined ... defined in the file main"`), so replicate any needed logic inline —
     e.g. for "Wrong Order" copy `farm_cactus`'s bubble sort but flip the comparator
     `>` to `<` (descending); define helpers like `goto_sw()` inline.
   - Start with a `quick_print("<X>_START")` marker and end with `quick_print("<X>_DONE")`.
   - **Game dialect:** NO keyword arguments, NO ternary (`a if c else b`), NO
     comprehensions; positional args only; use tabs; lists/sets are fine. Any of these
     causes a silent parse failure with no output.
   - To learn exact enum member names: `for e in Hats: quick_print(str(e))` (the same
     for `Items`/`Entities`). Use only OWNED items/hats.

3. **For heavy or destructive ops** (e.g. a full field of cacti), parallelize across
   drones mirroring `main.py`'s `farm_cactus()`: `spawn_drone()` over disjoint
   column/row ranges, then `wait_for()`. Print phase markers (`PLANTED`/`GROWN`/`SORTED`)
   so a stall is pinpointable. Only ONE `while` loop inside a cactus phase (no nested
   `while`), and **bound any grow-wait loop** so low seed stock can't hang it.

4. **Multi-file achievements** (e.g. "Circular Import") reuse the two existing
   registered scratch targets — edit `probe_target_a.py` and `sim_probe_target.py` to
   import each other and kick it off from `probe.py`. This avoids creating a NEW in-game
   file, which would need a save reload to register (the game caches its file list at load).

5. **Syntax-check** before handing off:
   `cd /home/bosko/projects/farmer && python -c "import ast; ast.parse(open('probe.py').read()); print('OK')"`.
   Pyright "X is not defined" for game-injected names (`quick_print`, `move`, `Hats`,
   `Items`, `Entities`, `spawn_drone`, …) is **expected**, not a real error.

6. **Arm `output-watcher` SENTINEL-ONLY** (not the settle fallback) — the live bot writes
   `output.txt` on a slow cadence during maze loops, so a settle gate misfires. Capture
   `ARMED=$(date +%s)`, freshness-gate every break on `mtime > ARMED`, and break on the
   `<X>_DONE` sentinel OR an `Error:` line. Arm it right before telling the user to run.

7. **Hand off:** tell the user to **STOP the live bot, run `probe` in-game, and WATCH THE
   GAME SCREEN for the achievement popup.** Then continue — the watcher reports back. The
   popup is the real success signal; the `*_DONE` sentinel / absence of `Error:` only
   confirms the snippet ran. Report the captured markers and ask the user to confirm the popup.

8. **Cleanup:** the achievement code lives only in gitignored scratch (`probe.py`,
   `probe_target_a.py`, `sim_probe_target.py` — see `.gitignore`), so cleanup =
   neutralize `probe.py` and restore the two targets to their prior scratch. **No commit**
   (they're gitignored; the working tree stays clean).

## Gotchas

- **Main helpers aren't game APIs.** `get_amount`, `goto_sw`, `farm_*` etc. are defined
  in `main.py`; a probe must inline them or use only injected APIs (use `num_items`, not
  `get_amount`; define `goto_sw` inline).
- **`plant()` silently no-ops on an occupied tile.** Fully clear (`harvest()` then
  `till()`) before planting a fresh test plant, and confirm with `get_entity_type()`.
- **The `__builtins__.py` stub is incomplete/wrong** — it omits `Hats`/`change_hat`/
  `spawn_drone` and miscalls some names (`Items.Bone`, not `Items.Bones`). Verify enum
  members by dumping them in-game.
- **Watch out for shared/destructive state.** `clear()` wipes the farm; `set_world_size()`,
  `change_hat()`, `plant()` change live state — flag destructive snippets to the user, and
  prefer operating on one tile when you can.

## Reference recipes (verified this session)

- **5 different hats on drones:** main drone `change_hat(h0)`, then
  `spawn_drone(wear, h1..h4)` where `wear` does `change_hat(h)` then idles via `do_a_flip()`;
  all 5 idle together so 5 distinct OWNED non-Dinosaur hats are worn at once.
- **Stack overflow:** unbounded recursion with the call NOT in tail position so it can't be
  optimized into a loop: `def recurse(n): return 1 + recurse(n + 1)` then `recurse(0)`.
- **Healer (cure an infected plant):** plant a carrot, then
  `use_item(Items.Weird_Substance)` twice — first infects, second cures.
- **Circular Import:** make `probe_target_a` and `sim_probe_target` import each other,
  kicked off from `probe.py`.
- **Wrong Order:** fill the field with cacti, wait for growth, bubble-sort rows then columns
  with the comparator flipped (`measure() < measure(East/North)` = descending).
