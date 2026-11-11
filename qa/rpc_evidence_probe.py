#!/usr/bin/env python3
"""Read-only authenticated-to-local-RPC topology probe. Not Enygma transfer evidence."""
import datetime as dt
import hashlib
import json
import pathlib
import urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"evidence"/"local-rpc"
ENDPOINTS=[("hub",3445,1337)]+[
    ("bank-"+chr(ord("a")+i),8545+i,12345+i) for i in range(7)
]+[("public-local",8845,7331)]
OPENER=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def rpc(port,method,args):
    payload=json.dumps({"jsonrpc":"2.0","id":7,"method":method,"params":args}).encode()
    req=urllib.request.Request("http://127.0.0.1:"+str(port),data=payload,headers={"Content-Type":"application/json"},method="POST")
    with OPENER.open(req,timeout=8) as f:
        raw=json.load(f)
    if "error" in raw: raise RuntimeError(str(raw["error"]))
    return raw.get("result")
def probe():
    rows=[]
    for label,port,expected in ENDPOINTS:
        obj={"service":label,"rpc":"localhost:"+str(port),"expected_chain_id":expected}
        try:
            chain_id=int(rpc(port,"eth_chainId",[]),16)
            height=int(rpc(port,"eth_blockNumber",[]),16)
            block=rpc(port,"eth_getBlockByNumber",[hex(height),False])
            if not isinstance(block,dict) or block.get("hash") is None:
                raise RuntimeError("latest block unavailable")
            obj.update({"observed_chain_id":chain_id,"height":height,"latest_block_hash":block["hash"],"status":"PASS" if chain_id==expected else "FAIL"})
        except Exception as e:
            obj.update({"status":"ERROR","error_type":type(e).__name__,"error_message":str(e)[:240]})
        rows.append(obj)
        print(label,obj["status"],obj.get("observed_chain_id"),obj.get("height"))
    report={
        "observed_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope":"LOCAL_DEVELOPER_CONTROLLED_RPC_TOPOLOGY_ONLY",
        "cannot_establish":"No genuine Enygma payment, independently authenticated institutional ledger, or public testnet transaction is established by this check.",
        "counts":{"checked":len(rows),"passed":sum(x["status"]=="PASS" for x in rows)},
        "rows":rows
    }
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/"topology-report.json"
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    (OUT/"topology-report.sha256").write_text(hashlib.sha256(path.read_bytes()).hexdigest()+"  topology-report.json\n")
    print("SAVED",path,"PASS" if report["counts"]["passed"]==len(rows) else "INCOMPLETE")
    return report["counts"]["passed"]==len(rows)
if __name__=="__main__":
    raise SystemExit(0 if probe() else 1)
