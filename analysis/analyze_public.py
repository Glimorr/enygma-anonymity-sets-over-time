#!/usr/bin/env python3
"""Public-observer-only analysis of pinned Rayls native anonymity-set samples.

This module intentionally does not accept or read a ground-truth path.
Evidence class: SOURCE-LEVEL synthetic traffic, NOT private-chain receipts.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


PREFIXES = (25, 50, 100, 200, 500)
ALPHA_TEN_TESTS = 0.005


def binomial_upper_tail(n, threshold, p):
    if threshold <= 0:
        return 1.0
    if threshold > n:
        return 0.0
    if p >= 1:
        return 1.0 if threshold <= n else 0.0
    if p <= 0:
        return 0.0
    logp = math.log(p)
    logq = math.log1p(-p)
    terms = []
    for k in range(threshold, n + 1):
        a = math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
        terms.append(a + k * logp + (n - k) * logq)
    m = max(terms)
    return min(1.0, math.exp(m) * math.fsum(math.exp(z - m) for z in terms))


def wilson95(x, n):
    z = 1.959963984540054
    p = x / n
    denominator = 1 + z * z / n
    midpoint = (p + z * z / (2 * n)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denominator
    return [round(max(0, midpoint - margin), 6), round(min(1, midpoint + margin), 6)]


def score(rows, n_banks, k):
    sender = 1001
    possible = list(range(1002, 1001 + n_banks))
    counts = Counter()
    for member_ids in rows:
        counts.update(i for i in member_ids if i != sender)
    ranking = sorted(possible, key=lambda i: (-counts[i], i))
    top, second = ranking[0], ranking[1]
    total = len(rows)
    pnull = (k - 1) / (n_banks - 1)
    p_family = min(1.0, (n_banks - 1) * binomial_upper_tail(total, counts[top], pnull))
    return {
        "n_observations": total,
        "top_candidate": top,
        "runner_up": second,
        "top_appearance_count": counts[top],
        "runner_up_count": counts[second],
        "top_membership_fraction": round(counts[top] / total, 6),
        "runner_membership_fraction": round(counts[second] / total, 6),
        "top_wilson95": wilson95(counts[top], total),
        "runner_wilson95": wilson95(counts[second], total),
        "null_expected_membership_fraction": round(pnull, 6),
        "binomial_max_test_p_family_bound": round(p_family, 12),
        "reject_balanced_model_at_fwer_0_05": p_family < ALPHA_TEN_TESTS,
        "all_counts": {str(x): counts[x] for x in possible},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--observer", required=True)
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    observer_bytes = Path(args.observer).read_bytes()
    meta_bytes = Path(args.metadata).read_bytes()
    meta = json.loads(meta_bytes)
    if meta["evidence_type"] != "NATIVE_SOURCE_FUNCTION_WITH_SYNTHETIC_TRAFFIC":
        raise ValueError("evidence type mismatch")
    scenarios = {x["scenario"]: x for x in meta["scenarios"]}
    records = defaultdict(list)
    with Path(args.observer).open(newline="", encoding="utf-8") as fd:
        rd = csv.DictReader(fd)
        required = {"scenario", "sequence", "sender_chain", "anonymity_set"}
        if set(rd.fieldnames or []) != required:
            raise ValueError("unexpected observer-data columns")
        for row in rd:
            scenario = row["scenario"]
            if scenario not in scenarios:
                raise ValueError("unknown scenario")
            spec = scenarios[scenario]
            n = int(spec["participants"])
            k = int(spec["k"])
            ids = [int(x) for x in row["anonymity_set"].split("|")]
            if row["sender_chain"] != "1001":
                raise ValueError("unexpected source chain")
            if len(ids) != k or len(set(ids)) != k or sorted(ids) != ids:
                raise ValueError("malformed anonymity set")
            if not set(ids) <= set(range(1001, 1001 + n)) or 1001 not in ids:
                raise ValueError("bad participant membership")
            records[scenario].append((int(row["sequence"]), ids))

    predictions = {}
    for scenario, spec in scenarios.items():
        rows = sorted(records[scenario], key=lambda x: x[0])
        if len(rows) != spec["observations"]:
            raise ValueError(f"missing or extra rows for {scenario}")
        if [s for s, _ in rows] != list(range(1, spec["observations"] + 1)):
            raise ValueError(f"non-contiguous sequence for {scenario}")
        arr = [member for _, member in rows]
        predictions[scenario] = {
            "participant_count": spec["participants"],
            "k": spec["k"],
            "traffic_model_hint": spec["traffic_model"],
            "prefixes": {
                str(count): score(arr[:count], spec["participants"], spec["k"])
                for count in PREFIXES
            },
        }

    result = {
        "claim_class": "NATIVE_SOURCE_FUNCTION_SYNTHETIC_TRAFFIC_BLIND_ANALYSIS",
        "ground_truth_used": False,
        "observer_sha256": hashlib.sha256(observer_bytes).hexdigest(),
        "metadata_sha256": hashlib.sha256(meta_bytes).hexdigest(),
        "preregistered_family_alpha": 0.05,
        "scenario_count": len(scenarios),
        "observation_count": sum(len(x) for x in records.values()),
        "results": predictions,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("BLIND_ANALYSIS_COMPLETE")
    for name, p in predictions.items():
        s = p["prefixes"]["500"]
        print(f"{name}: top={s['top_candidate']} count={s['top_appearance_count']}/500 "
              f"p_family={s['binomial_max_test_p_family_bound']} signal={s['reject_balanced_model_at_fwer_0_05']}")
    print("GROUND_TRUTH_NOT_READ")


if __name__ == "__main__":
    main()
