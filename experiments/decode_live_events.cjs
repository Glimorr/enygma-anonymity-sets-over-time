"use strict";
const fs=require("fs"),crypto=require("crypto"),{ethers}=require("ethers");require("dotenv").config();
const path="/parfin/rayls-privacy-contracts/scripts/w2_live_trial_state.json";
const state=JSON.parse(fs.readFileSync(path,"utf8"));
const root="/parfin/rayls-privacy-contracts/artifacts";
const artifact=(p)=>JSON.parse(fs.readFileSync(root+p)).abi;
const specs=[
 ["EnygmaTeleport","/src/rayls-protocol/Enygma/Enygma-Payments/EnygmaTeleport.sol/EnygmaTeleport.json"],
 ["EnygmaV1","/src/rayls-protocol/Enygma/Enygma-Payments/EnygmaV1.sol/EnygmaV1.json"],
 ["EnygmaTokenExample","/src/rayls-protocol/test-contracts/EnygmaTokenExample.sol/EnygmaTokenExample.json"],
 ["EndpointV1","/src/rayls-protocol/Endpoint/EndpointV1.sol/EndpointV1.json"],
 ["PNTokenRegistryV1","/src/rayls-protocol/TokenRegistry/PNTokenRegistryV1.sol/PNTokenRegistryV1.json"],
 ["TokenRegistryV1","/src/privateHub/TokenRegistry/TokenRegistryV1.sol/TokenRegistryV1.json"]
];
const decoders=specs.map(([n,p])=>({name:n,i:new ethers.Interface(artifact(p))}));
const toShort=v=>{
 if(typeof v==="bigint")return v.toString();
 if(typeof v==="string"){
  if(v.length>100){return {bytes:v.length>=2&&v.startsWith("0x")?(v.length-2)/2:null,sha256:crypto.createHash("sha256").update(v).digest("hex")}}
  return v;
 }
 if(Array.isArray(v))return v.map(toShort);
 return v;
};
const decodeLogs=(logs)=>{
 let out=[];
 for(const l of logs){
  let hit=null;
  for(const d of decoders){
   try{const x=d.i.parseLog(l);
    if(x){hit={event:x.name,artifact:d.name,emitter:l.address,txHash:l.transactionHash,blockNumber:l.blockNumber,args:x.fragment.inputs.map((inp,j)=>({name:inp.name||String(j),value:toShort(x.args[j])}))};break;}
   }catch(e){}
  }
  out.push(hit||{event:"UNKNOWN",emitter:l.address,txHash:l.transactionHash,blockNumber:l.blockNumber,topic0:l.topics?.[0]});
 }
 return out;
};
const tx={};
for(const [k,v] of Object.entries(state.transactions)){
 if(v.receipt?.logs)tx[k]={txHash:v.hash,receiptStatus:v.receipt.status,logs:decodeLogs(v.receipt.logs)};
}
const hub=[];
for(const [k,v] of Object.entries(state.observations.hubReceipts||{})){
 if(v)hub.push({txHash:k,receiptStatus:v.status,blockNumber:v.blockNumber,logs:decodeLogs(v.logs)});
}
const result={scope:"LOCAL_RESEARCHER_CONTROLLED_CHAINS",generatedAt:new Date().toISOString(),tokenSymbol:state.tokenSymbol,transactions:tx,hub};
fs.writeFileSync("/parfin/rayls-privacy-contracts/scripts/w2_decoded_live_events.json",JSON.stringify(result,null,2)+"\n");
for(const [k,v] of Object.entries(tx))console.log("SOURCE_EVENT_SUMMARY",k,"events",v.logs.map(x=>x.event).join(","));
for(const h of hub)console.log("HUB_EVENT_SUMMARY",h.txHash,"events",h.logs.map(x=>x.event).join(","));
