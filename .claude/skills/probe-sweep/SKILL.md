---
name: probe-sweep
description: Empirically find the safe or optimal value of a farmer-bot parameter via repeated in-game probe runs (per-iteration logging + bisection), then bake it into config.py and validate. Use when the user says "probe-sweep", "find the safe limit for X", "tune X empirically", "bisect the cap for X", "find the optimal X in-game", or "sweep a parameter".
---

# Probe Sweep

Find the threshold (max-safe-before-failure) or optimum (best ratio) of a tunable
farmer-bot parameter by iterating in-game probe runs, narrowing the value each round,
then deploying the result to `config.py` with a safety margin.

Builds on the single-shot `game-probe` skill (probe mechanics, Save0 symlink) — this
adds the **bisect-and-bake loop** on top. Lean on `config-set` for knob writes and
`bench` for twin regeneration; don't duplicate them.

## Steps

### 1. Pin down the goal (ask the user)
- **Which parameter** are we sweeping (a `config.py` knob, or a value that will become one)?
- **What are we finding** — the *max safe value before failure*, or the *optimal* value of some ratio (e.g. bones-per-tick)?
- **What's the failure / success signal** in `output.txt`? (e.g. snake self-collision = the run dies, so the cash-out/sentinel line is missing and the per-iteration markers stop partway.)

### 2. Edit the probe with per-iteration logging + a safety bound
Edit `/home/bosko/projects/farmer/probe.py` to exercise the parameter, and:
- `quick_print` a marker **every iteration** (e.g. `quick_print("lap " + str(lap) + " tail " + str(tail) + " ...")`) so that if the run dies, the last marker **pins the exact failure point**.
- Always include a **safety bound** on the loop (a hard cap on iterations) so the probe can never run away into a catastrophic state.
- End with a **sentinel** (`quick_print("DONE")`) and the result line so a clean finish is unambiguous.
- `probe.py` is symlinked into the game's `Save0/`, so edits **auto-sync — no copy/paste**.

### 3. Syntax-check
```bash
cd /home/bosko/projects/farmer && python -c "import ast; ast.parse(open('probe.py').read()); print('OK')"
```
Pyright "X is not defined" errors for `Items`/`Entities`/`move`/`quick_print`/etc. are
**expected** (game-injected APIs) — not real errors.

### 4. Run it in-game (the user does this)
Tell the user to **stop the main bot**, run `probe` in-game, and say "done". You cannot
run it yourself. (Stopping the bot matters: a probe death is contained, but it shares the
farm.)

### 5. Read and interpret
```bash
OUT="$HOME/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt"
grep -E "<iteration markers>|<sentinel>|<result>" "$OUT"
```
- **Clean finish:** sentinel + result line present → that value is safe; push higher.
- **Failure:** markers stop partway with **no sentinel** → the last marker pins the failure
  iteration (e.g. last `lap 193 tail 985` then it died → collision just above 985).
- `output.txt` is **overwritten every run** — it only holds the latest.

### 6. Narrow and repeat
Bisect (or step) the value and go back to step 2 until the threshold is pinned. Because of
the per-iteration logging, **big jumps are safe diagnostically** — a crash still pins the
exact failure point, so you don't need tiny steps.

### 7. Bake in the result (with a safety margin)
- Write the chosen value **safely below the found limit** into `config.py` via a targeted
  `Edit` (margin matters — a live failure can halt the whole bot; e.g. this was first
  derived as collision at tail ~1023 → deployed `BONES_TARGET_TAIL = 900`). For a simple
  known value, `config-set` can do the write.
- Regenerate the bench twin and confirm it compiles:
  ```bash
  cd /home/bosko/projects/farmer && python3 gen_bench_main.py && python -m py_compile bench_main.py && echo OK
  ```
- Syntax-check `main.py`/`config.py` if either was edited.
- Offer to commit via the `git-commit` skill.

## Gotchas
- **Game Python dialect**: no keyword args, no ternary (`a if c else b`), no list/dict
  comprehensions, and `global` takes **one name per line** (no `global a, b, c`). Any of
  these cause a silent/parse failure with no useful output.
- **Always test in `probe.py`, never by trial-and-error on the running bot.** A failure
  in-game (e.g. snake self-collision) can halt the whole live bot; the probe is contained.
  Always keep a safety bound in the probe loop.
- **Deploy below the limit.** The found number is the edge of failure — bake the config
  value with margin, not at the limit.
- Reuse, don't duplicate: `game-probe` (probe + Save0 symlink details), `config-set`
  (knob writing), `bench` (twin regeneration).
