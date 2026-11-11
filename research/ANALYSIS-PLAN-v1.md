# Blinded analysis plan v1 — fixed before evaluating native observations
This addendum applies only to source-level synthetic-traffic trials specified in PROTOCOL-v1.md.
Source and synthetic ground truth are separate files; the first-stage analyzer has no argument or code path to access the ground-truth file.

1. Score every non-sender candidate by number of appearances in the anonymity set for that scenario.
2. Rank by decreasing appearance count; break ties by ascending chain ID; report the top candidate and runner-up.
3. Under the balanced null each candidate appears with p0=(k-1)/(N-1) independently across draws.
4. Calculate a one-sided binomial survival tail for the top candidate's count, then multiply by (N-1) as a conservative within-scenario family-wise bound. Flag departure from a balanced schedule only if adjusted p < 0.005 (Bonferroni correction for the ten prespecified scenarios at a family alpha 0.05).
5. Calculate Wilson 95% intervals for top and runner-up member inclusion proportions. These characterize inclusion frequency, NOT directly receiver identity probabilities.
6. Recompute rankings and null significance at predetermined 25, 50, 100, 200, and 500 observation prefixes. Do not choose a favorable stopping point.
7. Commit (hash) blind_predictions.json before the scorer accesses ground_truth_private.csv. Only then reveal and measure whether the top inferred receiver matches the held-back preferred receiver in the preferred-recipient scenarios.
8. For balanced and zero-only negative controls, report false-positive flags instead of inventing a preferred ground truth.
9. For mixed-zero and multi-receiver cases report results separately: the single-receiver analytic formula does not precisely model these conditions.
10. Native padding uses cryptographic randomness and will change in fresh runs, but saved raw evidence and the blind analysis are exactly reproducible. Do not present reruns as bitwise-identical generated samples or as blockchain receipts.

The selected test count of 500 per condition is fixed in advance; no outcome-dependent sampling extensions are allowed within this preregistered study.
