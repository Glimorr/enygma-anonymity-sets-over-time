# Can Enygma's Six-Bank Anonymity Cap Reveal Payment Relationships Over Time?

**Independent research on longitudinal recipient privacy in Rayls Enygma.** Updated November 2026.

**Interactive website:** https://glimorr.github.io/enygma-anonymity-sets-over-time/

**Public reproducibility repository:** https://github.com/Glimorr/enygma-anonymity-sets-over-time



**Current evidence status:** A pinned, unmodified Rayls Go relayer function was exercised under ten controlled synthetic payment schedules. It generated 5,000 authentic native-function outputs. Blind membership-frequency analysis identified the preferred receiver in all seven positive scenarios and rejected none of the three null controls. **These are native source-level observations, not blockchain transaction receipts or proof of a vulnerability in a production Rayls network.** The seven-bank local stack now has six mined Hub anonymity-set batches, 36 encrypted event envelopes, 15 receipt-to-fresh-RPC checks, and a reconciled 5,000-unit trial. G settled late after the original timeout. A retrospective public Rayls Testnet SHA-256 archive anchor is recorded separately in site/public-anchor.json when mined.

## Research question and answer

Can a Hub observer recover an institution's preferred receiver by counting appearances in repeated Enygma anonymity sets, even when an individual payment's true receiver is obscured by zero-value decoys?

Under a controlled model with known sender, a single receiver and random padding, yes: a bank selected often as the true receiver appears in an anonymity set more frequently than a bank selected only as a decoy. In the current pinned implementation, the relayer caps sets at six participants. For N registered institutions greater than six, not everyone appears in every batch. This creates an observable statistical signal under our experimental assumptions.

This does **not** mean a Hub observer can always infer an actual recipient, a production payment amount, or a complete payment graph. Real operational traffic may contain multiple real receivers, padding-only finalization batches, many senders, membership churn, and no observable linkage to a common payer.

## First-hand source-level evidence

The test harness calls the official Go production functions `getAnonymityIndex` and `fulfillAnonimitySet` directly from a pinned relayer checkout. It does not reimplement the padding function.

- **10 prespecified scenarios × 500 observations = 5,000 native outputs.**
- **Seven preferred-receiver conditions** produced seven correct top-ranked predictions after the sealed blind prediction file was compared with synthetic truth.
- **Three null conditions**—balanced six-bank traffic, balanced eight-bank traffic, and padding-only eight-bank traffic—produced no flagged positive signal at the preregistered family-wise threshold.
- A conservative concentration-bound sensitivity audit warned that 500 observations are **below** a conservative sufficient bound for the seven-bank case. That successful sample should not be confused with guaranteed inference success for all traffic histories.
- All 5,000 native observations were reconciled with synthetic ground truth by a separate verifier.
- Six adversarial evidence tests detected incorrect checksums, altered predictions, dropped rows, invalid sets, missing artifacts and impossible ground-truth recipients.

Both the full observer-only set ledger and the ground-truth reveal are included, allowing independent reanalysis.

## Genuine seven-bank local Hub observations

This source-level study is supplemented by genuine transactions on an isolated seven-institution Rayls laboratory, not by a public-chain impersonation of Enygma. Bank A deployed and registered a study token, authorized it locally, submitted it to the Hub, received Hub approval and minted 5,000 smallest units.

- A to B: source receipt mined, destination balance reconciled.
- A to G: source receipt mined; G mapping was absent at the preregistered 150-second deadline. The team discovered that the first attempted TLS repair targeted the NATS client certificate instead of the CTS gRPC server certificate. After correcting the actual server certificate, the relayer caught up and the original source transaction settled without another source transfer. This is late recovery, not an on-time pass.
- Final balances: A=4,998, B=1, G=1, totaling 5,000/5,000 minted base units, with zero unresolved units.
- Six actual Hub transaction batches emitted 36 EnygmaTransfer event envelopes. Every batch had six distinct bank IDs among the seven institutions.
- Fifteen saved source/Hub receipts were compared with fresh local RPC and matching block hashes. A second independent standard-library ABI decoder reproduced the recorded six-member sets and was compared with the Ethers decoder.

See evidence/local-rpc/ for raw local receipts and independently decoded events; see evidence/local-live-seven/ for the verifier report. The offline command python3 qa/verify_local_live.py --check-only reproduces structural checks without an active node.

**Authentication boundary:** these are genuine mined transactions on one researcher-operated local Private Network Hub, not independent third-party consensus. Six local batches establish observable event structure, not a statistically powered receiver deanonymization result on a production bank. An eventual public testnet hash commitment would establish artifact chronology/integrity, not retroactively authenticate these private-chain events.

## Native source and provenance

Pinned revisions:
- [Official Rayls Sovereign relayer](https://github.com/raylsnetwork/rayls-sovereign-relayer/tree/b01b427de4cfc2ac66e75eba0d5070b73a3b137c) — `b01b427de4cfc2ac66e75eba0d5070b73a3b137c`
- [Official Rayls Sovereign CLI](https://github.com/raylsnetwork/rayls-sovereign-cli/tree/c356f9211b168c643d8f25d26df709af7dc4dd92) — `c356f9211b168c643d8f25d26df709af7dc4dd92`
- [Official contracts](https://github.com/raylsnetwork/rayls-sovereign-contracts/tree/ed8863885c8ed5d5d317d47a34c063907192687a) — `ed8863885c8ed5d5d317d47a34c063907192687a`

The original relayer production code is unchanged. The research-only Go file `experiments/observer_w2_test.go` is copied into the official source package for native tests.

An official CLI full-stack demo enforces at most six members. Our research-only extension adds the seventh participant to the CLI and a corresponding `localG` Hardhat configuration. The exact patches are included in `experiments/`; these **are experimental configuration changes**, not protocol changes. The research-only extension is now backed by authentic local seven-bank Hub receipts, but does not establish production deployment or outside-validator consensus.

## How to reproduce

Prerequisites: Python 3.11+ and Git; Go 1.26.x is required for native relayer test reproduction.

From a clean repository checkout:

```bash
python3 qa/check_manifest.py
python3 qa/check_site.py --check-only
python3 qa/check_anchor.py --optional
python3 qa/verify_public.py
python3 qa/adversarial_checks.py
python3 analysis/analyze_public.py \
  --observer evidence/native/hub_observer_only.csv \
  --metadata evidence/native/native_scenario_metadata.json \
  --output /tmp/recomputed-enygma-w2-predictions.json
```

The recomputed result should equal `analysis/blind_predictions.json` byte-for-byte when using the same Python implementation. No private keys, live RPC endpoint or Docker image is needed for the offline analysis.

To reproduce the native function on fresh random draws:

```bash
python3 qa/bootstrap_sources.py
cd source/rayls-sovereign-relayer
ENYGMA_W2_OUTPUT=/tmp/enygma-w2-fresh go test ./enygma/service -run '^TestW2ObserverSelection$' -count=1 -v
```

Because the upstream function uses `crypto/rand`, independently generated samples are **not byte-for-byte identical**. They must satisfy the same structural invariants, not match archived hashes.

The GitHub Actions workflow runs the integrity and analysis checks on a fresh hosted runner.

## Experiment controls and interpretation

All scenarios include the sender in the observed set. For one real receiver per batch, under uniform independent decoy selection:

`q = (k-2)/(N-2)`, `P(bank i appears) = q + (1-q) r_i`.

Here `k=min(N,6)`, `N` is the number of registered participants, and `r_i` is the real receiver's traffic share. The simple formula does not apply unchanged to multi-recipient or padding-only batches.

The observer-only estimator ranks candidates by public membership frequency, with a fixed tie-break. Balanced-model significance uses a one-sided binomial tail, Bonferroni-adjusted across candidate banks and across the ten prespecified scenario families. Ground truth is provided only to the scorer after the blind output is sealed.

**Evidence taxonomy:** `NATIVE SOURCE-LEVEL` describes the Go function's outputs on synthetic schedules. `OFFLINE INTEGRITY` describes reproducibility on the released data. `LOCAL RPC VERIFIED` now denotes independently re-read local-chain source/Hub receipts, decoded events and balances; not independent external consensus. `PUBLIC TESTNET COMMITMENT` applies only to a successful mined transaction committing artifact hashes. A public hash commitment never proves the truth of private-chain events.

## Independent research contribution

Rayls documentation describes anonymity-set composition and single-transaction access privileges. This research adds a longitudinal, hypothesis-driven test of what repeated public set membership can reveal about a bank's *payment preferences* and, equally importantly, which control conditions should show no such signal.

The underlying statistical disclosure idea predates this experiment; no claim is made to have invented intersection or disclosure attacks. The new work is the **implementation-specific measurement, archived observer/ground-truth separation, positive controls, negative controls, and independently testable evidence record**.

## Files and publication

- `research/`: original protocol and analysis decisions, hashes, analytical power preflight
- `experiments/`: native Go harness and exact seven-bank deployment patches
- `evidence/native/`: all observed anonymity sets, synthetic truth and native test log
- `analysis/`: blinded predictions, cryptographic seal and post-reveal scoring
- `qa/`: source/independent reproducibility and adversarial verification
- `site/`: animated 3D research website with local Hub explorer and clear evidence boundaries
- `figures/`: six original reproducible research figures, including the real local Hub membership matrix
- `site/DESIGN-NOTES.md`: visual identity, accessibility and animated 3D design rationale
- `qa/check_site.py`: offline site and evidence-data integrity verifier
- `EVIDENCE-MANIFEST.json`: complete allowlisted release file catalog with SHA-256 digests

No private RPC credentials, dev wallets, secret keys or unpublished operator evidence are included in this public release. Private development environments should be treated as demonstrations, not third-party institutional testnets.

## Sources

Official [How Enygma Works](https://docs.rayls.com/docs/how-enygma-works) and [Enygma privacy and auditing](https://docs.rayls.com/docs/enygma-privacy-and-auditing); pinned relayer/CLI/contracts source above.

## Operational issues encountered and fixes

1. The CLI restricts its full demo to at most six participants; we independently verified the seven-member Compose graph and introduced an auditable CLI-only extension.
2. The default full-stack contracts image omitted required `PUBLIC_CHAIN_ID`; a corrected local public-chain preset supplies it.
3. Even with that preset, the contracts image had only `localA`–`localF` Hardhat networks. A source-pinned `localG` configuration extension was prepared, with the original failures retained as evidence.
4. Native inference must not be represented as a proof of real-network deanonymization; our website and verifier enforce that classification.
5. The localG deployment initially generated only chain-address fields for Bank G; runtime settings were reconstructed without exposing credentials, preserving G-specific chain IDs and addresses. See evidence/offline-compose/g_runtime_config_repair_report.json.
6. The first TLS repair targeted the wrong file (NATS client cts.crt). We preserved the failed attempt, restored the original client certificate, and corrected the CTS gRPC server.crt SAN for cts-g. Live server certificate inspection and G relayer catch-up verified the fix; see evidence/offline-compose/cts-g-certificate-provenance.json.
7. The seven-bank service graph exceeded PostgreSQL's default connection limit; the local Compose profile now sets max_connections=300 without resetting historical data. A separate read-only probe verified the Hub, seven privacy-node RPCs and local public chain, 9/9 endpoints (see evidence/local-rpc/).


This README records verified source-level and researcher-controlled local-chain evidence. A retrospective public Rayls Testnet hash anchor is documented separately in site/public-anchor.json, and verified using python3 qa/check_anchor.py --live-rpc. It proves the digest was committed to the public Testnet after the experiments; it does not establish independent private-ledger consensus or pre-experiment prediction chronology. The repository and site are publicly hosted.
