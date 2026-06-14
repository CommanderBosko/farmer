---
name: config-set
description: Update a config.py knob for the farmer bot. Use when the user wants to change FOCUS_CROP, MIN_GOLD_STOCK, MIN_POWER_STOCK, MIN_PREREQ_STOCK, MIN_WEIRD_SUBSTANCE_STOCK, PRINT_GOAL_INTERVAL, or USE_MULTIPLE_DRONES.
---

# Config Set Skill

Update a single knob in `/home/bosko/projects/farmer/config.py`.

## Valid keys and their types

| Key | Type | Notes |
|-----|------|-------|
| `FOCUS_CROP` | string or None | Must be one of: `"Hay"`, `"Wood"`, `"Carrot"`, `"Pumpkin"`, `"Cactus"`, `"Maze"`, `"Sunflower"`, or `None` |
| `PRINT_GOAL_INTERVAL` | int | 0 or None disables printing |
| `MIN_PREREQ_STOCK` | int | Must be positive |
| `MIN_POWER_STOCK` | int | Must be positive |
| `MIN_WEIRD_SUBSTANCE_STOCK` | int | Must be positive |
| `MIN_GOLD_STOCK` | int | 0 disables gold grinding |
| `USE_MULTIPLE_DRONES` | bool | `True` or `False` |

## Steps

1. Read the current value of the key from `config.py`.
2. Validate:
   - Key exists in the valid keys list above
   - Value is the correct type and within allowed values
   - If invalid, report the error and stop — do not edit the file
3. Edit `config.py` to update the value. Use the Edit tool for a targeted in-place replacement.
4. Read back the changed line to confirm it looks correct.
5. Report: old value → new value.

## Rules

- Only edit the value, never the comment lines
- For `FOCUS_CROP`: write `None` (no quotes) or `"Hay"` (with quotes) as appropriate
- For booleans: write `True` or `False` (Python capitalization)
- If the user doesn't provide a value, ask for one
- Never edit any file other than `config.py`
