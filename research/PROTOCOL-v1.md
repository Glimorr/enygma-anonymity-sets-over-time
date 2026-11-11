# Rayls Enygma longitudinal recipient-privacy study — preregistered protocol v1
Date: 2026-11-11 (UTC). Status: source-level experimental protocol, BEFORE measured native trials.
Working question: Does the six-member Enygma anonymity cap leak the identity of a sender's favored receiving institution from repeated Hub-visible anonymity-set membership?

## Scope and observer
- Target pinned relayer: raylsnetwork/rayls-sovereign-relayer @ b01b427de4cfc2ac66e75eba0d5070b73a3b137c.
- Target pinned CLI: raylsnetwork/rayls-sovereign-cli @ c356f9211b168c643d8f25d26df709af7dc4dd92.
- Target pinned contracts: raylsnetwork/rayls-sovereign-contracts @ ed8863885c8ed5d5d317d47a34c063907192687a.
- Observer may use only sending-chain identity, names of anonymity-set participants, token identifier and sequence/order visible on Private Network Hub. It cannot use decrypted messages, true recipients, application logs, confidential amounts, or operator keys.
- Source-level experiments synthesize recipient schedules and invoke the exact unmodified native padding function from the pinned relayer. This is NOT proof of on-chain Enygma payments.
- Primary claim is limited to a declared model unless verified genuine N>=7 Hub receipts establish applicability under a live network.

## Hypotheses
H0: With N<=6, membership frequencies convey no receiver-preference signal because every eligible bank appears in each six-member set.
H1: With N>6, a persistent preferred receiver can increase membership frequency above other eligible receivers under uniform padding and single genuine receiver per batch.
H2: Under balanced recipient schedules the blind method must not overclaim preference, tested with multiple null samples and a calibrated false-positive threshold.
H3: Zero-value finalizations and mixed-recipient batching alter the inference accuracy; quantify both rather than filter them using information a public Hub observer lacks.
H4: Disclosed outcomes must separate protocol-selection leakage from real-world linkability and from off-chain privileged information.

## Native scenarios and stopping rules
For each scenario produce 500 observations from the actual relayer function with untouched crypto/rand.Reader for padding:
A: N=6, balanced true receivers.
B: N=7, one receiver preferred at 0.60.
C: N=8, balanced receivers.
D: N=8, one receiver preferred at 0.60.
E: N=8, one receiver preferred at 1.00 (positive sensitivity control).
F: N=8, 25% zero-only finalizations; remaining real transfers 0.60 preferred.
G: N=8, two real receivers in each batch, first selected with 0.60 preference.
H: N=10, 0.60 preferred.
I: N=20, 0.60 preferred.
J: N=8, zero-only transactions (negative control).
Each observed anonymity set includes the sender chain and the true receiver(s), where present; padding uses the official function. No outcome-dependent stopping; all observations and failed calls must be counted.
Sender=1001, receiver candidates=1002,...; do not expose receiver schedule or preferred receiver label to the blind analyzer.
Use independent public-only inference and a separate ground-truth evaluation file. Reveal the ground truth only after writing the predictions file and its SHA-256 commitment.
Primary statistic: accuracy of top-ranked inferred receiver in D,E,H,I; report exact true receiver ID and all candidate scores after reveal.
Secondary: balanced false-positive rate across A,C,J; expected inclusion probabilities and calibration; zero-only and mixed-receiver degradation.
Avoid treating a few favorable examples as general network privacy proof.

## Mathematical benchmark
For N distinct banks, fixed k=min(6,N), one sender and one true receiver per batch:
q=(k-2)/(N-2); P(candidate i in set)=q+(1-q)*r_i.
Under balanced traffic r_i=1/(N-1), hence inclusion probability (k-1)/(N-1).
For zero-only batches, any non-sender candidate has inclusion probability (k-1)/(N-1).
For multiple actual receivers, the single-receiver formula DOES NOT directly apply.
Compare empirical native draws to independent analytic prediction, confidence intervals, and null-control distributions.

## Evidence taxonomy and go/no-go
- Native source-level tests: code execution of pinned Go function with synthetic truth (label: NATIVE SOURCE-LEVEL).
- Offline verifier: read-only reanalysis of archived CSV and hashes (label: ARCHIVED OFFLINE).
- Genuine Hub event observations: pinned RPC receipts and chain identity verified live, decoded with ABI (label: LOCAL RPC VERIFIED), only if executed.
- Public Rayls testnet commitments: separately authenticated public tx hashes for protocol, blinded predictions, final manifest. A hash anchor attests to a file commitment, NOT local private-chain transaction validity.
- Outside consensus or independent remote witness requires genuinely independent verification; never call our own local nodes an independent third party.
- If no authentic N>=7 Hub traffic with clear chain-of-custody is achievable, classify the on-chain privacy finding UNVERIFIED and reassess the topic against a more feasible alternative before making universal claims.
- Experiment findings do not imply a vulnerability in Enygma Retail or production institutional installations.

## Evaluator acceptance criteria
Independent question and new Rayls-specific evidence; pinned source/binaries with documented modifications; causal positive/negative controls; sufficient preregistered trial count; data-separated blind predictions with provable chronology; complete transaction outcome accounting; all artifacts present and checksummed; a verifier that rejects missing/altered files; reproducible code and CI; truthful labels; useful technical implications and searchable question-led publication.
Do not publish privileged private-network keys, credentials, or sensitive security reports in public artifacts.
