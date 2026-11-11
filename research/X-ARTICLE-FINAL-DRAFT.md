# Can Six Visible Banks Become a Signal? I Tested Enygma Over Time

One payment can hide its receiving institution among decoys. But repeated payments leave repeated observations. I wanted to know whether Enygma's six-member anonymity-set cap could turn those observations into a signal about an institution's preferred receiving bank.

I didn't begin with a mock privacy dashboard. I worked from Rayls' pinned relayer implementation, tested ten controlled traffic patterns, committed blind predictions before comparing them with hidden synthetic truth, and then built a seven-bank local Rayls stack to check what the actual Private Network Hub emits.

The result isn't a claim that a production bank has been deanonymized. It is a reproducible, implementation-specific test of a longitudinal metadata question—and a better understanding of where the signal appears, where it disappears, and what the local Hub really exposes.

**Research site:** https://glimorr.github.io/enygma-anonymity-sets-over-time/  
**Code, raw observations and receipts:** https://github.com/Glimorr/enygma-anonymity-sets-over-time

---

## The question behind the test

Rayls Enygma uses confidential payloads and anonymity sets to obscure which participating bank is the true receiver of a particular payment. The source-level model I inspected caps each observable set at six participants.

That creates an interesting edge case when the network has **more than six registered banks**. The sender and a true receiver can appear alongside randomly selected decoys. Across many payments, a frequently chosen true receiver may appear more often than institutions included only as padding.

The core question was simple: **can an observer estimate a preferred receiving bank from visible set membership alone, without seeing the confidential amount or receiving labels?**

Under the simplified single-receiver model, with `N` registered banks and set size `k=min(N,6)`, a bank that is not the sender has a background inclusion probability of approximately:

`q = (k-2)/(N-2)`

If institution `i` is the true receiver for a fraction `r_i` of payments, its modeled set-inclusion probability becomes:

`P(i appears) = q + (1-q) × r_i`.

This model is not a universal law for mixed or padding-only traffic. It gave me a falsifiable prediction to test against the real selection function.

**Figure 1:** What a Hub observer can see.  
[Insert `figures/01-anonymity-set-model.svg`]

---

## The native experiment: 5,000 real outputs from the pinned function

I pinned the official [Rayls Sovereign relayer](https://github.com/raylsnetwork/rayls-sovereign-relayer/tree/b01b427de4cfc2ac66e75eba0d5070b73a3b137c), [Sovereign CLI](https://github.com/raylsnetwork/rayls-sovereign-cli/tree/c356f9211b168c643d8f25d26df709af7dc4dd92), and [contracts](https://github.com/raylsnetwork/rayls-sovereign-contracts/tree/ed8863885c8ed5d5d317d47a34c063907192687a).

The Go test harness invokes the **actual production selection functions**, `getAnonymityIndex` and `fulfillAnonimitySet`. I did not substitute my own decoy sampler. The payment schedules fed to that function are synthetic; the function outputs are genuine native execution results, not blockchain transactions.

Ten scenarios × 500 observations produced **5,000 observer-visible sets**. The scenarios included preferred-recipient traffic, balanced traffic, mixed distributions, and a padding-only null condition. A separate file held the synthetic truth; the observer analysis saw only anonymized membership records.

I sealed the blind predictions with SHA-256, scored them against ground truth afterward, and checked early prefixes at 25, 50, 100, 200 and 500 observations.

**What the native experiment found:**

- **7/7** preferred-recipient conditions placed the hidden preferred bank first in the final blind rankings.
- **0/3** null conditions produced a flagged positive signal under the prespecified conservative decision rule.
- A separate verifier matched all **5,000** observer records to their synthetic ground truth.
- Six adversarial tests detected changed hashes, missing or altered data, impossible bank sets and inconsistent scoring.

**Figures 2 and 3:** Native inclusion frequencies and blinded controls.  
[Insert `figures/02-native-inclusion-measurements.svg`]  
[Insert `figures/03-controls-and-blind-results.svg`]

The sample-size preflight also matters: five hundred observations per condition fell below a conservative sufficient bound in the seven-bank case. The measured successes should not be converted into a guarantee that every real traffic history is easy to classify.

**Video 1:** The native source and blind experiment.  
[Embed recording after editing]

---

## I extended the local Rayls demo from six banks to seven

The official CLI demo configuration was built around at most six participants. I created a narrowly scoped research extension for a seventh bank, pinned the official source revisions and published the exact CLI/Hardhat patches. The original anonymity-selection algorithm stayed unchanged.

Bringing up a true seven-bank local environment revealed several integration details that a source-only test cannot:

- The new bank's initial deployment generated contract addresses but not its full relayer and CTS runtime configuration.
- The expanded service graph exhausted the default PostgreSQL connection limit.
- The governance service's stored database password disagreed with the existing PostgreSQL role.
- A CTS TLS certificate covered banks A–F but not the new `cts-g` hostname. My first certificate repair targeted the client certificate, not the server certificate. I kept that failed attempt in the evidence, corrected the **actual gRPC server certificate**, and verified the live handshake.

After these fixes, the Hub, seven private-chain RPCs and local public-chain RPC passed **9/9** read-only topology checks.

The live payment experiment was preregistered with exact balances and acceptance criteria before submitting its local test transactions.

---

## What the actual local Hub recorded

The seven-bank lab created a token, registered and authorized it, submitted it to the Hub, and minted **5,000 smallest token units** on Bank A.

The first genuine test payment went **A → B** and settled with a mined source receipt and destination balance. The second went **A → G**; its source transaction mined, but the destination mapping was missing at the preregistered timeout.

After fixing Bank G's CTS server certificate, its relayer caught up and the **original** payment settled—without sending a replacement source transaction.

The final balances were:

| Local institution | Final token units |
|---|---:|
| A | 4,998 |
| B | 1 |
| G | 1 |
| **Total** | **5,000 / 5,000** |

I count Bank G's original deadline as a **failed timing criterion** and its later settlement as a recovery. Combining the two into an uncomplicated “pass” would erase the most instructive part of the run.

The local Private Network Hub emitted **six mined transfer batches and 36 EnygmaTransfer event envelopes**. Every batch contained **six distinct visible participant banks**, drawn from the seven-bank local network.

A second ABI decoder, written independently of the Ethers event decoder, reconstructed the set membership. The verifier also compared **15** saved source and Hub transaction receipts against fresh local RPC responses and canonical block hashes.

**Figures 5 and 6:** Settlement accounting and the actual six-by-seven Hub membership matrix.  
[Insert `figures/05-seven-bank-settlement.svg`]  
[Insert `figures/06-real-hub-membership.svg`]

**Video 2:** Genuine local Hub events, the TLS failure and late recovery.  
[Embed recording after editing]

The local Hub data prove that these six-member sets are observable in a real researcher-controlled deployment. **They do not provide a powered longitudinal attack study against a production institution.** Six batches also cannot tell an ordinary observer which included bank received value.

---

## How to challenge the result yourself

Every claim has a different evidence class. The repository includes the complete synthetic observer ledger, separately sealed predictions and truth, native harness, pinned upstream revisions, exact seven-bank patches, raw local receipts, decoded event records, manifest checksums and independent verification scripts.

From a clean public checkout:

```bash
python3 qa/check_manifest.py
python3 qa/verify_public.py
python3 qa/verify_local_live.py --check-only
python3 qa/check_site.py --check-only
python3 qa/adversarial_checks.py
```

The archived offline checks do not require my Docker stack. A clean native rerun is available through the published Go/bootstrap instructions. Because the upstream selection function uses secure random sampling, a new run is **not expected to produce byte-for-byte identical random sets**; it must instead satisfy the same structural invariants.

The public Rayls Testnet SHA-256 anchor is documented separately in `site/public-anchor.json` once verified. Its timestamp and transaction input can authenticate **when the finalized archive digest was recorded**, not whether the earlier private-ledger history is true. It was recorded after the native experiments, not before the blind predictions.

**Figure 4:** Evidence taxonomy: native function, local Hub, reproducibility and public hash anchor.  
[Insert `figures/04-evidence-boundaries.svg`]

**Video 3:** Independent reconstruction and archive integrity.  
[Embed recording after editing]

---

## What I would test next

The most valuable next step is a larger native-to-Hub longitudinal series with multiple active senders, mixed real receivers, membership churn and padding-only finalization events. Those conditions can remove or confound the simple signal. A source-level preference signal is interesting only if the observer's actual view and operational assumptions are correctly defined.

For Rayls engineers, one architectural question follows from this experiment:

> When set membership changes over repeated transfers, what protocol or operational safeguards are intended to prevent long-term preference inference by observers who can link payments to the same sender?

This is a question about the metadata surface, not an allegation that confidentiality of payment amounts or production recipient identities has been broken.

The contribution is the **measurement**, the **controls**, the **actual local Hub observer records**, and the **reproduction trail**. Anyone can check the data without accepting the headline on trust.

---

**Sources:** [Rayls: How Enygma Works](https://docs.rayls.com/docs/how-enygma-works) · [Privacy and Auditing](https://docs.rayls.com/docs/enygma-privacy-and-auditing) · [Public Chain Reference](https://docs.rayls.com/docs/public-chain-reference) · [Source-pinned repository](https://github.com/Glimorr/enygma-anonymity-sets-over-time)

**Publication note:** Add the three edited video embeds before publishing this article. This draft is not itself a finished X publication.
