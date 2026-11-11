#!/usr/bin/env python3
"""Separate scoring of committed blind predictions against hidden synthetic truth.
Only run AFTER predictions.json and its hash have been written.
Do not mislabel these native-source samples as blockchain transactions.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def check_sha256(path, sha_path):
    raw = Path(sha_path).read_text(encoding="utf-8").strip().split()
    if not raw or len(raw[0]) != 64:
        raise ValueError("prediction commitment file invalid")
    got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if raw[0] != got:
        raise ValueError("BLIND_PREDICTION_COMMITMENT_MISMATCH")
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--seal", required=True)
    ap.add_argument("--truth", required=True)
    ap.add_argument("--observer", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    committed_hash = check_sha256(args.predictions, args.seal)
    blind = json.loads(Path(args.predictions).read_text(encoding="utf-8"))
    if blind["ground_truth_used"] is not False:
        raise ValueError("not a blind analysis")
    if hashlib.sha256(Path(args.observer).read_bytes()).hexdigest() != blind["observer_sha256"]:
        raise ValueError("observer data not the same as prediction data")

    public_rows = {}
    with Path(args.observer).open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["scenario"], int(row["sequence"]))
            if key in public_rows:
                raise ValueError("duplicate public row")
            public_rows[key] = set(map(int, row["anonymity_set"].split("|")))

    by_scenario = defaultdict(list)
    seen = set()
    with Path(args.truth).open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        expected = ["scenario", "sequence", "actual_receivers", "kind", "preferred_receiver"]
        if rd.fieldnames != expected:
            raise ValueError("unexpected ground-truth schema")
        for row in rd:
            key = (row["scenario"], int(row["sequence"]))
            if key in seen or key not in public_rows:
                raise ValueError("unmatched/duplicate ground-truth row")
            seen.add(key)
            recips = list(map(int, filter(None, row["actual_receivers"].split("|"))))
            if not set(recips) <= public_rows[key]:
                raise ValueError("a genuine receiver missing from set")
            if row["kind"] == "zero_only" and recips:
                raise ValueError("zero-only observation claims a receiver")
            if row["kind"] == "payment" and len(recips) != 1:
                raise ValueError("single transfer inconsistent")
            if row["kind"] == "multi_receiver" and len(recips) != 2:
                raise ValueError("multi-transfer inconsistent")
            by_scenario[key[0]].append({
                "sequence": key[1],
                "receivers": recips,
                "kind": row["kind"],
                "preferred_receiver": row["preferred_receiver"],
            })
    if seen != set(public_rows):
        raise ValueError("missing ground-truth rows")

    outcomes = {}
    for name, obj in blind["results"].items():
        rows = sorted(by_scenario[name], key=lambda x: x["sequence"])
        if len(rows) != 500 or [x["sequence"] for x in rows] != list(range(1,501)):
            raise ValueError("nonstandard experiment length")
        expected_pref = set(x["preferred_receiver"] for x in rows)
        if len(expected_pref) != 1:
            raise ValueError("preferred receiver changed across run")
        pref = next(iter(expected_pref))
        preferred = int(pref) if pref else None
        kinds = Counter(row["kind"] for row in rows)
        truth_counts = Counter(c for row in rows for c in row["receivers"])
        prefix = obj["prefixes"]
        stages = {}
        for count in (25, 50, 100, 200, 500):
            claim = prefix[str(count)]
            stages[str(count)] = {
                "predicted_top": claim["top_candidate"],
                "predicted_signal": claim["reject_balanced_model_at_fwer_0_05"],
                "matches_preferred": (claim["top_candidate"] == preferred)
                if preferred is not None else None,
            }
        outcomes[name] = {
            "known_preferred_receiver": preferred,
            "total_observations": len(rows),
            "genuine_receiver_inclusions": sum(len(x["receivers"]) for x in rows),
            "traffic_kinds": dict(sorted(kinds.items())),
            "true_receiver_counts": {str(k):v for k,v in sorted(truth_counts.items())},
            "prediction_at_500": prefix["500"]["top_candidate"],
            "prediction_matches_preferred_at_500": (
                prefix["500"]["top_candidate"] == preferred if preferred is not None else None
            ),
            "balanced_null_rejected": prefix["500"]["reject_balanced_model_at_fwer_0_05"],
            "prefix_comparisons": stages,
        }

    out = {
        "evidence_class": "NATIVE_SOURCE_FUNCTION_SYNTHETIC_TRAFFIC_OFFLINE_SCORING",
        "prediction_commitment_sha256": committed_hash,
        "truth_sha256": hashlib.sha256(Path(args.truth).read_bytes()).hexdigest(),
        "observer_sha256": blind["observer_sha256"],
        "all_public_rows_matched_to_truth": True,
        "total_observations": len(public_rows),
        "outcomes": outcomes,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("GROUND_TRUTH_SCORING_COMPLETE")
    for name, r in outcomes.items():
        print(f"{name}: preferred={r['known_preferred_receiver']} "
              f"prediction={r['prediction_at_500']} "
              f"match={r['prediction_matches_preferred_at_500']} "
              f"null_rejected={r['balanced_null_rejected']}")
    print("PREDICTION_COMMITMENT_VERIFIED")
    print("PUBLIC_PRIVATE_ROW_RECONCILIATION_PASS")


if __name__ == "__main__":
    main()
