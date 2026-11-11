# Seven-participant Enygma live transfer — preregistered protocol v1

**Experiment type:** controlled, local, researcher-operated Rayls private network.  
**Preparation date:** November 11, 2026.  
**Status of this protocol at creation:** No fresh Enygma trial launched.

## Research purpose

Test whether a fully configured seven-participant local Rayls network can process genuine Enygma payments from Bank A to Banks B and G, including verifiable Private Network Hub event records. This is a feasibility and native-versus-chain boundary check for the broader source-level anonymity-set investigation.

## Network and controls

- Hub: chain ID 1337 (local Besu).
- Seven Sovereign ledgers: A–G, chain IDs 12345–12351 respectively.
- Local public test chain: 7331; **not** Rayls Public Testnet.
- Hub and seven ledgers must first answer read-only JSON-RPC with expected chain IDs and matching latest block hashes.
- Research-only local CLI and Hardhat extensions must be accompanied by pinned upstream source revisions and exact patches.
- Local development CTS certificate must authenticate cts-g using the local development CA. Private keys are not release artifacts.

## Prespecified procedure

1. Record baseline RPC heights, block hashes, event counts and deployed contract addresses before the first transfer.
2. Create a fresh EnygmaTokenExample on A with a unique study token identifier. Register and approve it through the local Hub's TokenRegistry.
3. Mint exactly 5000 smallest token units to the funded local test signer on A. Verify the mint receipt and exact balance.
4. Transfer **1 unit A→B**. Record source transaction hash and receipt. Await the destination mint and verify B balance = 1, A balance = 4999.
5. Transfer **1 unit A→G**. Record source transaction hash and receipt. Await the destination mint and verify G balance = 1, B balance = 1, A balance = 4998.
6. Independently collect Hub transaction receipts and EnygmaTransfer events covering the measured interval. For each, record contract, block hash, transaction index, status, event topic and participant set if actually decoded from the pinned ABI.
7. Label transactions that are unmined, reverted, incomplete or timed out as such and preserve all raw errors. Do not silently re-run failed cases with changed conditions.
8. Run a separate read-only verifier and compare the Hub records with the source and destination state observations.

## Success criteria

**Local transfer feasibility** requires authenticated-by-local-RPC mined source receipts, Hub Enygma event/receipt evidence and exact source/destination balance reconciliation for both transfers. Mere service health or a transaction hash is not sufficient.

**Longitudinal privacy inference** requires an additional preregistered sequence of transactions large enough for the chosen statistical analysis. Two transfers do not establish receiver-frequency inference, deanonymization or a production protocol weakness.

A fresh real-world third-party verifier and a Rayls Public Testnet archive commitment are separate evidence classifications.

## Evidence preservation and provenance

- Source revisions: relayer b01b427de4cfc2ac66e75eba0d5070b73a3b137c, contracts ed8863885c8ed5d5d317d47a34c063907192687a, CLI c356f9211b168c643d8f25d26df709af7dc4dd92.
- Preserve raw receipts, not only interpreted outputs.
- Preserve failed attempts without changing the original protocol.
- Do not publish local dev wallet keys, operator credentials, private certificates or internal URLs.
- Any later substantive change receives a new protocol version; do not rewrite this file.

**Interpretation boundary:** This network is researcher-controlled and local. Independent external validator consensus is not established by reading two RPC endpoints served by our own deployment.
