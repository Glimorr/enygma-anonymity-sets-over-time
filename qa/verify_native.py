#!/usr/bin/env python3
"""Independent completeness/integrity checks for the native Rayls W2 evidence.
Not an outside-consensus authenticator and not a blockchain verifier.
"""
import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def require(condition, message):
    if not condition:
        raise AssertionError(message)

def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check_seal(target, seal):
    expected = Path(seal).read_text().split()[0]
    actual = hash_file(target)
    require(expected == actual, "checksum mismatch: "+str(target))
    return actual

def run(command, cwd):
    return subprocess.check_output(command, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()

def main():
    check_seal(ROOT/"research/PROTOCOL-v1.md", ROOT/"research/PROTOCOL-v1.sha256")
    check_seal(ROOT/"research/ANALYSIS-PLAN-v1.md", ROOT/"research/ANALYSIS-PLAN-v1.sha256")
    check_seal(ROOT/"analysis/blind_predictions.json", ROOT/"analysis/blind_predictions.sha256")
    check_seal(ROOT/"evidence/native/hub_observer_only.csv", ROOT/"evidence/native/observer.sha256")
    check_seal(ROOT/"evidence/native/ground_truth_private.csv", ROOT/"evidence/native/truth.sha256")

    refs = {
        "rayls-sovereign-relayer": "b01b427de4cfc2ac66e75eba0d5070b73a3b137c",
        "rayls-sovereign-cli": "c356f9211b168c643d8f25d26df709af7dc4dd92",
        "rayls-sovereign-contracts": "ed8863885c8ed5d5d317d47a34c063907192687a",
    }
    for name, sha in refs.items():
        actual = run(["git","rev-parse","HEAD"], ROOT/"source"/name)
        require(actual == sha, "upstream pin mismatch "+name)
    require(hash_file(ROOT/"experiments/observer_w2_test.go")
            == hash_file(ROOT/"source/rayls-sovereign-relayer/enygma/service/observer_w2_test.go"),
            "native test-only harness differs from public source")
    tracked_diff = run(["git","diff","--name-only"], ROOT/"source/rayls-sovereign-relayer")
    require(not tracked_diff, "production relayer has modified tracked files")

    meta = json.loads((ROOT/"evidence/native/native_scenario_metadata.json").read_text())
    blind = json.loads((ROOT/"analysis/blind_predictions.json").read_text())
    scoring = json.loads((ROOT/"analysis/ground_truth_scoring.json").read_text())
    require(meta["evidence_type"] == "NATIVE_SOURCE_FUNCTION_WITH_SYNTHETIC_TRAFFIC", "wrong native class")
    require(not blind["ground_truth_used"], "blind analyzer used truth")
    require(scoring["prediction_commitment_sha256"] == hash_file(ROOT/"analysis/blind_predictions.json"), "scoring commitment mismatch")
    require(scoring["observer_sha256"] == hash_file(ROOT/"evidence/native/hub_observer_only.csv"), "scoring observer mismatch")
    require(scoring["truth_sha256"] == hash_file(ROOT/"evidence/native/ground_truth_private.csv"), "scoring truth mismatch")
    require(scoring["all_public_rows_matched_to_truth"], "scoring not reconciled")

    specifications = {x["scenario"]:x for x in meta["scenarios"]}
    observed=defaultdict(list)
    public_by_id={}
    with (ROOT/"evidence/native/hub_observer_only.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            scenario=row["scenario"]
            require(scenario in specifications,"unknown scenario")
            seq=int(row["sequence"])
            key=(scenario,seq)
            require(key not in public_by_id, "duplicate observed ID")
            spec=specifications[scenario]
            members=[int(x) for x in row["anonymity_set"].split("|")]
            require(len(members)==spec["k"],"wrong anonymity set k")
            require(sorted(set(members))==members,"duplicate/unsorted member")
            require(1001 in members, "sender missing")
            require(all(1001<=x<=1000+spec["participants"] for x in members), "member out of registry")
            public_by_id[key]=set(members)
            observed[scenario].append((seq,members))
    require(len(public_by_id)==5000,"missing/extra source observations")
    require(set(observed)==set(specifications),"missing scenario")

    valid_id_count=0
    for scenario,rows in observed.items():
        spec=specifications[scenario]
        rows.sort()
        require(len(rows)==500,"wrong observations in scenario")
        require([i for i,_ in rows]==list(range(1,501)),"sequence gap")
        candidates=list(range(1002,1001+spec["participants"]))
        for prefix in (25,50,100,200,500):
            counts=Counter(c for _,set_ids in rows[:prefix] for c in set_ids if c!=1001)
            sorted_candidates=sorted(candidates, key=lambda x: (-counts[x],x))
            predicted=blind["results"][scenario]["prefixes"][str(prefix)]
            require(predicted["top_candidate"]==sorted_candidates[0],"blind top not derivable from public data")
            require(predicted["runner_up"]==sorted_candidates[1],"blind runner not derivable from public data")
            require(predicted["all_counts"]=={str(c):counts[c] for c in candidates},"blind count mismatch")
        valid_id_count+=len(rows)

    groundtruth_count=0
    with (ROOT/"evidence/native/ground_truth_private.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            key=(row["scenario"],int(row["sequence"]))
            require(key in public_by_id,"truth row without public row")
            recips=[int(x) for x in row["actual_receivers"].split("|") if x]
            require(set(recips)<=public_by_id[key],"genuine recipient missing from actual native set")
            if row["kind"]=="zero_only":
                require(len(recips)==0,"zero-only with recipients")
            if row["kind"]=="payment":
                require(len(recips)==1,"payment without exactly 1 receiver")
            if row["kind"]=="multi_receiver":
                require(len(recips)==2,"multi payment without 2 receivers")
            groundtruth_count+=1
    require(groundtruth_count==5000, "truth observation count wrong")
    pref = [a for a in scoring["outcomes"].values() if a["known_preferred_receiver"] is not None]
    null = [a for a in scoring["outcomes"].values() if a["known_preferred_receiver"] is None]
    correct=sum(x["prediction_matches_preferred_at_500"] is True for x in pref)
    false=sum(x["balanced_null_rejected"] is True for x in null)
    require(len(pref)==7 and len(null)==3, "unexpected scenario allocation")
    require(scoring["total_observations"]==5000, "scoring total mismatch")

    offline_graph_path=ROOT/"evidence/offline-compose/seven_member_service_graph.json"
    if offline_graph_path.exists():
        graph=json.loads(offline_graph_path.read_text())
        require(graph["evidence_type"]=="OFFLINE_SEVEN_MEMBER_COMPOSE_STRUCTURE","seven graph not offline")
        require(len(graph["participants"])==7,"seven graph size mismatch")
        require(graph["service_count"]==len(graph["services"]),"offline service count wrong")
        require(graph["deployed"] is False,"offline graph mislabeled as deployed")

    report={
        "status":"PASS",
        "claims_scope":"OFFLINE_SOURCE_LEVEL_NATIVE_SYNTHETIC_TRAFFIC",
        "source_pins":refs,
        "source_harness_matches":True,
        "tracked_relayer_source_unmodified":True,
        "blind_prediction_sha256":hash_file(ROOT/"analysis/blind_predictions.json"),
        "observations":valid_id_count,
        "truth_records":groundtruth_count,
        "preferred_cases_correct":correct,
        "preferred_cases_total":len(pref),
        "null_cases_falsely_flagged":false,
        "null_cases_total":len(null),
        "no_live_chain_evidence_in_this_report":True,
    }
    output=ROOT/"qa/native-verification-report.json"
    output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("W2_NATIVE_INDEPENDENT_VERIFIER_PASS")
    print(f"OBSERVATIONS={valid_id_count} TRUTH={groundtruth_count}")
    print(f"PREFERRED={correct}/{len(pref)} FALSE_POSITIVES={false}/{len(null)}")

if __name__=="__main__":
    main()
