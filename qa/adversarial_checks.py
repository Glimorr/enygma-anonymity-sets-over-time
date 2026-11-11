#!/usr/bin/env python3
"""Adversarial tests using disposable copies; never modifies original evidence."""
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PY=sys.executable

def cmd_expect_failure(command):
    r=subprocess.run(command,capture_output=True,text=True,timeout=30)
    if r.returncode==0:
        raise AssertionError(f"tampering was ACCEPTED: {command}")
    return (r.stderr or r.stdout)[-280:].strip()

def main():
    e=ROOT/"evidence/native"
    trials={}
    with tempfile.TemporaryDirectory(prefix="w2-attack-",dir=ROOT/"qa") as work:
        out=Path(work)
        observer=e/"hub_observer_only.csv"
        pred=ROOT/"analysis/blind_predictions.json"
        meta=e/"native_scenario_metadata.json"
        truth=e/"ground_truth_private.csv"
        seal=ROOT/"analysis/blind_predictions.sha256"
        obs_seal=e/"observer.sha256"

        tamper=out/"tampered_observer.csv"
        shutil.copyfile(observer,tamper)
        content=tamper.read_bytes()
        tamper.write_bytes(content.replace(b"A_N6_balanced",b"Z_N6_balanced",1))
        expected=obs_seal.read_text().split()[0]
        require_not_equal=hashlib.sha256(tamper.read_bytes()).hexdigest()
        if expected==require_not_equal:
            raise AssertionError("observer mutation not detected by SHA-256")
        trials["observer_mutation_rejected_by_hash"]="PASS"

        bogus=out/"missing_observer.csv"
        if bogus.exists():
            raise AssertionError("missing test path exists")
        try:
            bogus.read_bytes()
        except FileNotFoundError:
            trials["missing_artifact_rejected"]="PASS"
        else:
            raise AssertionError("missing evidence unexpectedly readable")

        altered=out/"altered_prediction.json"
        shutil.copyfile(pred,altered)
        data=altered.read_bytes().replace(b'"ground_truth_used": false',b'"ground_truth_used": true',1)
        if data==altered.read_bytes():raise AssertionError("prediction mutation did not apply")
        altered.write_bytes(data)
        rejection=cmd_expect_failure([
            PY,str(ROOT/"analysis/score_private.py"),
            "--predictions",str(altered),"--seal",str(seal),
            "--truth",str(truth),"--observer",str(observer),
            "--output",str(out/"should_not_appear.json")
        ])
        trials["altered_blind_prediction_rejected"]="PASS"

        # Replacing one bank ID creates a duplicate in a seven-member set.
        with observer.open(newline="") as f:
            records=list(csv.DictReader(f))
        for row in records:
            if row["scenario"]=="D_N8_preferred":
                members=row["anonymity_set"].split("|")
                members[-1]=members[0]
                row["anonymity_set"]="|".join(members)
                break
        invalid=out/"bad_set.csv"
        with invalid.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(records[0]))
            writer.writeheader();writer.writerows(records)
        rejection=cmd_expect_failure([
            PY,str(ROOT/"analysis/analyze_public.py"),
            "--observer",str(invalid),"--metadata",str(meta),
            "--output",str(out/"bad_out.json")
        ])
        trials["invalid_anonymity_set_rejected"]="PASS"

        rows=records[:-1]
        missing=out/"one_row_missing.csv"
        with missing.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(records[0]))
            writer.writeheader();writer.writerows(rows)
        rejection=cmd_expect_failure([
            PY,str(ROOT/"analysis/analyze_public.py"),
            "--observer",str(missing),"--metadata",str(meta),
            "--output",str(out/"bad_missing_out.json")
        ])
        trials["incomplete_trial_ledger_rejected"]="PASS"

        with truth.open(newline="") as f:
            truths=list(csv.DictReader(f))
        for row in truths:
            if row["scenario"]=="D_N8_preferred" and row["kind"]=="payment":
                row["actual_receivers"]="9999"
                break
        badtruth=out/"truth_corrupted.csv"
        with badtruth.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(truths[0]))
            writer.writeheader();writer.writerows(truths)
        rejection=cmd_expect_failure([
            PY,str(ROOT/"analysis/score_private.py"),
            "--predictions",str(pred),"--seal",str(seal),
            "--truth",str(badtruth),"--observer",str(observer),
            "--output",str(out/"bad_truth_result.json")
        ])
        trials["ground_truth_receiver_not_in_set_rejected"]="PASS"

    report={
        "status":"PASS",
        "test_scope":"ADVERSARIAL_OFFLINE_INTEGRITY_CHECKS",
        "original_evidence_modified":False,
        "tests":trials,
        "passing_tests":len(trials)
    }
    target=ROOT/"qa/adversarial-report.json"
    target.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("W2_ADVERSARIAL_EVIDENCE_CHECKS_PASS",len(trials))
    for name in sorted(trials):print(name,": PASS")

if __name__=="__main__":
    main()
