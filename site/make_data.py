#!/usr/bin/env python3
"""Prepare an evidence-grounded, static, no-external-dependency website data file."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
blind=json.loads((root/"analysis/blind_predictions.json").read_text())
truth=json.loads((root/"analysis/ground_truth_scoring.json").read_text())
power=json.loads((root/"research/POWER-PREFLIGHT.json").read_text())
scenarios=[]
for name, p in blind["results"].items():
    actual=truth["outcomes"][name]
    scenarios.append({
        "id":name,"n":p["participant_count"],"k":p["k"],
        "model":p["traffic_model_hint"],
        "preferred":actual["known_preferred_receiver"],
        "realPaymentLegs":actual["genuine_receiver_inclusions"],
        "traffic":actual["traffic_kinds"],
        "prefixes":p["prefixes"],
        "inferenceCorrect":actual["prediction_matches_preferred_at_500"]
    })
payload={
    "status":"NATIVE_SOURCE_LEVEL_ONLY",
    "honesty":"Native Go relayer source with synthetic traffic. No authenticated seven-member Hub transactions yet.",
    "observerFilesHash":blind["observer_sha256"],
    "predictionsHash":truth["prediction_commitment_sha256"],
    "sources":{
        "relayer":"b01b427de4cfc2ac66e75eba0d5070b73a3b137c",
        "cli":"c356f9211b168c643d8f25d26df709af7dc4dd92",
        "contracts":"ed8863885c8ed5d5d317d47a34c063907192687a",
    },
    "trials":blind["observation_count"],
    "scenarioCount":len(scenarios),
    "preferredCorrect":sum(x["inferenceCorrect"] is True for x in scenarios),
    "preferredTotal":sum(x["preferred"] is not None for x in scenarios),
    "nullFalsePositives":sum(x["preferred"] is None and x["prefixes"]["500"]["reject_balanced_model_at_fwer_0_05"] for x in scenarios),
    "nullTotal":sum(x["preferred"] is None for x in scenarios),
    "scenarios":scenarios,
    "power":power["results"]
}
js="window.RAYLS_RESEARCH_DATA = "+json.dumps(payload,separators=(",",":"),sort_keys=True)+";\n"
dest=root/"site/data.js"
dest.write_text(js,encoding="utf-8")
print("WEBSITE_DATA_PREPARED",len(js),"bytes",len(scenarios),"scenarios")
