#!/usr/bin/env python3
"""Independent analytic sensitivity preflight, computed without observed data."""
import json
import math
from pathlib import Path

def simulate_parameter(n, k=6, preferred_share=0.60, alpha=0.05):
    if n <= 6:
        k=n
    if n < 3:
        raise ValueError("Need at least three banks for candidate comparison")
    q=(k-2)/(n-2)
    neutral_share=(1-preferred_share)/(n-2)
    primary=q+(1-q)*preferred_share
    other=q+(1-q)*neutral_share
    delta=primary-other
    if delta == 0:
        min_samples=None
    else:
        min_samples=math.ceil(2*math.log((n-2)/alpha)/(delta**2))
    return {
        "participants":n, "k":k,
        "uniform_padding_decoy_rate":round(q,6),
        "favored_receiver_share":preferred_share,
        "favored_appearance_probability":round(primary,6),
        "other_appearance_probability":round(other,6),
        "appearance_probability_gap":round(delta,6),
        "conservative_hoeffding_95pct_samples":min_samples,
        "planned_samples":500,
        "planned_sample_count_meets_conservative_bound": (
            min_samples is not None and 500>=min_samples
        )
    }

rows=[simulate_parameter(n) for n in (6,7,8,10,20)]
out={
    "evidence_type":"THEORETICAL_PREEXPERIMENT",
    "formula":"q=(k-2)/(N-2), appearance_i=q+(1-q)*r_i",
    "hoeffding_bound":"P(any rival outranks favored) <= (N-2)*exp(-n*gap^2/2)",
    "warning":"Conservative sufficient bound, not a calibrated power estimate; multi-destination and zero-only traffic are excluded.",
    "results":rows
}
root=Path(__file__).resolve().parents[1]
target=root/"research"/"POWER-PREFLIGHT.json"
target.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print("PREFLIGHT_CALCULATED_BEFORE_OBSERVING_LABELS")
for row in rows:
    print("N=%d delta=%.4f conservative_n=%s planned=500" %
          (row["participants"],row["appearance_probability_gap"],row["conservative_hoeffding_95pct_samples"]))
