# Configuration for the Farmer bot

# Set a focus crop, or set to None for default behavior.
# Possible values: "Hay", "Wood", "Carrot", "Pumpkin", "Cactus", "Maze", "Sunflower", None
# WARNING: FOCUS_CROP bypasses prerequisite stock checks entirely.
# If planting a crop that requires prerequisites (e.g. Pumpkin requires Carrot),
# you must pre-stock those prerequisites manually before enabling this mode.
FOCUS_CROP = None

# --- Companion (Polyculture) farming ---
# When set, the bot ignores normal farming and runs a single-drone companion-planting
# sweep for this crop: each plant's get_companion() preference is satisfied at a nearby
# tile so the harvest yields the Polyculture multiplier (currently ~40x). Only Grass
# (Hay), Tree (Wood), and Carrot expose companions, so the valid values are:
#   "Hay", "Wood", "Carrot", or None (off — normal monoculture/unlock-steering).
# Single-drone by design (companion tiles cross column boundaries), so it trades the
# 32-drone parallelism for the per-harvest multiplier; it pulls ahead as Polyculture
# levels up. No-op unless Unlocks.Polyculture is unlocked. Hay needs no seeds; Wood/
# Carrot companions cost a few wood/hay to place (dwarfed by the multiplier).
COMPANION_CROP = None

# Companion movement strategy (only matters when COMPANION_CROP is set):
#   False = Stage 1 triplet: per tile place companion -> return -> harvest one crop type.
#   True  = Stage 2 chain-random: follow each plant's companion to the next plant,
#           harvesting old satisfied links as the chain crosses them. Fewer moves/harvest,
#           but a MIXED-resource optimizer (yields Hay+Wood+Carrot together, not one crop).
# COMPANION_CROP picks the seed plant for chain mode; the chain then wanders across types.
COMPANION_CHAIN = False

# --- Auto companion farming ---
# WARNING — MEASURED SLOWER, KEEP OFF. A live A/B (2026-06-19, Wood, x160 Polyculture)
# found single-drone companion farming ~19x SLOWER than 32-drone monoculture:
# ~0.24M vs ~4.47M wood/sec. The x160 multiplier is only ~2.8x per drone, which cannot
# overcome monoculture's 32x parallelism. Companion would only win if parallelized across
# drones (a multi-strip chain — NOT built) or once Polyculture climbs several more levels
# (~x1024+). Kept off, for that future possibility / the verified mechanic.
#
# When True, the bot uses companion farming for a Hay/Wood/Carrot goal (replacing 32-drone
# monoculture) when num_unlocked(Polyculture) >= COMPANION_MIN_LEVEL. It slots in AFTER
# plant_decision()'s energy floor + prereq gating (steering unchanged; only the METHOD
# changes). Method is cost-driven: unlock costing >=2 of {Hay,Wood,Carrot} (Top_Hat) ->
# mixed chain; exactly 1 -> targeted triplet; all unlocks maxed -> chain. DEFAULT OFF.
COMPANION_AUTO = False

# Minimum Polyculture level (num_unlocked(Unlocks.Polyculture)) at which COMPANION_AUTO
# would kick in. Multiplier = 5 * 2**level (level 0 = x5 ... level 5 = x160). Set high
# because companion LOSES badly to monoculture at today's levels (see warning above) — the
# single-drone multiplier would need to be ~32x the per-harvest base to break even, i.e.
# many more Polyculture levels. Moot while COMPANION_AUTO is False.
COMPANION_MIN_LEVEL = 5

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

# Max fertilizer applications to spend ripening a single pumpkin tile in place.
# Each use adds +2s of growth; a handful matures a tile so neighbours finish
# together and merge into giant pumpkins. Only used WHILE fertilizer is in stock -
# with no fertilizer the bot does not block-wait at all (the tile grows on its own
# across passes). Lower = move on sooner; raise = ripen more tiles in place.
PUMPKIN_MAX_WAIT = 100

# --- Bones / Dinosaur snake farming ---
# Bones come from wearing Hats.Dinosaur_Hat and growing a snake: eat apples (each
# costs 64 Cactus) to grow a tail, then unequip to cash out length**2 Items.Bone.
# It's a single-drone, full-farm takeover (clears the farm), so it's throttled.

# Don't start a bones run unless Cactus stock is at least this high (apples cost
# 64 Cactus each; a run eats roughly one apple per tail segment).
MIN_CACTUS_FOR_BONES = 100000

# Throttle: run bones at most once per this many outer loops.
BONES_LOOP_INTERVAL = 10

# Target snake tail length (= apples eaten) per bones run. farm_bones() sweeps the
# safe Hamiltonian cycle counting apples via measure() and cashes out at EXACTLY this
# tail (bones_step stops moving once reached). Bones = ~multiplier * tail**2 (live-
# calibrated ~40x, likely the Polyculture level), so tail 900 -> ~32M bones. Live
# test: self-collision happens at tail ~1023 (the 1024-tile field), so 900 leaves a
# ~123-tile margin. Keep under ~950; collision halts the whole bot. The run is a long
# single-drone field takeover (~190 laps) but rare (throttled). Higher = more bones.
BONES_TARGET_TAIL = 900

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
