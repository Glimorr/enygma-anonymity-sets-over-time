const fs=require("fs"),{ethers}=require("ethers");require("dotenv").config();
const s=JSON.parse(fs.readFileSync("/parfin/rayls-privacy-contracts/scripts/w2_live_trial_state.json","utf8"));
(async()=>{
 const a=new ethers.JsonRpcProvider(process.env.PRIVACY_NODE_A_RPC_URL),g=new ethers.JsonRpcProvider(process.env.PRIVACY_NODE_G_RPC_URL),h=new ethers.JsonRpcProvider(process.env.PNH_RPC_URL);
 const w=new ethers.Wallet(process.env.PRIVATE_KEY_SYSTEM);
 const source=new ethers.Contract(s.tokenAddress,["function balanceOf(address) view returns (uint256)"],a);
 const reg=new ethers.Contract(process.env.PRIVACY_NODE_G_DEPLOYMENT_PROXY_REGISTRY,["function getContract(string) view returns(address)"],g);
 const epAddr=await reg.getContract("Endpoint");
 const ep=new ethers.Contract(epAddr,["function getAddressByResourceId(bytes32) view returns(address)"],g);
 let dest=null,balance=null;
 try{dest=await ep.getAddressByResourceId(s.tokenResourceId);if(dest!==ethers.ZeroAddress){const t=new ethers.Contract(dest,["function balanceOf(address) view returns (uint256)"],g);balance=(await t.balanceOf(w.address)).toString()}}catch(e){balance="QUERY_FAILED_"+(e.code||e.name)}
 const hubLogs=await h.getLogs({address:s.hubEnygmaContract,fromBlock:s.baseline.hub.blockNumber,toBlock:"latest"});
 console.log(JSON.stringify({sourceBalance:(await source.balanceOf(w.address)).toString(),gDestResourceMapped:!!dest&&dest!==ethers.ZeroAddress,gBalance:balance,hubLogCount:hubLogs.length,hubTxCount:[...new Set(hubLogs.map(x=>x.transactionHash))].length,hubLatest:await h.getBlockNumber(),GHeight:await g.getBlockNumber()}));
 a.destroy();g.destroy();h.destroy();
})().catch(e=>{console.error("CHECK_ERROR",e.code||e.message);process.exitCode=1});
