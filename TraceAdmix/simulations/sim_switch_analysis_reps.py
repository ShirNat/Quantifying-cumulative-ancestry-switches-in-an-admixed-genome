#!/usr/bin/env python3
import os, sys, argparse, csv
import numpy as np
import pandas as pd
import tskit, pyslim

UNKNOWN = -1
A0, A1  = 0, 1
UNSEEN  = -128 

def parse_args():
    ap = argparse.ArgumentParser(
        description="Compute mean ancestry-switch count for ONE generation."
    )
    ap.add_argument("--n", type=int, required=True, help="sample size: uses n_<n>/rep_<rep>/...")
    ap.add_argument("--rep", type=int, required=True, help="replicate index (e.g. 0..9)")
    ap.add_argument("--gen", type=int, required=True, help="absolute SLiM generation to process (e.g. 1905)")
    ap.add_argument("--start-gen", type=int, required=True,
                    help="SLiM generation just BEFORE admixture (used for relative time and CSV index)")
    ap.add_argument("--admix-pop-id", type=int, default=2, help="admixed population ID in SLiM/tskit")
    ap.add_argument("--tree-path", default="tree_outputs",
                    help="root dir containing n_<n>/rep_<rep>/gen_<gen>.trees")
    ap.add_argument("--out-dir", default="obs_switches", help="output directory for CSV")
    ap.add_argument("--heartbeat", type=int, default=0, help="print every this many trees (0 = silent)")
    ap.add_argument("--force", action="store_true", help="write even if this generation is already in CSV")
    return ap.parse_args()

def mean_switches_for_generation(ts: tskit.TreeSequence,
                                      is_remembered: np.ndarray,
                                      nodes_arr: np.ndarray,
                                      heartbeat: int) -> float:
    # Count ancestry switches per sample by walking to first remembered ancestor on each tree.
    node_individual = ts.tables.nodes.individual  # node -> individual or -1
    prev   = np.full(len(nodes_arr), UNKNOWN, dtype=np.int8)
    counts = np.zeros(len(nodes_arr), dtype=np.int32)
    
    for t_idx, tree in enumerate(ts.trees()):
        if heartbeat and (t_idx + 1) % heartbeat == 0:
            frac = 100 * (t_idx + 1) / ts.num_trees
            print(f"  processed {t_idx + 1}/{ts.num_trees} trees ({frac:.2f}%)",
                  file=sys.stderr, flush=True)

        parent = tree.parent
        anc_cache: dict[int, int] = {}

        def get_anc(u: int) -> int:
            path = []
            cur = u
            while cur != tskit.NULL:
                cached = anc_cache.get(cur, UNSEEN)
                if cached != UNSEEN:
                    anc = cached
                    break
                ind = node_individual[cur]
                if ind != tskit.NULL and is_remembered[ind]:
                    pop = ts.individual(ind).population
                    if pop == tskit.NULL:  # fallback for older metadata
                        pop = ts.node(cur).population
                    anc = A0 if pop == 0 else (A1 if pop == 1 else UNKNOWN)
                    break
                path.append(cur)
                cur = parent(cur)
            else:
                anc = UNKNOWN
            for n in path:
                anc_cache[n] = anc
            return anc

        for j, u in enumerate(nodes_arr):
            anc = get_anc(u)
            if anc != UNKNOWN:
                if prev[j] != UNKNOWN and anc != prev[j]:
                    counts[j] += 1
                prev[j] = anc
            # if UNKNOWN: keep prev as-is

    return float(counts.mean()) if len(counts) else 0.0

def main():
    args = parse_args()

    # Tree path
    tree_dir = os.path.join(args.tree_path, f"n_{args.n}", f"rep_{args.rep}")
    path = os.path.join(tree_dir, f"gen_{args.gen}.trees")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing tree file: {path}")
    print(f"Loading tree file: {os.path.abspath(path)}", file=sys.stderr, flush=True)

    # Output path organized by n
    out_subdir = os.path.join(args.out_dir, f"n_{args.n}")
    os.makedirs(out_subdir, exist_ok=True)
    out_csv = os.path.join(out_subdir, f"observed_switches_rep_{args.rep}.csv")

    # CSV index for this generation
    gen_idx = args.gen - (args.start_gen + 1)

    # Skip if already present (unless --force)
    if os.path.exists(out_csv) and not args.force:
        try:
            prev_gen = pd.read_csv(out_csv, usecols=["generation"])["generation"]
            if (prev_gen == gen_idx).any():
                print(f"[rep {args.rep}] gen {args.gen} -> already in {out_csv}; skipping (use --force to overwrite)",
                      file=sys.stderr, flush=True)
                return
        except Exception as e:
            print(f"[warn] Could not read existing CSV ({e}); proceeding…", file=sys.stderr, flush=True)

    print(f"Starting single-gen run | rep={args.rep} n={args.n} gen={args.gen} "
          f"(idx={gen_idx}) | dir={tree_dir}", file=sys.stderr, flush=True)

    # Load and prep trees
    ts = pyslim.update(tskit.load(path))
    t_rel = args.gen - args.start_gen

    rem = pyslim.individuals_alive_at(ts, time=t_rel, remembered_stage="late")
    if len(rem) == 0:
        raise RuntimeError(f"No remembered founders at t_rel={t_rel} in {path}")

    is_remembered = np.zeros(ts.num_individuals, dtype=bool)
    is_remembered[np.asarray(rem, dtype=np.int64)] = True

    node_ids = ts.samples(population=args.admix_pop_id)
    if len(node_ids) == 0:
        raise RuntimeError(f"No samples in population {args.admix_pop_id} at gen {args.gen}")
    nodes_arr = np.asarray(node_ids, dtype=np.int64)

    # Compute number of switches
    mean_sw = mean_switches_for_generation(ts, is_remembered, nodes_arr, args.heartbeat)
    row = {"generation": gen_idx, "observed_switches": mean_sw}

    # Append to CSV (header if new)
    write_header = not os.path.exists(out_csv)
    with open(out_csv, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["generation", "observed_switches"])
        if write_header:
            w.writeheader()
        w.writerow(row)
        f.flush(); os.fsync(f.fileno())

    print(f"[rep {args.rep}] wrote gen {gen_idx} -> {out_csv}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()