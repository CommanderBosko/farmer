---
name: farm-status
description: Show the current status of the farming bot. Use when the user asks what the bot is doing, what its current goal is, or wants to check if the bot is running correctly.
---

# Farm Status Skill

Read the bot's output log and summarize the current farming state.

## Output file path

```
/home/bosko/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/output.txt
```

## Steps

1. Read the last 80 lines of the output file using `tail -80`.
2. Parse and report:
   - **Current goal**: extract the "Current Goal: X (for upgrading Y)" lines
   - **Loop activity**: note if the separator lines (`---`) are appearing (bot is running)
   - **Any errors or unexpected output**: flag anything that looks like a Python traceback or error
3. Also read `/home/bosko/projects/farmer/config.py` to show the active config knobs.
4. Report a concise summary:
   - What crop is being farmed and why (unlock target or fallback)
   - Which config knobs are non-default
   - Any errors or warnings in the log

## Rules

- Do not modify any files
- If the output file doesn't exist or is empty, say so clearly
- Highlight anything that suggests the bot is stuck or crashing
