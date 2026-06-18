import config

# --- Configuration ---
FOCUS_CROP_MAP = {
	"Hay": Items.Hay,
	"Wood": Items.Wood,
	"Carrot": Items.Carrot,
	"Pumpkin": Items.Pumpkin,
	"Cactus": Items.Cactus,
	"Maze": Items.Weird_Substance,
	"Sunflower": Items.Power,
	"Bones": Items.Bone,
}

# --- Global State ---
hay = 0
wood = 0
carrot = 0
pumpkin = 0
cactus = 0
weird_substance = 0
fertilizer = 0
water = 0
power = 0
gold = 0
bones = 0
loop_counter = 0 # New: Global counter for loop iterations
last_bones_loop = 0 # Loop index of the last bones run (throttle for farm_bones)

# Bone snake state: tail length (= apples eaten) and the current apple position,
# updated per move by bones_step() so farm_bones() can stop at an exact tail length.
bone_tail = 0
bone_apple_x = 0
bone_apple_y = 0

# Map Items enum to readable names for printing
ITEM_NAMES = {
	Items.Hay: "Hay",
	Items.Wood: "Wood",
	Items.Carrot: "Carrot",
	Items.Pumpkin: "Pumpkin",
	Items.Cactus: "Cactus",
	Items.Weird_Substance: "Weird_Substance",
	Items.Power: "Power",
	Items.Gold: "Gold",
	Items.Bone: "Bones",
}
# New: Map Unlocks enum to readable names
UNLOCK_NAMES = {
	# Tier 1 – Hay-cost unlocks
	Unlocks.Loops: "Loops",
	Unlocks.Plant: "Plant",
	Unlocks.Hats: "Hats",
	Unlocks.Speed: "Speed",
	Unlocks.Senses: "Senses",
	Unlocks.Grass: "Grass",
	# Tier 2 – Wood-cost unlocks
	Unlocks.Carrots: "Carrots",
	Unlocks.Fertilizer: "Fertilizer",
	Unlocks.Watering: "Watering",
	# Tier 3 – Carrot-cost unlocks
	Unlocks.Variables: "Variables",
	Unlocks.Functions: "Functions",
	Unlocks.Import: "Import",
	Unlocks.Lists: "Lists",
	Unlocks.Sunflowers: "Sunflowers",
	Unlocks.Trees: "Trees",
	Unlocks.Pumpkins: "Pumpkins",
	# Tier 4 – Pumpkin-cost unlocks
	Unlocks.Expand: "Expand",
	Unlocks.Utilities: "Utilities",
	Unlocks.Timing: "Timing",
	Unlocks.Costs: "Costs",
	Unlocks.Dictionaries: "Dictionaries",
	Unlocks.Polyculture: "Polyculture",
	Unlocks.Auto_Unlock: "Auto_Unlock",
	Unlocks.Cactus: "Cactus",
	# Tier 5 – Cactus-cost unlocks
	Unlocks.Dinosaurs: "Dinosaurs",
	Unlocks.Mazes: "Mazes",
}

# New: Prerequisite mapping for stock checks
PREREQUISITES = {
	Items.Wood: [(Items.Hay, config.MIN_PREREQ_STOCK)],
	Items.Carrot: [(Items.Hay, config.MIN_PREREQ_STOCK), (Items.Wood, config.MIN_PREREQ_STOCK)],
	Items.Pumpkin: [(Items.Carrot, config.MIN_PREREQ_STOCK)],
	Items.Cactus: [(Items.Pumpkin, config.MIN_PREREQ_STOCK)],
	Items.Weird_Substance: [(Items.Cactus, config.MIN_PREREQ_STOCK)],
}


# --- Functions ---

def get_amount(item):
	if item == Items.Hay:
		return hay
	if item == Items.Wood:
		return wood
	if item == Items.Carrot:
		return carrot
	if item == Items.Pumpkin:
		return pumpkin
	if item == Items.Cactus:
		return cactus
	if item == Items.Weird_Substance:
		return weird_substance
	if item == Items.Fertilizer:
		return fertilizer
	if item == Items.Water:
		return water
	if item == Items.Power:
		return power
	if item == Items.Gold:
		return gold
	if item == Items.Bone:
		return bones
	return 0

def get_next_unlock_goal():
	unlocks_to_check = [
		# Hay-cost unlocks (cheapest first)
		(Unlocks.Loops, Items.Hay),
		(Unlocks.Plant, Items.Hay),
		(Unlocks.Hats, Items.Hay),
		(Unlocks.Speed, Items.Hay),
		(Unlocks.Senses, Items.Hay),
		# Wood-cost unlocks
		(Unlocks.Grass, Items.Wood),
		(Unlocks.Carrots, Items.Wood),
		(Unlocks.Fertilizer, Items.Wood),
		(Unlocks.Watering, Items.Wood),
		# Carrot-cost unlocks
		(Unlocks.Variables, Items.Carrot),
		(Unlocks.Functions, Items.Carrot),
		(Unlocks.Import, Items.Carrot),
		(Unlocks.Lists, Items.Carrot),
		(Unlocks.Sunflowers, Items.Carrot),
		(Unlocks.Trees, Items.Hay),
		(Unlocks.Pumpkins, Items.Carrot),
		# Pumpkin-cost unlocks
		(Unlocks.Utilities, Items.Pumpkin),
		(Unlocks.Timing, Items.Pumpkin),
		(Unlocks.Costs, Items.Pumpkin),
		(Unlocks.Dictionaries, Items.Pumpkin),
		(Unlocks.Polyculture, Items.Pumpkin),
		(Unlocks.Auto_Unlock, Items.Pumpkin),
		(Unlocks.Expand, Items.Pumpkin),
		# Cactus-cost unlocks
		(Unlocks.Cactus, Items.Pumpkin),
		(Unlocks.Dinosaurs, Items.Cactus),
		(Unlocks.Mazes, Items.Cactus),
	]

	cheapest_goal = (None, None)
	min_cost = 10 ** 15

	for unlock_item, required_item in unlocks_to_check:
		cost = get_cost(unlock_item)
		
		# If the unlock is available to be purchased and costs the expected item
		if cost and required_item in cost:
			required_amount = cost[required_item]

			# If we can't afford it yet AND it's the cheapest so far
			shortfall = required_amount - get_amount(required_item)
			if shortfall > 0 and shortfall < min_cost:
				min_cost = shortfall
				cheapest_goal = (required_item, UNLOCK_NAMES[unlock_item])

	return cheapest_goal

def plant_decision():
	# Helper to check prerequisite stock
	def check_stock(crop_to_plant):
		progress = True
		while progress:
			progress = False
			if crop_to_plant in PREREQUISITES:
				for prereq_item, required_amount in PREREQUISITES[crop_to_plant]:
					if get_amount(prereq_item) < required_amount:
						crop_to_plant = prereq_item
						progress = True
						break
		return crop_to_plant

	if config.FOCUS_CROP and config.FOCUS_CROP in FOCUS_CROP_MAP:
		return FOCUS_CROP_MAP[config.FOCUS_CROP] # Focus mode bypasses stock checks

	# Power doubles drone speed — replenish before pursuing other goals.
	# Sunflower seeds are bought with Carrots, so only enter sunflower mode when we
	# hold enough carrots to sustain it; otherwise fall through and farm carrots first.
	# Without this guard, draining carrots in sunflower mode deadlocks: no carrots ->
	# can't plant sunflowers -> no power -> never leaves sunflower mode.
	if num_unlocked(Unlocks.Sunflowers) > 0 and power < config.MIN_POWER_STOCK and carrot >= config.MIN_CARROT_FOR_SUNFLOWER:
		return Items.Power

	# Bones (single-drone snake): farm when bones is the lowest tracked stock,
	# throttled to once per BONES_LOOP_INTERVAL loops (each run is a long full-farm
	# takeover), and only with a Cactus buffer since apples cost 64 Cactus each.
	if num_unlocked(Unlocks.Dinosaurs) > 0 and cactus >= config.MIN_CACTUS_FOR_BONES:
		if loop_counter - last_bones_loop >= config.BONES_LOOP_INTERVAL:
			if bones <= hay and bones <= wood and bones <= carrot and bones <= pumpkin and bones <= cactus:
				return Items.Bone

	# Prioritize maze runs when gold is below the manual-upgrade target
	if config.MIN_GOLD_STOCK > 0 and gold < config.MIN_GOLD_STOCK and num_unlocked(Unlocks.Mazes) > 0:
		n_substance = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
		if weird_substance >= n_substance:
			return Items.Weird_Substance

	goal_item, unlock_name = get_next_unlock_goal()
	if goal_item:
		return check_stock(goal_item) # Check stock for the goal item

	# Run a maze when we've stockpiled enough weird substance
	if num_unlocked(Unlocks.Mazes) > 0 and weird_substance >= config.MIN_WEIRD_SUBSTANCE_STOCK:
		return Items.Weird_Substance

	# Fallback logic: plant what you have the least of, but check prerequisites.
	# Branches are ordered by ascending priority (Hay lowest, Cactus highest).
	# Each branch uses <= so tied crops fall through to the higher-priority branch,
	# meaning the last matching branch wins: Cactus > Pumpkin > Carrot > Wood > Hay.
	_hay = get_amount(Items.Hay)
	_wood = get_amount(Items.Wood)
	_carrot = get_amount(Items.Carrot)
	_pumpkin = get_amount(Items.Pumpkin)
	_cactus = get_amount(Items.Cactus)
	result = Items.Hay
	if _wood <= _hay and _wood <= _carrot and _wood <= _pumpkin and _wood <= _cactus:
		result = check_stock(Items.Wood)
	if _carrot <= _hay and _carrot <= _wood and _carrot <= _pumpkin and _carrot <= _cactus:
		result = check_stock(Items.Carrot)
	if _pumpkin <= _hay and _pumpkin <= _wood and _pumpkin <= _carrot and _pumpkin <= _cactus:
		result = check_stock(Items.Pumpkin)
	if _cactus <= _hay and _cactus <= _wood and _cactus <= _carrot and _cactus <= _pumpkin:
		result = check_stock(Items.Cactus)
	return result

def auto_unlocks():
	unlocks = [
		# Hay-cost unlocks (cheapest first)
		(Unlocks.Loops, Items.Hay, "Loops"),
		(Unlocks.Plant, Items.Hay, "Plant"),
		(Unlocks.Hats, Items.Hay, "Hats"),
		(Unlocks.Speed, Items.Hay, "Speed"),
		(Unlocks.Senses, Items.Hay, "Senses"),
		# Wood-cost unlocks
		(Unlocks.Grass, Items.Wood, "Grass"),
		(Unlocks.Carrots, Items.Wood, "Carrots"),
		(Unlocks.Fertilizer, Items.Wood, "Fertilizer"),
		(Unlocks.Watering, Items.Wood, "Watering"),
		# Carrot-cost unlocks
		(Unlocks.Variables, Items.Carrot, "Variables"),
		(Unlocks.Functions, Items.Carrot, "Functions"),
		(Unlocks.Import, Items.Carrot, "Import"),
		(Unlocks.Lists, Items.Carrot, "Lists"),
		(Unlocks.Sunflowers, Items.Carrot, "Sunflowers"),
		(Unlocks.Trees, Items.Hay, "Trees"),
		(Unlocks.Pumpkins, Items.Carrot, "Pumpkins"),
		# Pumpkin-cost unlocks
		(Unlocks.Utilities, Items.Pumpkin, "Utilities"),
		(Unlocks.Timing, Items.Pumpkin, "Timing"),
		(Unlocks.Costs, Items.Pumpkin, "Costs"),
		(Unlocks.Dictionaries, Items.Pumpkin, "Dictionaries"),
		(Unlocks.Polyculture, Items.Pumpkin, "Polyculture"),
		(Unlocks.Auto_Unlock, Items.Pumpkin, "Auto_Unlock"),
		(Unlocks.Expand, Items.Pumpkin, "Expand"),
		# Cactus-cost unlocks
		(Unlocks.Cactus, Items.Pumpkin, "Cactus"),
		(Unlocks.Dinosaurs, Items.Cactus, "Dinosaurs"),
		(Unlocks.Mazes, Items.Cactus, "Mazes"),
	]

	for unlock_item, required_item, name in unlocks:
		cost = get_cost(unlock_item)
		if cost and required_item in cost and get_amount(required_item) >= cost[required_item]:
			unlock(unlock_item)
			print("Unlocked the next level of " + name)
			update_amounts()

def update_amounts():
	global hay
	global wood
	global carrot
	global pumpkin
	global cactus
	global weird_substance
	global fertilizer
	global water
	global power
	global gold
	global bones
	hay = num_items(Items.Hay)
	wood = num_items(Items.Wood)
	carrot = num_items(Items.Carrot)
	pumpkin = num_items(Items.Pumpkin)
	cactus = num_items(Items.Cactus)
	weird_substance = num_items(Items.Weird_Substance)
	fertilizer = num_items(Items.Fertilizer)
	water = num_items(Items.Water)
	power = num_items(Items.Power)
	gold = num_items(Items.Gold)
	# Items.Bone only exists once Dinosaurs is unlocked; guard to avoid an error.
	if num_unlocked(Unlocks.Dinosaurs) > 0:
		bones = num_items(Items.Bone)
	else:
		bones = 0

def farm(crop_choice, x, y):
	if crop_choice == Items.Hay:
		harvest()
		if get_ground_type() != Grounds.Grassland:
			till()

	elif crop_choice == Items.Wood:
		harvest()
		if (x % 2 == 0 and y % 2 == 0) or (x % 2 == 1 and y % 2 == 1):
			if get_ground_type() != Grounds.Soil:
				till()
			if config.MIN_WATER_LEVEL > 0 and get_water() < config.MIN_WATER_LEVEL and get_amount(Items.Water) > 0:
				use_item(Items.Water)
			if get_entity_type() != Entities.Tree:
				till()
				if get_ground_type() != Grounds.Soil:
					till()
				plant(Entities.Tree)
		else:
			if get_amount(Items.Hay) <= get_amount(Items.Carrot):
				if get_ground_type() != Grounds.Grassland:
					till()
			else:
				if get_ground_type() != Grounds.Soil:
					till()
				if config.MIN_WATER_LEVEL > 0 and get_water() < config.MIN_WATER_LEVEL and get_amount(Items.Water) > 0:
					use_item(Items.Water)
				if get_entity_type() != Entities.Carrot:
					till()
					if get_ground_type() != Grounds.Soil:
						till()
					plant(Entities.Carrot)

	elif crop_choice == Items.Carrot:
		if can_harvest():
			harvest()
		if get_ground_type() != Grounds.Soil:
			till()
		if config.MIN_WATER_LEVEL > 0 and get_water() < config.MIN_WATER_LEVEL and get_amount(Items.Water) > 0:
			use_item(Items.Water)
		if get_entity_type() != Entities.Carrot:
			till()
			if get_ground_type() != Grounds.Soil:
				till()
			plant(Entities.Carrot)

	elif crop_choice == Items.Pumpkin:
		# Collect anything that ripened since the last pass.
		if can_harvest():
			harvest()
		if get_ground_type() != Grounds.Soil:
			till()
		# Sweep: an empty plot AND a dead pumpkin both fail this check (a dead pumpkin
		# is Entities.Dead_Pumpkin, not Entities.Pumpkin). plant() auto-replaces a dead
		# or ungrown pumpkin, so this single branch both fills empties and clears the
		# ~20% that die at maturity - every visit, so dead pumpkins can't pile up.
		# NEVER plant on a living pumpkin: that resets its growth (see pumpkin mega
		# mechanic). Gated by the carrot reserve - pumpkins cost 256 Carrot each.
		if get_entity_type() != Entities.Pumpkin:
			while get_water() < 1 and num_items(Items.Water) > 0:
				use_item(Items.Water)
			if num_items(Items.Carrot) >= config.MIN_CARROT_FOR_PUMPKIN:
				plant(Entities.Pumpkin)
		# Only block-wait while we HAVE fertilizer: a few +2s uses ripen a tile fast,
		# so neighbours finish together and merge into giants. With no fertilizer we do
		# NOT idle here - do_a_flip growth is far too slow, and idling makes the whole
		# pass crawl so dead pumpkins linger between sweeps. Instead we leave the tile
		# to grow on its own across passes and harvest/sweep it on a later visit.
		if num_items(Items.Fertilizer) > 0:
			pumpkin_iter = 0
			while not can_harvest():
				if pumpkin_iter >= config.PUMPKIN_MAX_WAIT:
					break
				if num_items(Items.Fertilizer) <= 0:
					break
				pumpkin_iter += 1
				use_item(Items.Fertilizer)
				# If it died mid-grow, replace it so we don't leave a dead tile.
				if get_entity_type() != Entities.Pumpkin:
					if num_items(Items.Carrot) >= config.MIN_CARROT_FOR_PUMPKIN:
						plant(Entities.Pumpkin)

def goto_sw():
	while get_pos_y() > 0:
		move(South)
	while get_pos_x() > 0:
		move(West)

def farm_grid(crop_choice, start_x, end_x):
	update_amounts()
	world_size = get_world_size()
	goto_sw()
	for i in range(start_x):
		move(East)
	for x in range(start_x, end_x):
		if (x - start_x) % 2 == 0:
			for y in range(world_size):
				farm(crop_choice, x, y)
				if y < world_size - 1:
					move(North)
		else:
			for y in range(world_size - 1, -1, -1):
				farm(crop_choice, x, y)
				if y > 0:
					move(South)
		if x < end_x - 1:
			move(East)

def plant_cactus_strip(start_x, end_x):
	world_size = get_world_size()
	goto_sw()
	for _ in range(start_x):
		move(East)
	for x in range(start_x, end_x):
		if (x - start_x) % 2 == 0:
			for y in range(world_size):
				if can_harvest():
					harvest()
				if get_ground_type() != Grounds.Soil:
					till()
				if get_entity_type() != Entities.Cactus:
					plant(Entities.Cactus)
				if y < world_size - 1:
					move(North)
		else:
			for y in range(world_size - 1, -1, -1):
				if can_harvest():
					harvest()
				if get_ground_type() != Grounds.Soil:
					till()
				if get_entity_type() != Entities.Cactus:
					plant(Entities.Cactus)
				if y > 0:
					move(South)
		if x < end_x - 1:
			move(East)

def wait_cactus_strip(start_x, end_x):
	world_size = get_world_size()
	all_ready = False
	while not all_ready:
		all_ready = True
		goto_sw()
		for _ in range(start_x):
			move(East)
		for x in range(start_x, end_x):
			if (x - start_x) % 2 == 0:
				for y in range(world_size):
					if not can_harvest():
						all_ready = False
					if y < world_size - 1:
						move(North)
			else:
				for y in range(world_size - 1, -1, -1):
					if not can_harvest():
						all_ready = False
					if y > 0:
						move(South)
			if x < end_x - 1:
				move(East)

def sort_cactus_rows(start_row, end_row):
	world_size = get_world_size()
	goto_sw()
	for _ in range(start_row):
		move(North)
	for row in range(start_row, end_row):
		for _ in range(world_size - 1):
			swapped = False
			for col in range(world_size - 1):
				if measure() > measure(East):
					swap(East)
					swapped = True
				move(East)
			for col in range(world_size - 1):
				move(West)
			if not swapped:
				break
		if row < end_row - 1:
			move(North)

def sort_cactus_cols(start_col, end_col):
	world_size = get_world_size()
	goto_sw()
	for _ in range(start_col):
		move(East)
	for col in range(start_col, end_col):
		for _ in range(world_size - 1):
			swapped = False
			for row in range(world_size - 1):
				if measure() > measure(North):
					swap(North)
					swapped = True
				move(North)
			for row in range(world_size - 1):
				move(South)
			if not swapped:
				break
		if col < end_col - 1:
			move(East)

def farm_cactus():
	world_size = get_world_size()
	num_drones = min(config.NUM_DRONES, world_size)
	base = world_size // num_drones
	remainder = world_size % num_drones

	# Plant
	drones = []
	cur = 0
	for i in range(num_drones - 1):
		if i < remainder:
			width = base + 1
		else:
			width = base
		drones.append(spawn_drone(plant_cactus_strip, cur, cur + width))
		cur = cur + width
	plant_cactus_strip(cur, world_size)
	for d in drones:
		wait_for(d)

	# Wait until all harvestable
	drones = []
	cur = 0
	for i in range(num_drones - 1):
		if i < remainder:
			width = base + 1
		else:
			width = base
		drones.append(spawn_drone(wait_cactus_strip, cur, cur + width))
		cur = cur + width
	wait_cactus_strip(cur, world_size)
	for d in drones:
		wait_for(d)

	# Sort rows
	drones = []
	cur = 0
	for i in range(num_drones - 1):
		if i < remainder:
			width = base + 1
		else:
			width = base
		drones.append(spawn_drone(sort_cactus_rows, cur, cur + width))
		cur = cur + width
	sort_cactus_rows(cur, world_size)
	for d in drones:
		wait_for(d)

	# Sort columns
	drones = []
	cur = 0
	for i in range(num_drones - 1):
		if i < remainder:
			width = base + 1
		else:
			width = base
		drones.append(spawn_drone(sort_cactus_cols, cur, cur + width))
		cur = cur + width
	sort_cactus_cols(cur, world_size)
	for d in drones:
		wait_for(d)

	# Harvest cascade from SW corner
	goto_sw()
	harvest()

def farm_maze():
	# Determine how much Weird_Substance to use for this maze
	n_substance = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)

	# Only attempt if we have enough Weird_Substance
	if get_amount(Items.Weird_Substance) < n_substance:
		return

	# Plant a bush on grassland (no tilling needed) and grow a maze from it
	clear()
	if get_entity_type() != Entities.Bush:
		if get_ground_type() != Grounds.Grassland:
			till()
		plant(Entities.Bush)
	use_item(Items.Weird_Substance, n_substance)

	# Wall-following algorithm to navigate to the treasure
	# Directions cycle: North=0, East=1, South=2, West=3
	DIRS = [North, East, South, West]
	facing = 0  # start facing North
	max_steps = get_world_size() * get_world_size() * 4
	steps = 0

	while get_entity_type() != Entities.Treasure:
		if steps >= max_steps:
			break  # safety valve — bail out if maze takes too long
		steps += 1
		# Try to turn left and move (left-hand wall following)
		left = (facing - 1) % 4
		if move(DIRS[left]):
			facing = left
		elif move(DIRS[facing]):
			pass  # moved straight, keep facing
		else:
			# Turn right
			facing = (facing + 1) % 4

	# Harvest only if we actually reached the treasure
	if get_entity_type() == Entities.Treasure:
		harvest()

	# Reset farm to a clean farmable state regardless of outcome
	clear()

def bones_step(direction):
	# One snake move along the Hamiltonian cycle, counting apples as we go: if the
	# head lands on the tracked apple it was eaten, so grow the tail and re-measure
	# the next one. measure() returns the next apple position (one apple at a time).
	global bone_tail
	global bone_apple_x
	global bone_apple_y
	# Precise stop: once the target tail is reached, stop moving so the rest of the
	# lap is no-ops and we cash out at EXACTLY the target. Without this the per-lap
	# target check overshoots by a whole lap (~40+ apples near a full board), which
	# can blow past the ~1023 self-collision point and kill the bot.
	if bone_tail >= config.BONES_TARGET_TAIL:
		return
	move(direction)
	if get_pos_x() == bone_apple_x and get_pos_y() == bone_apple_y:
		bone_tail += 1
		bone_apple_x, bone_apple_y = measure()

def farm_bones():
	# Single-drone snake: wear the Dinosaur hat and sweep the field eating apples
	# (each costs 64 Cactus) until the tail reaches config.BONES_TARGET_TAIL, then
	# unequip to cash out ~Polyculture_multiplier * tail**2 as Items.Bone (live-
	# calibrated ~40x: tail 500 -> ~10M bones). Validated live (bench can't equip hats).
	#
	# Path = a Hamiltonian cycle with the bottom row (y=0) reserved as a return lane,
	# so it covers every tile and returns to (0,0); repeated laps grow the snake. The
	# tail trails behind on the cycle, so there is no self-collision until the tail
	# nearly fills the field (~1024 tiles). Requires an EVEN world size.
	global bone_tail
	global bone_apple_x
	global bone_apple_y
	n = get_world_size()
	if n % 2 != 0:
		return  # odd size: skip (would need set_world_size to make it even)
	clear()
	# The snake path is relative to the origin (0,0). In the main loop the drone is
	# left mid-field by the previous farm pass, so without this the snake starts
	# offset, tangles into its own tail, and dies (halting the whole bot).
	goto_sw()
	change_hat(Hats.Dinosaur_Hat)
	bone_apple_x, bone_apple_y = measure()
	bone_tail = 0
	# Safety valve: cap laps so a counter glitch can never grow the tail into the
	# collision zone (~380 laps fills the field). Reaching the target takes far fewer
	# laps (~2.7 apples/lap, so ~185 laps for tail 500); the cap only matters if the
	# apple count stalls. tail ~2.7*cap stays well under the field at cap=300.
	lap = 0
	while bone_tail < config.BONES_TARGET_TAIL and lap < 300:
		lap += 1
		bones_step(North)                # (0,0) -> (0,1): enter the comb
		for x in range(n):
			if x % 2 == 0:
				for k in range(n - 2):
					bones_step(North)
			else:
				for k in range(n - 2):
					bones_step(South)
			if x < n - 1:
				bones_step(East)
		bones_step(South)                # drop to the return lane (y=0)
		for k in range(n - 1):
			bones_step(West)             # run home along row 0 to (0,0)
	change_hat(Hats.Pumpkin_Hat)         # unequip -> cash out tail**2 (* multiplier)
	clear()                              # leave a clean field for the next crop

# A Sunflower_Seed costs up to 6 Carrots (see GetItemCosts in-game); plant() auto-buys
# the seed from Carrots. Only plant when we can afford the most expensive seed level —
# otherwise the game warns "Didn't have the required items to plant Entities.Sunflower"
# and the tile is left empty. num_items reads live inventory so it stays accurate as the
# strip consumes carrots cell by cell across drones.
MAX_SUNFLOWER_SEED_COST = 6

def plant_sunflower_cell():
	if num_items(Items.Carrot) >= MAX_SUNFLOWER_SEED_COST:
		plant(Entities.Sunflower)

def farm_sunflower_strip(start_x, end_x):
	world_size = get_world_size()
	goto_sw()
	for _ in range(start_x):
		move(East)
	for x in range(start_x, end_x):
		if (x - start_x) % 2 == 0:
			for y in range(world_size):
				if get_ground_type() != Grounds.Soil:
					till()
				if config.MIN_WATER_LEVEL > 0 and get_water() < config.MIN_WATER_LEVEL and get_amount(Items.Water) > 0:
					use_item(Items.Water)
				if get_entity_type() != Entities.Sunflower:
					if can_harvest():
						harvest()
					till()
					if get_ground_type() != Grounds.Soil:
						till()
					plant_sunflower_cell()
				elif can_harvest():
					harvest()
					if get_ground_type() != Grounds.Soil:
						till()
					plant_sunflower_cell()
				if y < world_size - 1:
					move(North)
		else:
			for y in range(world_size - 1, -1, -1):
				if get_ground_type() != Grounds.Soil:
					till()
				if config.MIN_WATER_LEVEL > 0 and get_water() < config.MIN_WATER_LEVEL and get_amount(Items.Water) > 0:
					use_item(Items.Water)
				if get_entity_type() != Entities.Sunflower:
					if can_harvest():
						harvest()
					till()
					if get_ground_type() != Grounds.Soil:
						till()
					plant_sunflower_cell()
				elif can_harvest():
					harvest()
					if get_ground_type() != Grounds.Soil:
						till()
					plant_sunflower_cell()
				if y > 0:
					move(South)
		if x < end_x - 1:
			move(East)

def farm_sunflower():
	world_size = get_world_size()
	num_drones = min(config.NUM_DRONES, world_size)
	base = world_size // num_drones
	remainder = world_size % num_drones
	drones = []
	cur = 0
	for i in range(num_drones - 1):
		if i < remainder:
			width = base + 1
		else:
			width = base
		drones.append(spawn_drone(farm_sunflower_strip, cur, cur + width))
		cur = cur + width
	farm_sunflower_strip(cur, world_size)
	for d in drones:
		wait_for(d)

# --- Main Execution ---

clear()
change_hat(Hats.Pumpkin_Hat)

while True:
	loop_counter += 1

	update_amounts()
	auto_unlocks()
	crop_choice = plant_decision()

	# Print goal occasionally based on config
	if config.PRINT_GOAL_INTERVAL and loop_counter % config.PRINT_GOAL_INTERVAL == 0:
		# Get goal info for printing
		goal_item, unlock_name = get_next_unlock_goal()

		if crop_choice in ITEM_NAMES:
			current_goal_name = ITEM_NAMES[crop_choice]
		else:
			current_goal_name = "Unknown Goal"

		status_message = "Current Goal: " + current_goal_name
		# Add unlock name to status if there is one
		if unlock_name and not config.FOCUS_CROP:
			status_message = status_message + " (for upgrading " + unlock_name + ")"

		quick_print('--------------------------------------------------------------------')
		quick_print(status_message)
		quick_print('--------------------------------------------------------------------')
	elif config.PRINT_GOAL_INTERVAL:
		quick_print('--------------------------------------------------------------------')


	if crop_choice == Items.Cactus:
		farm_cactus()
	elif crop_choice == Items.Weird_Substance:
		farm_maze()
	elif crop_choice == Items.Power:
		farm_sunflower()
	elif crop_choice == Items.Bone:
		farm_bones()
		last_bones_loop = loop_counter
	else:
		world_size = get_world_size()
		num_drones = min(config.NUM_DRONES, world_size)
		if num_drones > 1:
			base = world_size // num_drones
			remainder = world_size % num_drones
			drones = []
			cur = 0
			for i in range(num_drones - 1):
				if i < remainder:
					width = base + 1
				else:
					width = base
				drones.append(spawn_drone(farm_grid, crop_choice, cur, cur + width))
				cur = cur + width
			farm_grid(crop_choice, cur, world_size)
			for d in drones:
				wait_for(d)
		else:
			farm_grid(crop_choice, 0, world_size)

		if crop_choice == Items.Pumpkin:
			harvest()
