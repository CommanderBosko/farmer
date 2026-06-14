# Configuration for the Farmer bot

# Set a focus crop, or set to None for default behavior.
# Possible values: "Hay", "Wood", "Carrot", "Pumpkin", "Cactus", "Maze", "Sunflower", None
# WARNING: FOCUS_CROP bypasses prerequisite stock checks entirely.
# If planting a crop that requires prerequisites (e.g. Pumpkin requires Carrot),
# you must pre-stock those prerequisites manually before enabling this mode.
FOCUS_CROP = None

# How often to print the current goal (every N loops). Set to 1 to print every loop.
# Set to 0 or None to disable.
PRINT_GOAL_INTERVAL = 1

# The minimum amount of a prerequisite resource to have in stock before
# planting the next tier of crop.
MIN_PREREQ_STOCK = 500000

# Minimum power to keep on hand. When power drops below this the bot will
# switch to sunflower farming until it's replenished. Power doubles drone
# speed (1 power consumed per 30 actions), so keeping it stocked is worth
# the brief detour. Requires Unlocks.Sunflowers to be purchased first.
MIN_POWER_STOCK = 5000

# Minimum Carrot stock required before entering sunflower (power) mode. Sunflower
# seeds cost Carrots (up to 6 each), so the bot needs a carrot buffer to fill the
# grid. Below this, it farms carrots instead of getting stuck unable to plant
# sunflowers. Raise it if you run a large grid (cost scales with world_size^2);
# lower it to enter sunflower mode more eagerly.
MIN_CARROT_FOR_SUNFLOWER = 2000

# Carrot RESERVE that pumpkin planting will not dip below. Planting a pumpkin costs
# 256 Carrot, and the bot farms pumpkins to afford pumpkin-cost upgrades — without a
# floor, one pumpkin pass (made worse by the inner replant loop) drains carrots to 0,
# leaving carrot oscillating 0<->~600k. With this reserve the pumpkin path stops
# planting once live carrot stock falls below it, so carrot floors here instead of 0.
# Raise to protect more carrots (slower pumpkin growth); lower for more pumpkins.
MIN_CARROT_FOR_PUMPKIN = 100000

# Weird_Substance threshold for triggering maze farming. The bot will run a
# maze (clearing the current farm) only when this much WS is stockpiled.
# Maze cost = world_size * 2^(maze_level-1), so 500 comfortably covers any
# level. Lower this for more frequent maze runs; raise it to prioritize crops.
MIN_WEIRD_SUBSTANCE_STOCK = 500

# Gold target. When > 0, the bot will prioritize maze runs (as soon as one
# maze worth of WS is available) until gold reaches this amount. Set this
# before manually purchasing gold-cost upgrades (Top Hat, Megafarm, Debug_2,
# Simulation, Leaderboard), then reset to 0 when done.
MIN_GOLD_STOCK = 0

# Minimum soil water level before watering a cell. Applies to all soil-based crops
# (carrot, wood, sunflower); pumpkin always waters to 1.0 regardless. Set to 0.0
# to disable. get_water() returns 0.0–1.0; watering requires Items.Water in inventory.
MIN_WATER_LEVEL = 0.5

# Number of drones to use for parallel farming (1 = single-drone, max = 32 with Megafarm maxed).
# Capped automatically to world_size — you can't farm more columns than exist.
# Maze always runs single-drone regardless of this setting.
NUM_DRONES = 32
