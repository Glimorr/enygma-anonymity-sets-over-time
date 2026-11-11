"use strict";
/*
 Local-only, replay-safe EnygmaTokenExample feasibility trial.
 No public/testnet broadcast and no secret material in output.
 Protocol: research/LIVE-SEVEN-PROTOCOL-v1.md.
*/
const fs=require("fs"), crypto=require("crypto"),{ethers}=require("ethers");
require("dotenv").config();
const PHASE=process.argv[2];
const STATE="/parfin/rayls-privacy-contracts/scripts/w2_live_trial_state.json";
const root="/parfin/rayls-privacy-contracts/artifacts";
const paths={
 token:root+"/src/rayls-protocol/test-contracts/EnygmaTokenExample.sol/EnygmaTokenExample.json",
 pnRegistry:root+"/src/rayls-protocol/TokenRegistry/PNTokenRegistryV1.sol/PNTokenRegistryV1.json",
 registry:root+"/src/privateHub/TokenRegistry/TokenRegistryV1.sol/TokenRegistryV1.json",
 endpoint:root+"/src/rayls-protocol/Endpoint/EndpointV1.sol/EndpointV1.json"
};
const readArtifact=k=>JSON.parse(fs.readFileSync(paths[k]));
const signerKey=process.env.PRIVATE_KEY_SYSTEM;
if(!signerKey)throw Error("No development signer configured");
const wallet=new ethers.Wallet(signerKey);
const pA=new ethers.JsonRpcProvider(process.env.PRIVACY_NODE_A_RPC_URL);
const pB=new ethers.JsonRpcProvider(process.env.PRIVACY_NODE_B_RPC_URL);
const pG=new ethers.JsonRpcProvider(process.env.PRIVACY_NODE_G_RPC_URL);
const pHub=new ethers.JsonRpcProvider(process.env.PNH_RPC_URL);
const fromA=wallet.connect(pA),fromHub=wallet.connect(pHub);
const ZERO="0x0000000000000000000000000000000000000000";
const abiReg=["function getContract(string) view returns (address)"];
const getReg=(p,address)=>new ethers.Contract(address,abiReg,p);
const pnhRegistry=getReg(pHub,process.env.PNH_DEPLOYMENT_PROXY_REGISTRY);
const regA=getReg(pA,process.env.PRIVACY_NODE_A_DEPLOYMENT_PROXY_REGISTRY);
const regB=getReg(pB,process.env.PRIVACY_NODE_B_DEPLOYMENT_PROXY_REGISTRY);
const regG=getReg(pG,process.env.PRIVACY_NODE_G_DEPLOYMENT_PROXY_REGISTRY);
const read=()=>fs.existsSync(STATE)?JSON.parse(fs.readFileSync(STATE,"utf8")):null;
const save=x=>{x.updatedAt=new Date().toISOString();fs.writeFileSync(STATE+".tmp",JSON.stringify(x,null,2)+"\n",{mode:0o600});fs.renameSync(STATE+".tmp",STATE)};
const jsonValue=x=>JSON.parse(JSON.stringify(x,(k,v)=>typeof v==="bigint"?v.toString():v));
async function receipt(s,key,p,hash) {
 const existing=s.transactions?.[key];
 if(existing?.receipt?.hash) return existing.receipt;
 const r=await p.waitForTransaction(hash,1,150000);
 if(!r){s.transactions[key].outcome="UNMINED_TIMEOUT";save(s);throw Error("Receipt timed out: "+key)}
 const obj=jsonValue(r.toJSON());
 s.transactions[key].receipt=obj;
 s.transactions[key].outcome=r.status===1?"MINED_SUCCESS":"MINED_REVERTED";
 save(s);
 if(r.status!==1)throw Error("Reverted: "+key);
 return obj;
}
async function broadcast(s,key,contract,method,args,provider,opts={}) {
 const prior=s.transactions[key];
 if(prior?.hash){console.log("RECOVER_PRIOR_TX",key,prior.hash);return receipt(s,key,provider,prior.hash)}
 const tx=await contract[method](...args,{gasLimit:opts.gasLimit||10000000,gasPrice:0});
 s.transactions[key]={hash:tx.hash,nonce:tx.nonce,stage:key,observedAt:new Date().toISOString(),outcome:"PENDING"};
 save(s);console.log("BROADCAST",key,tx.hash);
 return receipt(s,key,provider,tx.hash);
}
async function waitFor(label,fn,timeout=120000,period=2000){
 const end=Date.now()+timeout;
 let last;
 while(Date.now()<end){
  try{last=await fn();if(last)return last}catch(e){last=e.code||e.message}
  await new Promise(r=>setTimeout(r,period));
 }
 throw Error(label+" not observed within timeout: "+String(last).slice(0,150));
}
const token=address=>new ethers.Contract(address,readArtifact("token").abi,fromA);
async function state(){
 const s=read();if(!s)throw Error("No state. Run init first.");
 if(s.scope!=="RESEARCHER_CONTROLLED_LOCAL_LEDGER")throw Error("Wrong scope");
 return s;
}
async function main(){
 if(!PHASE||!["init","deploy","register","authorize","submitHub","approve","mint","sendB","sendG","reconcileG","observe"].includes(PHASE))throw Error("Unknown stage");
 if(PHASE==="init"){
  if(read()){console.log("EXISTING_STATE; refusing new initialization");return}
  const chains=[["hub",pHub,1337],["A",pA,12345],["B",pB,12346],["G",pG,12351]];
  const snapshot={};
  for(const [name,p,expected] of chains){
   const [net,height]=await Promise.all([p.getNetwork(),p.getBlockNumber()]);
   if(Number(net.chainId)!==expected)throw Error("Mismatched chain "+name);
   const b=await p.getBlock(height);
   if(!b?.hash)throw Error("No block hash "+name);
   snapshot[name]={chainId:expected,blockNumber:height,blockHash:b.hash};
  }
  const hubTokenReg=await pnhRegistry.getContract("TokenRegistry");
  const reg=new ethers.Contract(hubTokenReg,readArtifact("registry").abi,pHub);
  const previous=await reg.getAllTokens();
  const s={scope:"RESEARCHER_CONTROLLED_LOCAL_LEDGER",protocol:"LIVE-SEVEN-PROTOCOL-v1.md",observedAt:new Date().toISOString(),signer:wallet.address,baseline:snapshot,registeredTokenCountBefore:previous.length,tokenName:"RQ2_Enygma_Seven_20261111",tokenSymbol:"RQ2N2",mintBaseUnits:"5000",transactions:{},observations:{}};
  if(previous.length!==0)throw Error("Unexpected existing token count; stop, do not assume clean");
  save(s);console.log("BASELINE_RECORDED",JSON.stringify(snapshot));return;
 }
 const s=await state();
 if(PHASE==="deploy"){
  if(!s.tokenAddress){
   const endpointA=await regA.getContract("Endpoint");
   const artifact=readArtifact("token");
   const factory=new ethers.ContractFactory(artifact.abi,artifact.bytecode,fromA);
   const prior=s.transactions.deploy;
   if(!prior){
    const contract=await factory.deploy(s.tokenName,s.tokenSymbol,endpointA,{gasLimit:10000000,gasPrice:0});
    const tx=contract.deploymentTransaction();
    s.transactions.deploy={hash:tx.hash,nonce:tx.nonce,stage:"deploy",outcome:"PENDING",observedAt:new Date().toISOString()};
    s.tokenAddress=await contract.getAddress();
    save(s);console.log("DEPLOY_BROADCAST",tx.hash,s.tokenAddress);
   }
   const r=await receipt(s,"deploy",pA,s.transactions.deploy.hash);
   const actual=await pA.getCode(s.tokenAddress);
   if(actual==="0x")throw Error("Deployment receipt but missing contract");
   s.observations.deployedCodeSha256=crypto.createHash("sha256").update(Buffer.from(actual.slice(2),"hex")).digest("hex");
   save(s);
  }
  console.log("DEPLOY_VERIFIED",s.tokenAddress);return;
 }
 if(!s.tokenAddress)throw Error("Deploy required");
 const tok=token(s.tokenAddress);
 if(PHASE==="register"){
  const pnTokenRegAddr=await regA.getContract("TokenRegistry");
  const pnTokenReg=new ethers.Contract(pnTokenRegAddr,readArtifact("pnRegistry").abi,fromA);
  await broadcast(s,"register",pnTokenReg,"registerToken",[s.tokenAddress],pA,{gasLimit:5000000});
  try{
   const rid=await tok.resourceId();
   s.tokenResourceId=rid;save(s);console.log("RESOURCE_ID_OBSERVED",rid);
  }catch(e){console.log("RESOURCE_ID_PENDING",e.code||e.message)}
  return;
 }
 if(!s.transactions.register?.receipt?.hash)throw Error("Registration required");
 if(PHASE==="authorize"||PHASE==="submitHub"){
  const pnTokenRegAddr=await regA.getContract("TokenRegistry");
  const pnTokenReg=new ethers.Contract(pnTokenRegAddr,readArtifact("pnRegistry").abi,fromA);
  if(PHASE==="authorize"){
   const prior=await pnTokenReg.getTokenByAddress(s.tokenAddress);
   if(prior.privacyNodeStatus!==2n)
     await broadcast(s,"authorize",pnTokenReg,"updatePrivacyNodeStatus",[s.tokenAddress,2],pA,{gasLimit:5000000});
   const after=await pnTokenReg.getTokenByAddress(s.tokenAddress);
   if(after.privacyNodeStatus!==2n)throw Error("PN token was not authorized");
   s.observations.pnAuthorized=true;save(s);
   console.log("PN_AUTHORIZED_STATUS_2");return;
  }
  const info=await pnTokenReg.getTokenByAddress(s.tokenAddress);
  if(info.privacyNodeStatus!==2n)throw Error("Authorize PN token before Hub submission");
  await broadcast(s,"submitHub",pnTokenReg,"submitToHub",[s.tokenAddress],pA,{gasLimit:5000000});
  console.log("HUB_SUBMIT_SOURCE_RECEIPT_VERIFIED");return;
 }
 if(PHASE==="approve"){
  if(!s.transactions.submitHub?.receipt?.hash)throw Error("Source Hub submission required");
  const hubTokenReg=await pnhRegistry.getContract("TokenRegistry");
  const reg=new ethers.Contract(hubTokenReg,readArtifact("registry").abi,fromHub);
  const info=await waitFor("Hub registration",async()=>{
   const all=await reg.getAllTokens();
   return all.find(t=>t.symbol===s.tokenSymbol)||null;
  },180000);
  const rid=info.resourceId;
  if(s.tokenResourceId && s.tokenResourceId!==ethers.ZeroHash && s.tokenResourceId!==rid)throw Error("Resource ID mismatch");
  s.tokenResourceId=rid;save(s);
  await broadcast(s,"approve",reg,"updateStatus",[rid,1],pHub,{gasLimit:5000000});
  const endpointHub=await pnhRegistry.getContract("Endpoint");
  const endpoint=new ethers.Contract(endpointHub,readArtifact("endpoint").abi,pHub);
  const enygmaAddr=await waitFor("Hub token mapping",async()=>{
   const a=await endpoint.getAddressByResourceId(rid);return a&&a!==ZERO?a:null;
  },180000);
  s.hubEnygmaContract=enygmaAddr;save(s);
  console.log("APPROVAL_VERIFIED",enygmaAddr);
  return;
 }
 if(!s.transactions.approve?.receipt?.hash)throw Error("Approval required");
 if(PHASE==="mint"){
  await broadcast(s,"mint",tok,"mint",[wallet.address,5000n],pA);
  const bal=await tok.balanceOf(wallet.address);
  if(bal!==5000n)throw Error("Mint balance mismatch "+bal);
  s.observations.balanceAfterMint=bal.toString();save(s);
  console.log("MINT_BALANCE_VERIFIED",bal.toString());return;
 }
 if(!s.transactions.mint?.receipt?.hash)throw Error("Mint required");
 if(PHASE==="reconcileG"){
  if(!s.transactions.sendG?.receipt?.hash)throw Error("No original G transfer receipt");
  const epAddr=await regG.getContract("Endpoint");
  const endpoint=new ethers.Contract(epAddr,readArtifact("endpoint").abi,pG);
  const address=await endpoint.getAddressByResourceId(s.tokenResourceId);
  if(!address||address===ZERO)throw Error("G token mapping still absent");
  const gToken=new ethers.Contract(address,readArtifact("token").abi,pG);
  const bToken=new ethers.Contract(s.observations.balanceAfterB.destinationToken,readArtifact("token").abi,pB);
  const [a,b,g]=await Promise.all([tok.balanceOf(wallet.address),bToken.balanceOf(wallet.address),gToken.balanceOf(wallet.address)]);
  if(a!==4998n||b!==1n||g!==1n||a+b+g!==5000n)throw Error("G settlement or accounting did not reconcile");
  s.observations.balanceAfterG={source:a.toString(),destination:g.toString(),destinationToken:address,observedAt:new Date().toISOString(),outcome:"SETTLED_LATE_AFTER_PREREGISTERED_TIMEOUT"};
  s.observations.reconciliation={bankA:a.toString(),bankB:b.toString(),bankG:g.toString(),total:(a+b+g).toString(),unitsUnreconciled:"0",noNewSourceTransaction:true,sourceGTransactionHash:s.transactions.sendG.hash};
  save(s);
  console.log("LATE_G_SETTLEMENT_RECONCILED_NO_NEW_PAYMENT",JSON.stringify(s.observations.reconciliation));
  return;
 }
 const dest=PHASE==="sendB"?"B":PHASE==="sendG"?"G":null;
 if(dest){
  if(dest==="G"&&!s.transactions.sendB?.receipt?.hash)throw Error("B transfer required");
  const id=dest==="B"?12346:12351;
  const key=dest==="B"?"sendB":"sendG";
  const senderBalance=await tok.balanceOf(wallet.address);
  const expectedBefore=dest==="B"?5000n:4999n;
  if(!s.transactions[key] && senderBalance!==expectedBefore)throw Error("Unexpected balance before "+dest+" transfer: "+senderBalance);
  await broadcast(s,key,tok,"crossTransfer",[[wallet.address],[1n],[id],[[]]],pA,{gasLimit:10000000});
  const expectedAfter=dest==="B"?4999n:4998n;
  await waitFor("Source balance after "+dest,async()=>await tok.balanceOf(wallet.address)===expectedAfter,150000);
  const p=dest==="B"?pB:pG;const r=dest==="B"?regB:regG;
  const endpointAddress=await r.getContract("Endpoint");
  const endpoint=new ethers.Contract(endpointAddress,readArtifact("endpoint").abi,p);
  const target=await waitFor(dest+" resource mapping",async()=>{
   const a=await endpoint.getAddressByResourceId(s.tokenResourceId);
   return a&&a!==ZERO?a:null;
  },150000);
  const destToken=new ethers.Contract(target,readArtifact("token").abi,p);
  await waitFor(dest+" destination balance",async()=>await destToken.balanceOf(wallet.address)===1n,150000);
  s.observations["balanceAfter"+dest]={source:expectedAfter.toString(),destination:"1",destinationToken:target};
  save(s);console.log("DESTINATION_SETTLED",dest,target);
  return;
 }
 if(PHASE==="observe"){
  if(!s.hubEnygmaContract)throw Error("No Hub contract");
  const iface=new ethers.Interface(["event EnygmaTransfer(bytes32 indexed resourceId,uint256 fromChainId,uint256[] anonymitySet,uint256[] encryptedMessages)"]);
  const latest=await pHub.getBlockNumber();
  // Collect actual raw logs for contract from the preregistered baseline forward
  const logs=await pHub.getLogs({address:s.hubEnygmaContract,fromBlock:s.baseline.hub.blockNumber,toBlock:latest});
  s.observations.hubBlockEnd=latest;
  s.observations.hubLogs=logs.map(log=>jsonValue({address:log.address,blockNumber:log.blockNumber,blockHash:log.blockHash,transactionHash:log.transactionHash,index:log.index,topics:log.topics,data:log.data}));
  const txhashes=[...new Set(logs.map(x=>x.transactionHash))];
  s.observations.hubReceipts={};
  for (const hash of txhashes){
   const r=await pHub.getTransactionReceipt(hash);
   s.observations.hubReceipts[hash]=r?jsonValue(r.toJSON()):null;
  }
  save(s);
  console.log("HUB_OBSERVED",logs.length,"event logs",txhashes.length,"tx receipts","at height",latest);
 }
}
main().catch(e=>{console.error("LIVE_STAGE_FAILED",PHASE,e.code||e.shortMessage||e.message);process.exitCode=1})
 .finally(()=>{pA.destroy();pB.destroy();pG.destroy();pHub.destroy()});
