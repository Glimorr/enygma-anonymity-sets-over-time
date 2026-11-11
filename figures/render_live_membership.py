#!/usr/bin/env python3
"""Figure 6: exact local Hub membership matrix; never substitute inferred recipients."""
from pathlib import Path
import json, html
R=Path(__file__).resolve().parents[1]
source=json.loads((R/"evidence/local-live-seven/receipt-reconciliation.json").read_text())
assert source["classification"]=="LOCAL_RESEARCHER_CONTROLLED_LEDGER_EVIDENCE_NOT_THIRD_PARTY_CONSENSUS"
rows=sorted(source["observed_batches"],key=lambda x:x["block"])
assert len(rows)==6 and all(len(x["members"])==6 and len(set(x["members"]))==6 for x in rows)
ids=list("ABCDEFG")
chains={12345+i:ids[i] for i in range(7)}
members=[{chains[k] for k in row["members"]} for row in rows]
counts={bank:sum(bank in row for row in members) for bank in ids}
assert set(counts)==set(ids) and sum(counts.values())==36
BG="#080611"; SURFACE="#1a122b"; GRID="#51406d"; PURPLE="#b69bf6"; LIME="#ecfb3e"; WHITE="#f7f5ff"; GREY="#c5bad9"; CYAN="#aff6d9"
esc=html.escape
def text(x,y,label,size=18,color=WHITE,weight=500,anchor="start"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Inter, Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{esc(str(label))}</text>'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="710" viewBox="0 0 1200 710" role="img" aria-labelledby="title desc">']
s+=['<title id="title">Observed Hub membership across six genuine local-chain batches</title>','<desc id="desc">A six-row by seven-bank grid: 36 filled cells represent each observed six-member anonymity set. The grid shows inclusion, not who received payment.</desc>']
s+=[f'<rect width="1200" height="710" fill="{BG}"/>']
s+=['<defs><linearGradient id="haze"><stop stop-color="#452969" stop-opacity=".75"/><stop offset="1" stop-color="#120d24" stop-opacity=".1"/></linearGradient><filter id="blur"><feGaussianBlur stdDeviation="45"/></filter></defs>']
s+=['<ellipse cx="870" cy="130" rx="360" ry="160" fill="url(#haze)" opacity=".5" filter="url(#blur)"/>']
s += [f'<rect x="55" y="41" width="5" height="43" rx="2.5" fill="{LIME}"/>']
s += [text(76,70,"Six authentic Hub batches. Seven registered banks.",30,WHITE,850),text(76,106,"Measured membership — never a recipient-deanonymization claim",17,GREY)]
s += [f'<rect x="56" y="142" width="1088" height="445" rx="19" fill="{SURFACE}" stroke="{GRID}"/>']
s += [text(89,188,"MINED LOCAL HUB BLOCK",13,CYAN,800),text(300,188,"OBSERVED ANONYMITY-SET MEMBER",13,CYAN,800)]
x0=326;step=108;yb=245;ystep=47
for j,bank in enumerate(ids):
    x=x0+j*step
    s.append(text(x,228,bank,16,WHITE,850,"middle"))
for i,row in enumerate(rows):
    y=yb+i*ystep
    s += [text(89,y+20,f"#{i+1:02d}",16,PURPLE,850),text(139,y+20,f"block {row['block']}",13,GREY)]
    for j,bank in enumerate(ids):
        x=x0+j*step
        present=bank in members[i]
        fill="#293319" if present else "#201930"
        stroke="#d6ee4f" if present else "#4a3d68"
        glow=f'<rect x="{x-34}" y="{y-6}" width="68" height="37" rx="10" fill="{LIME}" opacity=".06"/>' if present else ""
        s += [glow,f'<rect x="{x-33}" y="{y-5}" width="66" height="34" rx="9" fill="{fill}" stroke="{stroke}"/>',
              text(x,y+17,"●" if present else "—",16,LIME if present else "#907fae",800,"middle")]
s += [f'<line x1="90" y1="535" x2="1105" y2="535" stroke="{GRID}"/>']
s += [text(89,564,"APPEARANCES",13,CYAN,800)]
for j,bank in enumerate(ids):s.append(text(x0+j*step,563,f"{counts[bank]}/6",17,LIME if counts[bank]==6 else WHITE,800,"middle"))
s += [f'<rect x="55" y="608" width="1090" height="40" rx="9" fill="#272039" stroke="#4d3a63"/>',
      text(80,633,"36 included cells = 6 observed batches × 6 members. Inclusion is NOT evidence of payment receipt.",14,GREY,500)]
s += [f'<line x1="57" y1="660" x2="1143" y2="660" stroke="{GRID}"/>',text(58,675,"SOURCE: RESEARCHER-CONTROLLED PRIVATE NETWORK HUB • RECEIPTS + INDEPENDENT ABI DECODING",12,CYAN,700)]
s.append("</svg>")
data="\n".join(s)+"\n"
path=R/"figures/06-real-hub-membership.svg"
path.write_text(data,encoding="utf-8")
(R/"site/assets/06-real-hub-membership.svg").write_text(data,encoding="utf-8")
print("FIGURE_06_FROM_LIVE_RECEIPTS",str(path),"memberships",sum(counts.values()),"counts",counts)
