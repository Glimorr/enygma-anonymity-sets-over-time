# Recording guide — Enygma anonymity-set research

Three silent screen recordings; voice-over is added after editing. **All commands below are read-only**. Run from the root of the final public GitHub checkout or from the saved release on E:, not from a live Docker console that exposes credentials.

## Before any recording

Open the published research site, verify the heading and badges, and arrange the browser and terminal at readable zoom. Do not expose private wallet keys, local `.env` files, live Docker settings, or internal credential files. The site is an independent research demonstration; local Hub receipts are **not** a public Rayls Testnet payment.

## Video 1 — Can repeated six-member sets leak preference?

**Approx. 2–3 min.** On screen:
1. Title and 3D walkthrough: one payment, changing decoys, blind inference.
2. Figure 1 showing the observer model, Figure 2 showing observed native-function selection frequencies.
3. Terminal read-only snapshot:

```bash
python3 qa/showcase_readonly.py --part source
python3 qa/verify_public.py
```

4. Website experiment: change scenario to preferred vs balanced and change sample prefix. The controls should show why a top-ranked candidate is not automatically a significant signal.

**Voice-over (record afterward):**

“One confidential payment can hide its receiving bank among decoys. But what if the same institution receives repeatedly? We inspected Rayls’ pinned Go relayer rather than recreating its selection logic. Our harness ran that production selection function on ten controlled synthetic schedules, producing five thousand observable sets. We sealed blind rankings before comparing them with the separate synthetic recipient labels. The preferred bank ranked first in seven of seven positive cases, and none of the three controls triggered a false signal. That result belongs to the controlled source-level model. It does not prove that anyone has identified recipients on a production bank network.”

## Video 2 — Real Hub events, an unexpected timeout, recovery

**Approx. 3–4 min.** On screen:
1. Hub receipt explorer and newly added bank membership lens. Click Bank F, then Bank A; show six real batches, each containing six banks.
2. Figures 5 and 6, emphasizing that including a bank in a set does **not** prove it received value.
3. Terminal snapshot:

```bash
python3 qa/showcase_readonly.py --part hub
python3 qa/verify_local_live.py --check-only
```

4. Show the final 4,998 / 1 / 1 balances, and the note that G settled after the preregistered deadline.

**Voice-over:**

“The source-level tests raised a concrete question: can we observe the same public membership fields in a real Enygma Hub? We extended the local official six-bank demo to seven institutions without changing the relayer’s anonymity selection algorithm. In this researcher-controlled laboratory, we captured six mined Hub batches and thirty-six encrypted event envelopes. A payment from A to B settled. The payment to G mined at the source but initially missed the delivery deadline. The problem was a TLS hostname mismatch in the new bank’s CTS server certificate. After correcting the server certificate, the original transfer settled without replay. Final balances reconciled all five thousand token units. That is genuine local-ledger evidence, with a failed timing criterion retained—not independent external consensus.”

## Video 3 — Audit the evidence, do not trust captions

**Approx. 2–3 min.** On screen:
1. Public repository, pinned Rayls source revisions and the evidence manifest.
2. Run:

```bash
python3 qa/showcase_readonly.py --part integrity
python3 qa/check_manifest.py
python3 qa/check_site.py --check-only
python3 qa/verify_local_live.py --check-only
```

3. Show Figure 4’s evidence classes, the independently reproduced Hub observations, and the public Rayls Testnet hash anchor **only after its receipt and hash comparison have been verified**.

**Voice-over:**

“We have separated three kinds of evidence. First, original output from an unmodified pinned source function under synthetic schedules. Second, mined receipts from our own local seven-bank Hub, decoded and checked against the same local chain by an independent verifier. Third, an optional public Rayls Testnet hash commitment that timestamps the final archive. That public commitment does not turn our local receipts into externally governed transactions. The repository includes raw rows, blinded rankings, revealed truth, deterministic scoring, source pins, exact patches, decoded receipts, and adversarial checks. Anyone can rerun the offline audit without our machine. The contribution is a reproducible measurement of a potential longitudinal metadata signal—and a clear record of which claims the data actually support.”

## Recording-specific accuracy checks

- Never say “5,000 on-chain payments.” There were **5,000 native-function observations on synthetic schedules**.
- Never say the G transfer passed on time; it **settled late after the initial timeout**.
- Do not present a locally replayed saved receipt as independently authenticated public consensus.
- Never label an unmined transaction, a local block, or a historical saved-audit check “publicly on-chain verified.”
- Do not scroll beyond the meaningful command output; keep captions readable.
- The user's role remains to record, edit, add voice-overs and publish X/Discord. All evidence generation is already complete.
