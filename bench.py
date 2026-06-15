# Steady-state no-starvation harness — RUNNER.
#
# Snapshots your current unlocks + items as the simulate() starting state, then
# runs bench_main (a terminating twin of main) for a fixed op budget. bench_main
# quick_print()s its per-resource verdict to output.txt, which is read directly
# off disk — this file's own run_time line is just a secondary signal.
#
# Run this in-game after (re)generating bench_main (python3 gen_bench_main.py).

unlocks = {}
for u in Unlocks:
	unlocks[u] = num_unlocked(u)

items = {}
for it in Items:
	items[it] = num_items(it)

glob = {}
seed = 1
speedup = 10000

run_time = simulate("bench_main", unlocks, items, glob, seed, speedup)
quick_print("outer: bench_main returned run_time = " + str(run_time))
