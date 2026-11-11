#!/usr/bin/env python3
"""Independent, offline verification of a complete public Rayls W2 release.

No Git checkout, network RPC, Go toolchain or confidential data access is needed.
"""
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def check(x,m):
    if not x: raise AssertionError(m)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def assert_seal(file,sealed):
    check(Path(sealed).read_text().split()[0]==sha(file),f"checksum mismatch {file}")

def main():
    src=ROOT/"evidence/native/hub_observer_only.csv"
    truth=ROOT/"evidence/native/ground_truth_private.csv"
    blind=ROOT/"analysis/blind_predictions.json"
    score=ROOT/"analysis/ground_truth_scoring.json"
    meta=ROOT/"evidence/native/native_scenario_metadata.json"

    for data,seal in [
        (src,ROOT/"evidence/native/observer.sha256"),
        (truth,ROOT/"evidence/native/truth.sha256"),
        (blind,ROOT/"analysis/blind_predictions.sha256"),
        (ROOT/"research/PROTOCOL-v1.md",ROOT/"research/PROTOCOL-v1.sha256"),
        (ROOT/"research/ANALYSIS-PLAN-v1.md",ROOT/"research/ANALYSIS-PLAN-v1.sha256"),
    ]:
        check(Path(data).exists(),f"missing artifact: {data}")
        assert_seal(data,seal)
    original=json.loads(blind.read_text())
    scored=json.loads(score.read_text())
    check(not original["ground_truth_used"],"prediction claim not blind")
    check(original["observer_sha256"]==sha(src),"prediction set mismatch")
    check(original["metadata_sha256"]==sha(meta),"metadata mismatch")
    check(scored["prediction_commitment_sha256"]==sha(blind),"scoring seal mismatch")
    check(scored["observer_sha256"]==sha(src),"scoring observer mismatch")
    check(scored["truth_sha256"]==sha(truth),"scoring truth mismatch")

    specs={p["scenario"]:p for p in json.loads(meta.read_text())["scenarios"]}
    obs=defaultdict(list)
    present={}
    with src.open(newline="",encoding="utf-8") as f:
        rows=csv.DictReader(f)
        check(rows.fieldnames==["scenario","sequence","sender_chain","anonymity_set"],"unexpected observer schema")
        for row in rows:
            spec=specs[row["scenario"]]
            seq=int(row["sequence"])
            values=list(map(int,row["anonymity_set"].split("|")))
            check(int(row["sender_chain"])==1001,"wrong sender")
            check(len(values)==spec["k"],"wrong k")
            check(values==sorted(set(values)),"nonunique or unsorted bank IDs")
            check(1001 in values,"sender absent")
            check(set(values)<=set(range(1001,1001+spec["participants"])),"unknown bank")
            key=(row["scenario"],seq)
            check(key not in present,"duplicate row")
            present[key]=set(values)
            obs[row["scenario"]].append((seq,values))
    check(len(present)==5000,"wrong native observation total")
    check(set(obs)==set(specs),"missing scenario")

    truthrows={}
    with truth.open(newline="",encoding="utf-8") as f:
        rows=csv.DictReader(f)
        check(rows.fieldnames==["scenario","sequence","actual_receivers","kind","preferred_receiver"],"unexpected truth schema")
        for row in rows:
            key=(row["scenario"],int(row["sequence"]))
            check(key in present and key not in truthrows,"wrong truth linkage")
            receivers=list(map(int,[r for r in row["actual_receivers"].split("|") if r]))
            check(set(receivers)<=present[key],"real receiver missing from official set")
            if row["kind"]=="zero_only":check(len(receivers)==0,"zero-only with recipient")
            elif row["kind"]=="payment":check(len(receivers)==1,"single payment malformed")
            elif row["kind"]=="multi_receiver":check(len(receivers)==2,"multi payment malformed")
            else:raise AssertionError("unknown batch kind")
            truthrows[key]=row
    check(set(truthrows)==set(present),"incomplete truth linkage")

    for name, rows in obs.items():
        spec=specs[name]
        check(len(rows)==500,"wrong scenario size")
        rows.sort()
        check([n for n,_ in rows]==list(range(1,501)),"sequence mismatch")
        candidates=range(1002,1001+spec["participants"])
        for n in [25,50,100,200,500]:
            inc=Counter(member for _,members in rows[:n] for member in members if member!=1001)
            expected=sorted(candidates,key=lambda bank:(-inc[bank],bank))
            got=original["results"][name]["prefixes"][str(n)]
            check(got["top_candidate"]==expected[0],"wrong top inference")
            check(got["runner_up"]==expected[1],"wrong runner-up")
            check(got["all_counts"]=={str(i):inc[i] for i in candidates},"membership counts differ")
            check(sum(inc.values())==n*(spec["k"]-1),"total bank slots don't reconcile")

    # Re-run original analysis and scoring on disposable outputs, then compare
    # the exact JSON bytes. This enforces deterministic offline reproduction.
    with tempfile.TemporaryDirectory() as t:
        prefix=Path(t)
        scratch_blind=prefix/"blind_predictions.json"
        cmd=[sys.executable,str(ROOT/"analysis/analyze_public.py"),
             "--observer",str(src),"--metadata",str(meta),"--output",str(scratch_blind)]
        subprocess.run(cmd,check=True,capture_output=True,text=True)
        check(scratch_blind.read_bytes()==blind.read_bytes(),"blind analysis fails clean reproduction")
        scratch_scoring=prefix/"ground_truth_scoring.json"
        cmd=[sys.executable,str(ROOT/"analysis/score_private.py"),
             "--predictions",str(blind),
             "--seal",str(ROOT/"analysis/blind_predictions.sha256"),
             "--truth",str(truth),"--observer",str(src),
             "--output",str(scratch_scoring)]
        subprocess.run(cmd,check=True,capture_output=True,text=True)
        check(scratch_scoring.read_bytes()==score.read_bytes(),"private scoring fails clean reproduction")

    outcomes=scored["outcomes"]
    preferred=[x for x in outcomes.values() if x["known_preferred_receiver"] is not None]
    null=[x for x in outcomes.values() if x["known_preferred_receiver"] is None]
    check(len(preferred)==7 and len(null)==3,"wrong control conditions")
    print("PUBLIC_EVIDENCE_REPRODUCTION_PASS")
    print("ALL_5000_SOURCE_LEVEL_OBSERVATIONS_RECONCILED")
    print("PREFERRED_MATCHES",sum(x["prediction_matches_preferred_at_500"] for x in preferred),"/7")
    print("FALSE_NULL_FLAGS",sum(x["balanced_null_rejected"] for x in null),"/3")
    print("PREDICTIONS_AND_SCORING_RECOMPUTED_BYTE_FOR_BYTE")
    print("NATIVE_ONLY_VERIFICATION_DOES_NOT_AUTHENTICATE_LOCAL_HUB_RECEIPTS; SEE SEPARATE LOCAL_LEDGER_VERIFIER")

if __name__=="__main__": main()
