---
name: game-probe
description: Run a one-off diagnostic snippet inside the game "The Farmer Was Replaced" and read the result. Use when the user says "probe the game", "run a probe", "check X in-game", "what does X return in-game", "dump the Items/Entities/Hats enum", or "find the in-game cost of X". Writes a quick script to probe.py (auto-synced into the game), has the user run it, then reads output.txt.
---

# Game Probe Skill

Answer a question about the live game state/API by running a tiny diagnostic
in-game and reading its output. The game injects its API at runtime (`plant`,
`num_items`, `get_cost`, `quick_print`, enums like `Items`/`Entities`/`Hats`/
`Unlocks`), so the only way to learn a real value is to run code in-game and read
what it prints. You cannot run the game yourself — the user does.

## Key paths (baked in)

- Probe script (edit this): `/home/bosko/projects/farmer/probe.py`
- Game output (read this): `$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt`

`probe.py` is symlinked into the game's `Save0/`, so writing it **auto-syncs into
the game — no copy/paste**. `output.txt` is **overwritten every run** (only the
latest run is there).

## Steps

1. **Write the diagnostic** to `/home/bosko/projects/farmer/probe.py`. Emit every
   result with `quick_print(...)`, and end with a sentinel like
   `quick_print("PROBE_DONE")` so you can tell the run finished. Follow the game
   dialect (see Gotchas). To dump an enum: `for e in Entities: quick_print(str(e))`.
   To get a cost: `quick_print(str(get_cost(Entities.Apple)))`.

2. **If `probe` isn't registered in-game yet** (first use, or it never existed),
   tell the user to create a file named `probe` in-game once and reload the save
   (the game caches its file list at load — see the `game-file-sync` memory). After
   that, edits auto-sync. Confirm the symlink exists:
   ```bash
   ls -la "$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/Saves/Save0/probe.py"
   ```
   If missing: `ln -sf /home/bosko/projects/farmer/probe.py "<Save0>/probe.py"` (game closed), then reload.

3. **Warn first if the snippet is destructive.** Read-only calls (`num_items`,
   `get_cost`, `get_world_size`, enum dumps) are safe. Calls that change live state
   — `clear()`, `change_hat()`, `set_world_size()`, `plant()`, `move()` — alter the
   running farm; flag that to the user before they run it.

4. **Ask the user to run `probe` in-game and say "done".** You cannot run it.

5. **Read and interpret** the result:
   ```bash
   cat "$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt"
   ```
   If the run produces a lot of game warnings, `grep` for your sentinel / labels
   instead. If you don't see your final sentinel line, the script errored mid-run
   (or is still running) — check for an in-game error and look at the last line
   printed.

## Gotchas (game Python dialect)

- **No keyword arguments**, no list/dict comprehensions, no ternary expressions
  (`a if c else b`) — any of these cause a silent parse failure with no output.
  (See the `no-keyword-args` memory.)
- The generated `__builtins__.py` stub can be **wrong/incomplete**: e.g. the bones
  item is `Items.Bone` (not `Items.Bones`), and it omits `simulate`/`spawn_drone`.
  Verify names by dumping the enum (`for x in Items: quick_print(str(x))`).
- Pyright "X is not defined" errors for `Items`/`Entities`/`quick_print`/etc. are
  **expected** — they're game-injected, not real errors.
- `quick_print` output lands in `output.txt`; `print` writes in the air above the
  drone (slower). Prefer `quick_print` for probes.
- **`probe.py` is standalone — it CANNOT call `main.py`'s functions.** Calling a main
  helper (e.g. `goto_sw()`) errors with `"<name> has never been defined. It does appear
  to be defined in the file main..."`. Each probe must define every helper it needs
  inline (copy the few lines), or avoid them — operate on the current tile and use only
  game-injected APIs (`move`, `get_pos_x/y`, `harvest`, `till`, ...).
- **`plant()` silently no-ops on an occupied tile** — so a probe that means to plant a
  fresh test plant must FULLY CLEAR the tile first (`harvest()` then `till()`), not just
  ensure the ground type. A guard like `if get_ground_type() != Grounds.Soil: till()`
  does nothing when a leftover plant already sits on soil, so `plant()` fails and you
  read the OLD plant's state as if it were the new one (cost me a false "carrot returns
  None"). Confirm with `get_entity_type()` after planting before trusting the reading.
