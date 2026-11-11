#!/usr/bin/env python3
"""Offline site QA: links, data provenance, evidence boundaries, assets, accessibility basics."""
import argparse,collections,hashlib,html.parser,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
class IndexParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.internal=[];self.asset_refs=[];self.external_blank=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get("id"):self.ids.append(d["id"])
        if tag=="a" and d.get("href","").startswith("#"):self.internal.append(d["href"][1:])
        if tag in ("script","img") and d.get("src") and not d["src"].startswith(("https:","http:")):self.asset_refs.append(d["src"])
        if tag=="link" and d.get("href") and not d["href"].startswith(("https:","http:")):self.asset_refs.append(d["href"])
        if tag=="a" and d.get("target")=="_blank" and "noopener" not in d.get("rel",""):self.external_blank.append(d.get("href",""))
def require(ok,reason):
    if not ok:raise AssertionError(reason)
def main():
    a=argparse.ArgumentParser();a.add_argument("--check-only",action="store_true");args=a.parse_args()
    html=(SITE/"index.html").read_text()
    parsed=IndexParser();parsed.feed(html)
    ids=set(parsed.ids)
    require(len(ids)==len(parsed.ids),"Duplicate HTML IDs")
    require(all(x in ids for x in parsed.internal),"Broken internal anchor")
    require(not parsed.external_blank,"target=_blank without noopener")
    missing=[p for p in parsed.asset_refs if not (SITE/p).is_file()]
    require(not missing,"Missing referenced local assets: "+str(missing))
    required=["experience.css","experience.js","polish.css","polish.js","live-data.js","live-evidence.js","bank-lens.css","bank-lens.js","data.js","public-anchor.js"]
    require(all(x in parsed.asset_refs for x in required),"Missing site script or stylesheet")
    l=(SITE/"live-data.js").read_text().strip()
    require(l.startswith("window.RAYLS_LIVE_HUB_DATA = "),"Unexpected provenance source")
    data=json.loads(l.split("=",1)[1].strip().rstrip(";"))
    rec=json.loads((ROOT/"evidence/local-live-seven/receipt-reconciliation.json").read_text())
    require(data["hubBatches"]==len(rec["observed_batches"])==6,"Hub batches do not match receipts")
    require(data["envelopes"]==rec["hub_enygma_transfer_envelopes"]==36,"Envelope count mismatch")
    require(data["recheckedReceipts"]==rec["fresh_receipts_compared_to_live_rpc"]==15,"Receipt check count mismatch")
    require(set(data["bankIDs"])==set("ABCDEFG"),"Unexpected local bank IDs")
    for obs,real in zip(data["batchRows"],sorted(rec["observed_batches"],key=lambda x:x["block"])):
        require(obs["block"]==real["block"] and obs["txHash"]==real["tx_hash"],"Hub batch provenance mismatch")
        require(len(obs["members"])==len(set(obs["members"]))==6,"Bad six-bank set")
        require(set(obs["members"])=={chr(v-12345+ord("A")) for v in real["members"]},"Incorrect bank mapping")
    require(data["bankBalances"]=={"A":"4998","B":"1","G":"1","total":"5000"},"Final accounting mismatch")
    require("prefers-reduced-motion" in (SITE/"experience.css").read_text(),"Reduced motion CSS missing")
    require('id="motion-toggle"' in html and 'id="journey"' in html,"Motion controls missing")
    require('id="hub-matrix"' in html and "bank-lens.js" in html,"Receipt explorer missing")
    require('aria-label' in html and 'alt=' in html,"Accessible labels missing")
    figure_paths=list((SITE/"assets").glob("??-*.svg"))
    require(len(figure_paths)==6,"Expected six figures")
    require("LOCAL HUB" in (ROOT/"figures/05-seven-bank-settlement.svg").read_text(),"Local Hub settlement visual missing")
    require("36 included cells" in (ROOT/"figures/06-real-hub-membership.svg").read_text(),"Hub membership caveat missing")
    require("Public Testnet evidence commitments remain pending" in html,"Public evidence boundary missing")
    require(("utm_source="+"chatgpt.com") not in html,"Tracking URL found")
    for p in required:
        js=(SITE/p).read_text()
        require(not re.search(r"\b(?:sendBeacon|XMLHttpRequest)\b",js),"Unexpected telemetry API "+p)
    records=sorted([p for p in SITE.rglob("*") if p.is_file() and p.name not in ("_qa_viewport.html","_qa_overflow.html","_qa_interactions.html","_qa_depth.html","_qa_metrics.html")])
    size=sum(p.stat().st_size for p in records)
    audit={"result":"PASS","scope":"STANDALONE_OFFLINE_STATIC_SITE","html_ids":len(ids),"links_to_local_assets":len(parsed.asset_refs),"figure_count":len(figure_paths),"hub_mined_batches":len(data["batchRows"]),"hub_encrypted_event_envelopes":36,"receipt_rechecks":15,"source_data_sha256":hashlib.sha256((SITE/"live-data.js").read_bytes()).hexdigest(),"site_runtime_asset_bytes":size,"javascript_network_request_dependencies":0,"reduced_motion":True,"public_rayls_testnet_commitment":"PENDING"}
    if not args.check_only:(ROOT/"qa/site-audit.json").write_text(json.dumps(audit,indent=2)+"\n")
    print("SITE_EVIDENCE_AND_ACCESSIBILITY_STATIC_AUDIT_PASS",json.dumps(audit,sort_keys=True))
if __name__=="__main__":
    if (ROOT/"site/public-anchor.json").is_file() and (ROOT/".git").exists():
        import subprocess,sys
        print("POST_RELEASE_CHECKOUT: verifying the frozen evidence and later public annex separately",flush=True)
        subprocess.run([sys.executable,str(ROOT/"qa/verify_published_release.py"),"--manifest-only"],check=True)
    else:
        main()
