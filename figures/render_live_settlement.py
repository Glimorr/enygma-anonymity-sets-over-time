#!/usr/bin/env python3
"""Data-driven editorial figure of the preregistered local seven-bank transfer trial."""
from pathlib import Path
import json,html,hashlib
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/"evidence/local-rpc/live-seven-preregistered-trial-state.json").read_text())
r=json.loads((ROOT/"evidence/local-live-seven/receipt-reconciliation.json").read_text())
assert r["settlement"]["unreconciled_units"]=="0"
assert s["observations"]["reconciliation"]["noNewSourceTransaction"] is True
assert all(int(s["observations"]["reconciliation"][k])==v for k,v in (("bankA",4998),("bankB",1),("bankG",1)))
assert r["hub_enygma_transfer_envelopes"]==36 and r["hub_enygma_batches_with_six_members"]==6
e=html.escape
txB=s["transactions"]["sendB"]["hash"]
txG=s["transactions"]["sendG"]["hash"]
short=lambda x:x[:12]+"…"+x[-6:]
FG="#f6f4ff";GR="#ecfb3e";LV="#b69bf6";MU="#b8afd0";BG="#080611";CA="#aff6d9";AM="#ffcc92"
parts=[
'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Local A to B and A to G payment settlement paths: both finally settled, but G missed the preregistered deadline" width="1200" height="680" viewBox="0 0 1200 680">',
'<defs><linearGradient id="bg5" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#1b1531"/><stop offset=".65" stop-color="#090713"/><stop offset="1" stop-color="#1b1232"/></linearGradient><filter id="blur5"><feGaussianBlur stdDeviation="15"/></filter><linearGradient id="line5" x1="0" x2="1"><stop stop-color="#aff6d9"/><stop offset="1" stop-color="#ecfb3e"/></linearGradient></defs>',
'<rect width="1200" height="680" fill="url(#bg5)"/>',
'<circle cx="570" cy="320" r="240" fill="#825bc4" opacity=".12" filter="url(#blur5)"/>',
f'<rect x="48" y="42" width="5" height="43" rx="2" fill="{GR}"/>',
f'<text x="68" y="73" font-family="Arial,sans-serif" font-weight="800" font-size="31" fill="{FG}">Two local payments. One delayed destination.</text>',
f'<text x="69" y="109" font-family="Arial,sans-serif" font-size="17" fill="{MU}">Original receipts + independent RPC reconciliation in a seven-bank laboratory</text>',
'<path d="M48 145 H1152" stroke="#51406c"/>',
'<rect x="60" y="190" width="293" height="326" rx="19" fill="#1b1530" stroke="#9d7fcd" stroke-width="1.5"/>',
f'<text x="87" y="230" font-family="Arial,sans-serif" font-size="16" font-weight="800" fill="{LV}">BANK A / SENDER</text>',
f'<text x="87" y="292" font-family="Arial,sans-serif" font-size="52" font-weight="850" fill="{FG}">5,000</text>',
f'<text x="90" y="316" font-family="Arial,sans-serif" font-size="14" fill="{MU}">minted smallest units</text>',
'<path d="M87 345 H327" stroke="#5d487e"/>',
f'<text x="87" y="395" font-family="Arial,sans-serif" font-size="17" fill="{MU}">Final source balance</text>',
f'<text x="87" y="455" font-family="Arial,sans-serif" font-size="52" font-weight="850" fill="{GR}">4,998</text>',
'<circle cx="370" cy="350" r="7" fill="#ecfb3e"/>',
'<path d="M355 350 H444" stroke="#b69bf6" stroke-width="3" stroke-linecap="round"/>',
'<path d="M436 344 L447 350 L436 356" stroke="#ecfb3e" stroke-width="2" fill="none"/>',
'<rect x="453" y="217" width="289" height="262" rx="21" fill="#201434" stroke="#b69bf6" stroke-width="2"/>',
'<circle cx="596" cy="328" r="99" fill="#9e6cf418" stroke="#ac80ec70"/>',
'<circle cx="596" cy="328" r="78" fill="#24183e" stroke="#ecfb3e70" stroke-dasharray="8 9"/>',
f'<text x="596" y="311" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="800" fill="{CA}" letter-spacing="2">LOCAL HUB</text>',
f'<text x="596" y="351" text-anchor="middle" font-family="Arial,sans-serif" font-size="23" font-weight="850" fill="{FG}">ENYGMA</text>',
f'<text x="596" y="387" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="{MU}">6 observed batches</text>',
f'<text x="596" y="406" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="{MU}">36 encrypted envelopes</text>',
'<path d="M744 283 L807 283 L836 260" stroke="#aff6d9" stroke-width="3" fill="none"/>',
'<path d="M826 258 L838 260 L834 272" stroke="#aff6d9" stroke-width="2" fill="none"/>',
'<path d="M744 399 L801 399 L836 418" stroke="#ecfb3e" stroke-width="3" fill="none"/>',
'<path d="M829 406 L839 419 L824 421" stroke="#ecfb3e" stroke-width="2" fill="none"/>',
'<rect x="842" y="182" width="302" height="166" rx="18" fill="#16252b" stroke="#aff6d9" stroke-width="1.5"/>',
f'<text x="866" y="219" font-family="Arial,sans-serif" font-weight="800" font-size="15" fill="{CA}">BANK B / DESTINATION</text>',
f'<text x="868" y="264" font-family="Arial,sans-serif" font-weight="850" font-size="40" fill="{FG}">1 <tspan font-size="17" fill="{MU}">unit</tspan></text>',
f'<text x="868" y="304" font-family="Arial,sans-serif" font-size="16" fill="{GR}">SETTLED IN OBSERVATION WINDOW</text>',
f'<text x="868" y="330" font-family="monospace" font-size="11" fill="{MU}">TX  {e(short(txB))}</text>',
'<rect x="842" y="370" width="302" height="203" rx="18" fill="#292033" stroke="#ffcc92" stroke-width="1.5"/>',
f'<text x="866" y="407" font-family="Arial,sans-serif" font-weight="800" font-size="15" fill="{AM}">BANK G / LATE SETTLEMENT</text>',
f'<text x="868" y="447" font-family="Arial,sans-serif" font-weight="850" font-size="40" fill="{FG}">1 <tspan font-size="17" fill="{MU}">unit</tspan></text>',
f'<text x="868" y="477" font-family="Arial,sans-serif" font-size="15" fill="{AM}">INITIAL TIMEOUT • NO REPLAY</text>',
f'<text x="868" y="499" font-family="Arial,sans-serif" font-size="14" fill="{GR}">TLS CERTIFICATE CORRECTED</text>',
f'<text x="868" y="533" font-family="monospace" font-size="11" fill="{MU}">TX  {e(short(txG))}</text>',
'<path d="M55 609 H1147" stroke="#53446d"/>',
f'<text x="62" y="641" font-family="Arial,sans-serif" font-size="16" font-weight="800" fill="{GR}">RECONCILED 5,000 / 5,000</text>',
f'<text x="1143" y="640" text-anchor="end" font-family="Arial,sans-serif" font-size="14" fill="{MU}">RESEARCHER-CONTROLLED LOCAL BLOCKCHAIN • NOT RAYLS PUBLIC TESTNET</text>',
'</svg>'
]
out=ROOT/"figures/05-seven-bank-settlement.svg"
out.write_text("\n".join(parts)+"\n")
(ROOT/"site/assets"/out.name).write_bytes(out.read_bytes())
print("FIGURE_5_REAL_LOCAL_LEDGER_SETTLEMENT_CREATED",len(parts),"svg elements",hashlib.sha256(out.read_bytes()).hexdigest()[:16])
