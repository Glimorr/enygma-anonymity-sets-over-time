#!/usr/bin/env python3
"""Publish only already verified public observer data from researcher-controlled local Hub receipts."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
source=json.loads((R/"evidence/local-live-seven/receipt-reconciliation.json").read_text())
assert source["classification"]=="LOCAL_RESEARCHER_CONTROLLED_LEDGER_EVIDENCE_NOT_THIRD_PARTY_CONSENSUS"
assert source["fresh_receipts_compared_to_live_rpc"]==15
assert source["settlement"]["unreconciled_units"]=="0"
assert source["hub_enygma_batches_with_six_members"]>=6
batches=sorted(source["observed_batches"],key=lambda x:x["block"])
assert all(len(x["members"])==6 for x in batches)
data={
 "evidence_class":"RESEARCHER_CONTROLLED_LOCAL_HUB_NOT_PUBLIC_TESTNET",
 "hubBatches":len(batches),
 "envelopes":source["hub_enygma_transfer_envelopes"],
 "recheckedReceipts":source["fresh_receipts_compared_to_live_rpc"],
 "bankIDs":list("ABCDEFG"),
 "batchRows":[{"block":a["block"],"txHash":a["tx_hash"],"members":[chr(c-12345+ord("A")) for c in a["members"]]} for a in batches],
 "bankBalances":{"A":"4998","B":"1","G":"1","total":"5000"},
 "lateG":True,
 "publicTestnetCommitment":"PENDING",
 "verificationTimestamp":source["verified_at_utc"]
}
(R/"site/live-data.js").write_text("window.RAYLS_LIVE_HUB_DATA = "+json.dumps(data,separators=(",",":"))+";\n")
print("LIVE_SITE_DATA_GENERATED",len(batches),"Hub batches",data["envelopes"],"event envelopes")
