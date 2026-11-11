# Rayls Public Testnet archive-hash commitment — signing procedure

This procedure creates a **retrospective, publicly queryable checksum anchor** for the completed research archive. It is **not a preregistration timestamp** or a proof of private-ledger consensus.

### Network

- Chain: Rayls Public Testnet
- Chain ID: **7295799**
- RPC: https://testnet-rpc.rayls.com/
- Explorer: https://testnet-explorer.rayls.com/
- Gas: testnet USDr

### Unsigned transaction specification

- **From:** the user's funded Rayls testnet burner wallet, controlled by the user.
- **To:** the same wallet address.
- **Value:** 0 USDr.
- **Data:** exactly `0x` followed by the `files_merkle_equivalent_sha256` value recorded in `EVIDENCE-MANIFEST.json`.
- **Gas:** estimate against the official testnet RPC and set an adequate limit.
- **Nonce:** let the connected wallet choose the pending nonce.
- **Approval:** **only the user should approve the wallet signing prompt.** No private key or seed phrase should be sent to a website, to a chat, or to any research repository.

The corresponding unsigned JSON request is generated locally at `E:\Rayls-Nov-Week2\release\PUBLIC-TESTNET-UNSIGNED-ANCHOR.json`. It contains no secret key and is not itself a confirmed transaction.

### After the wallet signs and broadcasts

Record the mined transaction hash, status, public block hash, block number, sender, recipient, and exact transaction input. Save them in `site/public-anchor.json` as a post-release annex, with `state: confirmed`, `chain_id: 7295799`, `commitment_type: files_merkle_equivalent_sha256`, `evidence_scope` containing `retrospective`, and `verified_receipt_status: 1`.

Verify locally with:

```bash
python3 qa/check_anchor.py --live-rpc
```

This check independently queries the public chain ID, transaction input, receipt, mined block and transaction membership. **Never populate the confirmed sidecar before the public transaction is mined and matches the frozen archive digest.**

The sidecar is deliberately excluded from the archive manifest to avoid a circular hash dependency. Updating the sidecar after the public transaction does not modify any hash-covered research artifacts.
