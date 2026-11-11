#!/usr/bin/env python3
"""Verify a disclosure-safe Rayls Testnet evidence digest sidecar. No signing keys."""
import argparse,hashlib,json,pathlib,re,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
HEX32=re.compile(r"^0x[0-9a-fA-F]{64}$")
RPC="https://testnet-rpc.rayls.com/"
def must(condition,message):
    if not condition:raise AssertionError(message)
def post(method,params):
    req=urllib.request.Request(RPC,data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=18) as response:obj=json.load(response)
    if "error" in obj:raise RuntimeError(obj["error"])
    return obj.get("result")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--live-rpc",action="store_true",help="Authenticate the transaction against the public Rayls Testnet RPC")
    ap.add_argument("--optional",action="store_true",help="Allow absent sidecar while preparing the release")
    args=ap.parse_args()
    manifest=json.loads((ROOT/"EVIDENCE-MANIFEST.json").read_text()) if (ROOT/"EVIDENCE-MANIFEST.json").exists() else json.loads((ROOT/"release/public/EVIDENCE-MANIFEST.json").read_text())
    root="0x"+manifest["files_merkle_equivalent_sha256"]
    side=ROOT/"site/public-anchor.json"
    if not side.is_file():
        if args.optional:
            print("NO_PUBLIC_TESTNET_ANCHOR_YET; NO CLAIM OF AN ONCHAIN COMMITMENT")
            return
        raise FileNotFoundError(side)
    a=json.loads(side.read_text())
    must(a["state"]=="confirmed","Anchor has not been confirmed")
    must(a["chain_id"]==7295799,"Rayls Testnet chain ID mismatch")
    must(a["commitment"].lower()==root.lower(),"On-chain commitment does not match the frozen archive manifest root")
    h=a["transaction_hash"];must(HEX32.fullmatch(h),"Transaction hash invalid")
    must(a["verified_receipt_status"]==1,"Transaction failed")
    must(a["from"].lower()==a["to"].lower(),"Expected self-addressed signature")
    must(a["explorer_url"]=="https://testnet-explorer.rayls.com/tx/"+h,"Unexpected explorer URL")
    must(a["commitment_type"]=="files_merkle_equivalent_sha256","Wrong commitment format")
    must("retrospective" in a["evidence_scope"].lower(),"Anchor chronology is not identified")
    if args.live_rpc:
        chain=int(post("eth_chainId",[]),16)
        must(chain==7295799,"RPC chain ID mismatch")
        tx=post("eth_getTransactionByHash",[h])
        receipt=post("eth_getTransactionReceipt",[h])
        must(tx is not None and receipt is not None,"Public transaction or receipt not found")
        must(tx["hash"].lower()==h.lower(),"Public tx mismatch")
        must(tx["input"].lower()==root.lower(),"Public input does not match manifest")
        must(tx["from"].lower()==a["from"].lower(),"Public sender does not match anchor")
        must(tx["to"].lower()==a["to"].lower(),"Public recipient does not match anchor")
        must(int(receipt["status"],16)==1,"Public receipt reverted")
        must(int(receipt["blockNumber"],16)==a["block_number"],"Public block number mismatch")
        must(receipt["blockHash"].lower()==a["block_hash"].lower(),"Public block hash mismatch")
        header=post("eth_getBlockByHash",[a["block_hash"],False])
        must(header and h.lower() in [x.lower() for x in header["transactions"]],"Public header does not include tx")
    print("RAYLS_TESTNET_MANIFEST_ANCHOR_PASS",h,"CHAIN",a["chain_id"],"LIVE_RPC",args.live_rpc)
if __name__=="__main__":main()
