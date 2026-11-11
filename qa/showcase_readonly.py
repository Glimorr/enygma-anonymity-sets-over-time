#!/usr/bin/env python3
"""Read-only, disclosure-safe console views for three silent research recordings."""
import argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
j=lambda p:json.loads((R/p).read_text())
def section(s):
 print("\n"+"="*68+"\n"+s+"\n"+"="*68)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--part",choices=["source","hub","integrity"],required=True)
 a=ap.parse_args()
 if a.part=="source":
  section("PART 1 / NATIVE ENYGMA PRIVACY EXPERIMENT")
  reg=j("qa/native-verification-report.json")
  score=j("analysis/ground_truth_scoring.json")
  predicted=j("analysis/blind_predictions.json")
  print("EVIDENCE CLASS  : PINNED NATIVE RAYLS FUNCTION / SYNTHETIC SCHEDULES")
  print("OBSERVATIONS   :",reg["observations"])
  print("SOURCE REVISIONS:")
  for line in (R/"README.md").read_text().splitlines():
   if any(k in line for k in ("b01b427de4cfc2","c356f9211b168c","ed8863885c8ed")):
    print(" ",line[:180])
  o=score["outcomes"]
  positives=[(k,v) for k,v in o.items() if v["known_preferred_receiver"] is not None]
  negatives=[(k,v) for k,v in o.items() if v["known_preferred_receiver"] is None]
  print("POSITIVE CASES :",sum(bool(v["prediction_matches_preferred_at_500"]) for _,v in positives),"/",len(positives))
  print("NULL FLAGS     :",sum(bool(v["balanced_null_rejected"]) for _,v in negatives),"/",len(negatives))
  print("BLIND SEAL     :",hashlib.sha256((R/"analysis/blind_predictions.json").read_bytes()).hexdigest())
  print("INTERPRETATION : This is not an institutional payment or production deanonymization.")
 elif a.part=="hub":
  section("PART 2 / ACTUAL RESEARCHER-CONTROLLED HUB RECEIPTS")
  d=j("evidence/local-live-seven/receipt-reconciliation.json")
  print("EVIDENCE CLASS :",d["classification"])
  print("Mined Hub batches with six members  :",d["hub_enygma_batches_with_six_members"])
  print("Encrypted EnygmaTransfer envelopes :",d["hub_enygma_transfer_envelopes"])
  print("Saved receipts checked against RPC :",d["fresh_receipts_compared_to_live_rpc"])
  print("LOCAL HUB TX HASHES:")
  for batch in d["observed_batches"]:
   print("  block",batch["block"],"tx",batch["tx_hash"],"members",batch["members"])
  print("SETTLEMENT:",d["settlement"]["A_to_B"])
  print("LATE G    :",d["settlement"]["A_to_G"])
  print("FINAL UNRECONCILED UNITS :",d["settlement"]["unreconciled_units"])
  print("PROOF BOUNDARY : Local self-operated ledgers; no independent third-party quorum.")
 else:
  section("PART 3 / REPRODUCIBILITY AND MANIFEST")
  package=R if (R/"EVIDENCE-MANIFEST.json").is_file() else R/"release/public"
  m=json.loads((package/"EVIDENCE-MANIFEST.json").read_text())
  files=m["files"]
  good=True
  for name,entry in files.items():
   f=package/name
   if not f.is_file() or f.stat().st_size!=entry["bytes"] or hashlib.sha256(f.read_bytes()).hexdigest()!=entry["sha256"]:
    good=False;print("MISMATCH",name)
  print("RELEASE FILES   :",len(files))
  print("DIGEST CHECK    :","PASS" if good else "FAIL")
  print("ROOT SHA-256    :",m["files_merkle_equivalent_sha256"])
  print("EVIDENCE SCOPE  :",m["claim_scope"])
  print("LOCAL TESTS     :",j("qa/adversarial-report.json")["passing_tests"],"adversarial conditions (see report)")
  print("TESTNET ANCHOR  : PENDING (do not label this as on-chain)")
  if not good:raise SystemExit(1)
if __name__=="__main__":main()
