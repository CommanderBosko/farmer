#!/usr/bin/env python3
"""Regenerate bench_main.py from main.py.

bench_main is a terminating twin of main used as the simulate() target for the
steady-state no-starvation harness. It shares main's ENTIRE strategy verbatim
(everything above "# --- Main Execution ---") and only swaps the bottom: instead
of `while True:` it runs the same per-iteration logic for a fixed op budget,
tracks the min/final of each tracked resource, and quick_print()s a verdict that
lands in output.txt.

This generator is what keeps bench_main from drifting: run it (or /bench) after
any change to main.py and the twin is rebuilt from the current strategy.

Usage:  python3 gen_bench_main.py
"""
import pathlib

ROOT = pathlib.Path(__file__).parent
MARKER = "# --- Main Execution ---"

main_src = (ROOT / "main.py").read_text()
if MARKER not in main_src:
    raise SystemExit("marker not found in main.py: " + MARKER)

head = main_src.split(MARKER)[0]

# --- bench harness bottom (game-Python: no kwargs / ternaries / comprehensions) ---
BOTTOM = '''# --- Steady-state no-starvation benchmark (generated; edit gen_bench_main.py) ---
# Runs main's real strategy from the simulate() starting state for a fixed op
# budget, tracking each resource's minimum so net drains and stuck-at-zero
# resources (e.g. Bones) are visible. Reports init/min/final + verdict to
# output.txt. run_time is returned to the caller as a secondary signal.
#
# The budget is a plain loop count (not get_op_count/get_time): those are gated
# behind unlocks that the simulate() snapshot can't always convey, so they error
# in-sim. loop_counter needs no unlock.
MAX_LOOPS = 20

clear()
# change_hat() is intentionally omitted: hats are NOT part of the Unlocks enum,
# so the simulate() unlocks snapshot can't convey them and change_hat() errors
# in-sim ("must be unlocked first"). The harness runs hatless — a minor,
# documented yield divergence from production.

update_amounts()
bones = num_items(Items.Bone)

init_hay = hay
init_wood = wood
init_carrot = carrot
init_pumpkin = pumpkin
init_cactus = cactus
init_gold = gold
init_bones = bones

min_hay = hay
min_wood = wood
min_carrot = carrot
min_pumpkin = pumpkin
min_cactus = cactus
min_gold = gold
min_bones = bones

while loop_counter < MAX_LOOPS:
    loop_counter += 1

    update_amounts()
    bones = num_items(Items.Bone)

    if hay < min_hay:
        min_hay = hay
    if wood < min_wood:
        min_wood = wood
    if carrot < min_carrot:
        min_carrot = carrot
    if pumpkin < min_pumpkin:
        min_pumpkin = pumpkin
    if cactus < min_cactus:
        min_cactus = cactus
    if gold < min_gold:
        min_gold = gold
    if bones < min_bones:
        min_bones = bones

    auto_unlocks()
    crop_choice = plant_decision()

    if crop_choice == Items.Cactus:
        farm_cactus()
    elif crop_choice == Items.Weird_Substance:
        farm_maze()
    elif crop_choice == Items.Power:
        farm_sunflower()
    elif crop_choice == Items.Bone:
        # Bones can't be farmed in-sim (the dino hat errors); skip but advance the
        # throttle so the rest of the rotation still runs. Validate bones LIVE.
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

update_amounts()
bones = num_items(Items.Bone)

quick_print("=== BENCH steady-state result ===")
quick_print("max_loops " + str(MAX_LOOPS) + "  loops_run " + str(loop_counter))
quick_print("hay     init " + str(init_hay) + "  min " + str(min_hay) + "  final " + str(hay))
quick_print("wood    init " + str(init_wood) + "  min " + str(min_wood) + "  final " + str(wood))
quick_print("carrot  init " + str(init_carrot) + "  min " + str(min_carrot) + "  final " + str(carrot))
quick_print("pumpkin init " + str(init_pumpkin) + "  min " + str(min_pumpkin) + "  final " + str(pumpkin))
quick_print("cactus  init " + str(init_cactus) + "  min " + str(min_cactus) + "  final " + str(cactus))
quick_print("gold    init " + str(init_gold) + "  min " + str(min_gold) + "  final " + str(gold))
quick_print("bones   init " + str(init_bones) + "  min " + str(min_bones) + "  final " + str(bones))

# Starvation = a tracked resource ENDED empty (final == 0) -> the hard
# set-and-forget failure, so it drives PASS/FAIL. Resources that merely spent
# down (final < init, but still > 0) are a non-fatal WATCH list (the bot draws
# down its highest stock to top up the lowest). final==0 (not min==0) avoids
# falsely flagging a resource that grows up from a zero start. Bones is EXCLUDED
# from PASS/FAIL: it can't be farmed in-sim (dino hat errors) so it's validated
# live, not here; min/final are still reported above for reference.
starved = ""
if hay == 0:
    starved = starved + " hay"
if wood == 0:
    starved = starved + " wood"
if carrot == 0:
    starved = starved + " carrot"
if pumpkin == 0:
    starved = starved + " pumpkin"
if cactus == 0:
    starved = starved + " cactus"
if gold == 0:
    starved = starved + " gold"

watch = ""
if hay < init_hay and hay > 0:
    watch = watch + " hay"
if wood < init_wood and wood > 0:
    watch = watch + " wood"
if carrot < init_carrot and carrot > 0:
    watch = watch + " carrot"
if pumpkin < init_pumpkin and pumpkin > 0:
    watch = watch + " pumpkin"
if cactus < init_cactus and cactus > 0:
    watch = watch + " cactus"
if gold < init_gold and gold > 0:
    watch = watch + " gold"

quick_print("bones: not farmable in-sim (dino hat) - validate live")

if watch != "":
    quick_print("WATCH (spent down, above zero):" + watch)

if starved == "":
    quick_print("VERDICT: PASS - no tracked resource ended empty")
else:
    quick_print("VERDICT: FAIL - ended empty:" + starved)
'''

(ROOT / "bench_main.py").write_text(head + BOTTOM)
print("wrote bench_main.py (" + str(len(head + BOTTOM)) + " bytes)")
