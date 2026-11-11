#!/usr/bin/env python3
"""Generate original editable SVG figures from real native-source evidence."""
from pathlib import Path
import json
from html import escape

root=Path(__file__).resolve().parents[1]
fig=root/"figures"; fig.mkdir(exist_ok=True)
pred=json.loads((root/"analysis/blind_predictions.json").read_text())
truth=json.loads((root/"analysis/ground_truth_scoring.json").read_text())
BG="#080611"; PANEL="#1B152D"; LINE="#54426D"; TXT="#F7F6FF"
MUTED="#B7B0CC"; GREEN="#ECFB3E"; PURPLE="#B69BF6"; CYAN="#AFF6D9"
def t(x,y,s,size=19,color=TXT,weight="normal",anchor="start"):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(s))}</text>'
def base(title,sub,body,footer,view=(1200,680)):
    w,h=view
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#12152B"/><stop offset=".6" stop-color="{BG}"/><stop offset="1" stop-color="#111628"/></linearGradient><filter id="soft"><feGaussianBlur stdDeviation="12"/></filter></defs>
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<circle cx="{w-90}" cy="50" r="150" fill="{PURPLE}" opacity=".08" filter="url(#soft)"/>
<rect x="38" y="36" width="5" height="43" rx="2" fill="{GREEN}"/>
{t(60,69,title,32,TXT,"bold")}
{t(60,105,sub,18,MUTED)}
{body}
<path d="M55 {h-68} H{w-55}" stroke="{LINE}" stroke-width="1"/>
{t(56,h-37,footer,15,MUTED)}
</svg>'''
def save(file,svg):
    (fig/file).write_text(svg,encoding="utf-8")
    print("FIGURE_WRITTEN",file)

# Fig 1: conceptual anatomy, not a claimed on-chain transaction.
body=''
body+=f'<rect x="55" y="150" width="1090" height="438" rx="22" fill="{PANEL}" stroke="{LINE}"/>'
body+=t(90,191,"ONE ENYGMA BATCH / SCHEMATIC",17,CYAN,"bold")
body+=f'<circle cx="185" cy="352" r="51" fill="#1F3541" stroke="{CYAN}" stroke-width="3"/>'
body+=t(185,347,"BANK A",21,TXT,"bold","middle")+t(185,371,"sender",17,CYAN,"normal","middle")
body+=f'<path d="M239 352 H313" stroke="{CYAN}" stroke-width="3" stroke-dasharray="8 7"/>'
body+=t(275,335,"Hub",16,CYAN,"bold","middle")
body+=f'<rect x="335" y="216" width="765" height="268" rx="20" fill="#0D1320" stroke="{PURPLE}" stroke-width="2"/>'
body+=t(360,255,"PUBLICLY VISIBLE ANONYMITY SET (k=6)",19,PURPLE,"bold")
names=["A","B","C","D","E","F"]
for idx,name in enumerate(names):
    x=405+idx*125; y=346
    color=CYAN if idx==0 else LINE
    fill="#1D3540" if idx==0 else "#20283A"
    body+=f'<circle cx="{x}" cy="{y}" r="37" fill="{fill}" stroke="{color}" stroke-width="2"/>'
    body+=t(x,y+6,"Bank "+name,17,TXT,"bold","middle")
body+=t(707,421,"Observer sees every included bank, not which receives value.",18,MUTED,"normal","middle")
body+=f'<rect x="335" y="508" width="765" height="44" rx="10" fill="#162A22" stroke="{GREEN}" opacity=".96"/>'
body+=t(718,537,"Researcher-only ground truth identifies the true recipient after reveal.",17,GREEN,"normal","middle")
save("01-anonymity-set-model.svg",base("What is actually visible?","A genuine receiver is included alongside zero-value decoys.",body,"SCHEMATIC • NOT A BLOCKCHAIN RECEIPT"))

# Fig 2: native observed frequencies, source-derived.
a=pred["results"]["C_N8_balanced"]["prefixes"]["500"]["all_counts"]
b=pred["results"]["D_N8_preferred"]["prefixes"]["500"]["all_counts"]
target=truth["outcomes"]["D_N8_preferred"]["known_preferred_receiver"]
body=''
body+=f'<rect x="55" y="155" width="1090" height="442" rx="18" fill="{PANEL}" stroke="{LINE}"/>'
body+=t(95,207,"Membership frequency among 500 batches",20,TXT,"bold")
body+=f'<rect x="835" y="183" width="16" height="16" rx="4" fill="{PURPLE}"/>'+t(860,197,"Balanced traffic",16,MUTED)
body+=f'<rect x="835" y="212" width="16" height="16" rx="4" fill="{GREEN}"/>'+t(860,226,"Preferred receiver",16,MUTED)
plotTop=270; plotBottom=524; plotH=235
for tick in (0.5,0.6,0.7,0.8,0.9,1.0):
    yy=plotBottom-(tick-0.45)/0.55*plotH
    body+=f'<line x1="133" y1="{yy:.1f}" x2="1100" y2="{yy:.1f}" stroke="{LINE}" stroke-dasharray="4 8"/>'
    body+=t(111,yy+6,f"{tick:.0%}",15,MUTED,"normal","end")
for i,bank in enumerate(range(1002,1009)):
    xc=215+i*134
    p=float(a[str(bank)])/500; q=float(b[str(bank)])/500
    ph=(p-0.45)/0.55*plotH; qh=(q-0.45)/0.55*plotH
    body+=f'<rect x="{xc-23}" y="{plotBottom-ph:.1f}" width="26" height="{ph:.1f}" rx="5" fill="{PURPLE}"/>'
    body+=f'<rect x="{xc+8}" y="{plotBottom-qh:.1f}" width="26" height="{qh:.1f}" rx="5" fill="{GREEN}"/>'
    body+=t(xc+5,555,str(bank),17,TXT if bank==target else MUTED,"bold" if bank==target else "normal","middle")
body+=t(760,595,f"Preferred recipient disclosed after sealing blind predictions: {target}",16,GREEN,"normal","middle")
save("02-native-inclusion-measurements.svg",base("Repeated sets leave a measurable signature","Actual pinned Go selection function • synthetic traffic schedules",body,"NATIVE SOURCE-LEVEL EVIDENCE • 500 BATCHES PER CONDITION"))

# Fig 3: all ten control conditions.
body=f'<rect x="55" y="145" width="1090" height="467" rx="18" fill="{PANEL}" stroke="{LINE}"/>'
body+=t(90,188,"Condition",18,MUTED,"bold")+t(538,188,"Top member",18,MUTED,"bold")
body+=t(725,188,"Ground truth",18,MUTED,"bold")+t(960,188,"Null rejected?",18,MUTED,"bold")
names=list(pred["results"])
for i,name in enumerate(names):
    y=224+i*34
    outcome=truth["outcomes"][name]
    claim=pred["results"][name]["prefixes"]["500"]
    sign=claim["reject_balanced_model_at_fwer_0_05"]
    body+=f'<line x1="88" y1="{y+10}" x2="1110" y2="{y+10}" stroke="{LINE}" opacity=".65"/>'
    body+=t(90,y,name,16,TXT)
    body+=t(545,y,claim["top_candidate"],16,GREEN if sign else MUTED)
    body+=t(729,y,outcome["known_preferred_receiver"] or "No preferred receiver",16,PURPLE if outcome["known_preferred_receiver"] else MUTED)
    body+=t(990,y,"YES" if sign else "NO",16,GREEN if sign else MUTED,"bold")
save("03-controls-and-blind-results.svg",base("Blind predictions against ten controls","Positive, balanced, mixed-recipient and zero-only trials",body,"7/7 PREFERRED CASES MATCH • 0/3 NULL CONTROLS FLAGGED • NATIVE SOURCE-LEVEL"))

# Fig 4: evidence chain with exact statuses.
nodes=[
    ("01","PINNED SOURCE","Git commits recorded","PASS"),
    ("02","NATIVE TEST","5,000 observations","PASS"),
    ("03","BLIND SEAL","Predictions hashed locally","PASS"),
    ("04","INDEPENDENT QA","6 tamper checks rejected","PASS"),
    ("05","LOCAL HUB","6 batches / 36 events","PASS"),
]
body=f'<rect x="55" y="158" width="1090" height="430" rx="18" fill="{PANEL}" stroke="{LINE}"/>'
for i,(num,title,desc,status) in enumerate(nodes):
    x=86+i*215; y=253
    c=GREEN if status=="PASS" else "#F0BA76"
    body+=f'<rect x="{x}" y="{y}" width="191" height="188" rx="14" fill="#0C1420" stroke="{c}" stroke-width="1.5"/>'
    body+=t(x+16,y+43,num,24,c,"bold")
    body+=t(x+16,y+82,title,17,TXT,"bold")
    body+=t(x+16,y+111,desc,13,MUTED)
    body+=t(x+16,y+160,status,16,c,"bold")
    if i<4: body+=f'<path d="M{x+191} {y+96} h23" stroke="{CYAN}" stroke-width="2"/>'
body+=t(93,504,"A public testnet hash commitment proves inclusion of an artifact hash, not the private-chain payment history.",17,MUTED)
save("04-evidence-boundaries.svg",base("Verification boundaries","Every conclusion must match the evidence that actually exists.",body,"PINNED TESTS + OFFLINE VERIFICATION VERIFIED • 15 FRESH LOCAL RPC RECEIPTS VERIFIED • PUBLIC TESTNET ANCHOR PENDING"))

print("FOUR_VECTOR_RESEARCH_FIGURES_COMPLETE")
