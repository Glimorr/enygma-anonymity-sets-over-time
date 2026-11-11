# Independent evaluator audit — Rayls Enygma longitudinal privacy study

**Goal:** maximize scientific quality, provenance and reproducibility; no score is guaranteed. This audit uses the stricter evaluation priorities observed from October Week 3 onward.

| Criterion | Current evidence | Evaluator risk and final handling |
|---|---|---|
| Relevance | Real Rayls Enygma privacy-selection function and seven-bank local Hub | Strong connection; do not generalize to Retail or production institutions |
| Originality | Question about longitudinal preferred-recipient inference, not ciphertext size or recovery | Clearly distinguish the known statistical-disclosure idea from new implementation-specific data |
| Effort | 5,000 native outputs, ten controls, seven-bank environment, CTS/G recovery, real receipts, custom visual explorer | Publish both source and on-ledger verification |
| Causal controls | 7 preferred scenarios, 3 negatives including padding-only, sealed blind predictions | Do not claim more than a source-level model |
| Chronology | Blind predictions SHA256 and original source/testing dates, local protocol committed before the live payment test | A **later** public Testnet anchor proves archive integrity/timestamp after experiments, not preregistration before predictions |
| Evidence authentication | 15 saved source/Hub receipts rechecked against live local RPC and block hashes, independent ABI decoder | Still researcher-controlled ledger. No externally governed validator consensus claimed |
| Falsification | Six adversarial verifier checks; null controls did not trigger spurious positives | Keep failures and the G timeout unedited |
| Recovery integrity | Original G source payment eventually settled; 5,000/5,000 base units accounted for | Never rewrite the initial timeout as an on-time pass |
| Reproducibility | Pinned official Go relayer/CLI/contracts, exact patches, deterministic archived verifier, clean GitHub Actions runner | Crypto/rand native reruns test invariants, not identical sample bytes |
| Public on-chain artifact | Final SHA-256 archive-root commitment on Rayls Public Testnet when mined | Must link transaction hash and independently check from/to, status, data and chain ID |
| Presentation | Six original figures, interactive 3D storytelling, actual Hub bank lens, keyboard/motion QA | Motion illustrates mechanism; real measurements are separately labeled |
| Publication | Public repo and GitHub Pages; three voice-overs, recording commands and X article draft | User records/edits videos and publishes article/Discord |

## Non-negotiable wording

- **Native source-level output:** 5,000 real outputs from a pinned Go function fed synthetic schedules.
- **Genuine local blockchain:** six mined local Private Network Hub batches, 36 EnygmaTransfer envelopes, 15 fresh local RPC cross-checks.
- **Late recovery:** G initially missed the preregistered deadline, then settled after CTS server certificate repair, without a second source payment.
- **Public Testnet hash anchor:** cryptographic commitment only; not proof that private transfers were validated by an independent public blockchain network.
- **Not proven:** production deanonymization, universal inference accuracy, or outside-chain consensus.

## Acceptance gates

- [x] Raw synthetic observations, separate ground truth and sealed predictions available
- [x] Native reproduction and six adversarial integrity tests pass
- [x] Source revision pins and exact seven-bank extension available
- [x] Mined A→B and A→G source receipts preserved
- [x] G timing failure retained and subsequent 5,000/5,000 reconciliation proven
- [x] 6 Hub anonymity-set batches and 36 event envelopes decoded
- [x] 15 source/Hub receipts checked against fresh local RPC
- [x] Local mobile/desktop/browser interactions, six figures and provenance links tested
- [ ] Public testnet hash anchor independently mined and verified
- [ ] Final commit, GitHub workflow runs and live Pages content checked
- [ ] User's three videos recorded and edited with accurate voiceovers
- [ ] X article and Discord submission published by user

This is a working audit, not a claim of a 10/10 RP award. Any final evaluation must be based on the actual submitted artifact and verified evidence.
