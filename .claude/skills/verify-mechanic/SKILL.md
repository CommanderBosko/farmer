---
name: verify-mechanic
description: Confirm how a game mechanic in "The Farmer Was Replaced" actually works, reconcile it with the bot's code, and record the verified fact to memory. Use when the user says "verify-mechanic", "how does X work in the game", "check the wiki for X", "is X actually true", "verify the mechanic".
---

# Verify Mechanic

Verify how a mechanic in "The Farmer Was Replaced" actually works against authoritative sources or a live probe, reconcile it with the bot's code, and record the confirmed fact to memory — never guess from training data.

## Steps

1. Search authoritative sources with WebSearch / WebFetch: the wiki at `https://thefarmerwasreplaced.wiki.gg/wiki/<Topic>` and the Steam community discussions. Extract the concrete behavior — numbers, entity names, function semantics.
2. Reconcile with the code: grep `main.py` for the relevant function or branch and note any mismatch between the wiki and the implementation.
3. If the wiki is silent or contradicts the code, get ground truth from the live game using the `game-probe` skill — write a tiny read-only probe to `probe.py`, have the user run it, then read `output.txt`.
4. Record the verified fact to the memory directory `/home/bosko/.claude/projects/-home-bosko-projects-farmer/memory/`: update the most relevant existing memory file (e.g. `pumpkin_mega_mechanic.md`, `bones_farming.md`, `simulate_sandbox.md`) or create a new one with frontmatter (name/description/metadata type: reference), and add a one-line pointer in `MEMORY.md`. Date the observation — memories are point-in-time.

## Gotchas

- Never assert game behavior from training data — always verify against the wiki/community or a live probe. Past guesses in this project were wrong (e.g. a snake "freeze" theory, a bone-yield multiplier, and the claim that `till()` clears dead pumpkins — it actually poisons the soil).
- Wiki URL form is `https://thefarmerwasreplaced.wiki.gg/wiki/<Topic>`. 404s are common — search first to find the correct page title.
- Leans on the `game-probe` skill for the live-probe step; reference it rather than duplicating probe mechanics.
