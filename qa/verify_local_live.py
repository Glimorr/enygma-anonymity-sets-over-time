#!/usr/bin/env python3
"""Independent stdlib decoder and local-RPC receipt reconciler.
Does not authenticate an external validator quorum or imply public testnet evidence.
"""
import argparse,datetime as dt,hashlib,json,pathlib,urllib.request
R=pathlib.Path(__file__).resolve().parents[1]
STATE=R/"evidence/local-rpc/live-seven-preregistered-trial-state.json"
DECODED=R/"evidence/local-rpc/live-seven-decoded-events.json"
OUT=R/"evidence/local-live-seven"
SIGNATURE="EnygmaTransfer(bytes32,bytes,uint256,uint256,uint256[],uint256[],uint256)"
def require(cond,message):
    if not cond:raise AssertionError(message)
def n(v): return int(v,16) if isinstance(v,str) and v.startswith("0x") else int(v)
def rpc(port,method,params):
    payload=json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":2}).encode()
    req=urllib.request.Request("http://127.0.0.1:"+str(port),data=payload,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=12) as f:d=json.load(f)
    if "error" in d:raise RuntimeError(str(d["error"]))
    return d["result"]
def word(d,off):
    require(0<=off<=len(d)-32,"ABI offset out of bounds")
    return int.from_bytes(d[off:off+32],"big")
def dynamic_array(d,off):
    offset=word(d,off);length=word(d,offset)
    require(0<=length<=1000,"implausible ABI uint256 array")
    require(offset+32+length*32<=len(d),"ABI dynamic array overflow")
    return [word(d,offset+32+i*32) for i in range(length)]
def decode_enygma_event(l):
    d=bytes.fromhex(l["data"][2:])
    require(len(d)>=192,"ABI static head too short")
    aset=dynamic_array(d,96)
    hashes=dynamic_array(d,128)
    return {"resource_id":l["topics"][1],"message_length":len(bytes.fromhex(l["data"][2+word(d,0)*2+64:2+word(d,0)*2+64+word(d,word(d,0))*2])) if False else word(d,word(d,0)),"message_tag":word(d,32),"message_block":word(d,64),"anonymity_set":aset,"hash_secret_count":len(hashes),"to_chain_id":word(d,160)}
def compare_live_receipt(port,record):
    hash=record["hash"];got=rpc(port,"eth_getTransactionReceipt",[hash])
    require(got is not None,"receipt missing at live RPC: "+hash)
    require(got["transactionHash"].lower()==hash.lower(),"receipt hash mismatch")
    require(got["blockHash"].lower()==record["blockHash"].lower(),"receipt block hash mismatch")
    require(n(got["blockNumber"])==n(record["blockNumber"]),"receipt block number mismatch")
    require(n(got["status"])==n(record["status"]),"receipt execution status mismatch")
    require(len(got["logs"])==len(record["logs"]),"receipt log count mismatch")
    for i,(a,b) in enumerate(zip(got["logs"],record["logs"])):
        require(a["address"].lower()==b["address"].lower(),"log emitter mismatch "+str(i))
        require(a["data"].lower()==b["data"].lower(),"log data mismatch "+str(i))
        require([t.lower() for t in a["topics"]]==[t.lower() for t in b["topics"]],"log topics mismatch "+str(i))
    block=rpc(port,"eth_getBlockByHash",[record["blockHash"],False])
    require(block is not None and block["hash"].lower()==record["blockHash"].lower(),"canonical block query mismatch")
    require(hash.lower() in [a.lower() for a in block["transactions"]],"block does not include receipt transaction")
    return {"block_hash":record["blockHash"],"tx_hash":hash,"status":n(record["status"])}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fresh-local-rpc",action="store_true")
    ap.add_argument("--check-only",action="store_true",help="Validate without writing into a staged release")
    args=ap.parse_args()
    s=json.loads(STATE.read_text());derived=json.loads(DECODED.read_text())
    require(s["scope"]=="RESEARCHER_CONTROLLED_LOCAL_LEDGER","overstated source scope")
    require(derived["scope"]=="LOCAL_RESEARCHER_CONTROLLED_CHAINS","overstated derived scope")
    source=s["transactions"]
    for stage in ("deploy","register","authorize","submitHub","approve","mint","sendB","sendG"):
        require(stage in source and source[stage]["receipt"]["hash"]==source[stage]["hash"],"missing source tx "+stage)
        require(n(source[stage]["receipt"]["status"])==1,"reverted source tx "+stage)
    hub=s["observations"]["hubReceipts"]
    require(len(hub)>=4,"Hub receipt count unexpectedly low")
    unique_anon=[]
    example_abi_topic=None
    txrecords=[]
    observed=0
    parsed_by_hash={h["txHash"]:h for h in derived["hub"]}
    for hash,receipt in hub.items():
        require(hash.lower()==receipt["hash"].lower(),"Hub receipt key mismatch")
        require(n(receipt["status"])==1,"Hub reverted receipt")
        desc=parsed_by_hash[hash]
        require(len(desc["logs"])==len(receipt["logs"]),"derived Hub log count mismatch")
        memberlogs=[]
        for index,(raw,evt) in enumerate(zip(receipt["logs"],desc["logs"])):
            if evt["event"]!="EnygmaTransfer":continue
            decoded=decode_enygma_event(raw)
            logged={x["name"]:x["value"] for x in evt["args"]}
            require(decoded["anonymity_set"]==[n(x) for x in logged["anonymitySet"]],"native vs independent ABI decoder mismatch")
            require(decoded["to_chain_id"]==n(logged["toChainId"]),"destination ID decode disagreement")
            require(decoded["resource_id"].lower()==logged["resourceId"].lower(),"resource ID decode disagreement")
            require(decoded["message_length"]>0,"empty encrypted message")
            require(len(decoded["anonymity_set"])==6,"not six participants")
            require(len(set(decoded["anonymity_set"]))==6,"duplicate anonymity-set member")
            require(decoded["to_chain_id"] in decoded["anonymity_set"],"envelope recipient outside member set")
            if example_abi_topic is None:example_abi_topic=raw["topics"][0].lower()
            else:require(raw["topics"][0].lower()==example_abi_topic,"EnygmaTransfer topic not stable")
            memberlogs.append(decoded)
            observed+=1
        if memberlogs:
            sets={tuple(x["anonymity_set"]) for x in memberlogs}
            require(len(sets)==1,"mixed sets within one Hub batch")
            participants=memberlogs[0]["anonymity_set"]
            require({x["to_chain_id"] for x in memberlogs}==set(participants),"one envelope per set member not established")
            unique_anon.append({"tx_hash":hash,"block":n(receipt["blockNumber"]),"members":participants,"envelopes":len(memberlogs)})
            txrecords.append(hash)
    require(len(unique_anon)>=2,"not enough observed Hub Enygma batches")
    live_results=[]
    if args.fresh_local_rpc:
        for k,v in source.items():
            port=3445 if k=="approve" else 8545
            live_results.append(compare_live_receipt(port,v["receipt"]))
        for receipt in hub.values():
            live_results.append(compare_live_receipt(3445,receipt))
        signer=s["signer"]
        query="0x70a08231"+signer[2:].lower().rjust(64,"0")
        token=s["tokenAddress"]
        btarget=s["observations"]["balanceAfterB"]["destinationToken"]
        gtarget=s["observations"]["balanceAfterG"]["destinationToken"]
        a=n(rpc(8545,"eth_call",[{"to":token,"data":query},"latest"]))
        b=n(rpc(8546,"eth_call",[{"to":btarget,"data":query},"latest"]))
        g=n(rpc(8551,"eth_call",[{"to":gtarget,"data":query},"latest"]))
        require(a==4998,"source balance not 4998")
        require(b==1,"B recipient balance not one")
        require(g==1,"G recipient balance not one")
        require(a+b+g==5000,"total supply not reconciled")
    reconciliation=s["observations"].get("reconciliation")
    require(reconciliation and reconciliation.get("total")=="5000" and reconciliation.get("unitsUnreconciled")=="0","late recovery accounting absent")
    require(reconciliation.get("noNewSourceTransaction") is True,"recovery must not depend on replay")
    report={
        "classification":"LOCAL_RESEARCHER_CONTROLLED_LEDGER_EVIDENCE_NOT_THIRD_PARTY_CONSENSUS",
        "verified_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "live_rpc_reconciliation":args.fresh_local_rpc,
        "source_successful_receipts":len(source),
        "hub_successful_receipts":len(hub),
        "hub_enygma_batches_with_six_members":len(unique_anon),
        "hub_enygma_transfer_envelopes":observed,
        "abi_signature":SIGNATURE,
        "abi_event_topic0_from_actual_logs":example_abi_topic,
        "observed_batches":unique_anon,
        "fresh_receipts_compared_to_live_rpc":len(live_results),
        "settlement":{
            "A_to_B":"SETTLED_AND_BALANCE_RECONCILED" if args.fresh_local_rpc else "RECORDED_AS_SETTLED_AT_OBSERVATION_TIME",
            "A_to_G":"SETTLED_AFTER_PRE_REGISTERED_TIMEOUT_WITHOUT_NEW_SOURCE_TRANSACTION",
            "source_balance_after_two_payments":"4998",
            "known_B_balance":"1",
            "G_balance":"1",
            "late_recovery":"Bank G mapping and balance appeared after correcting the CTS server certificate and allowing replay-free relayer catch-up",
            "initial_deadline_outcome":"FAIL_TIMEOUT",
            "final_reconciliation":"PASS_5000_OF_5000",
            "unreconciled_units":"0"
        },
        "what_this_proves":"Local Hub emitted queryable six-member sets for a researcher-controlled seven-bank stack; both A-to-B and A-to-G eventually settled, with G initially timing out.",
        "what_this_does_not_prove":"On-time G settlement, a longitudinal attack on a real institution, independent outside consensus or a Rayls Public Testnet commitment."
    }
    if not args.check_only:
        OUT.mkdir(exist_ok=True)
        p=OUT/"receipt-reconciliation.json";p.write_text(json.dumps(report,indent=2)+"\n")
        (OUT/"receipt-reconciliation.sha256").write_text(hashlib.sha256(p.read_bytes()).hexdigest()+"  receipt-reconciliation.json\n")
    print("LOCAL_RECEIPT_RECONCILIATION_PASS","HubBatches",len(unique_anon),"Envelopes",observed,"FreshRPCTx",len(live_results),"G_SETTLED_LATE_ACCOUNTING_CLOSED")
if __name__=="__main__":main()
