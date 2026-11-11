/* Optional public Rayls Testnet proof annex.
   The annex is intentionally OUTSIDE the frozen research archive manifest so
   publishing the already-mined receipt does not change the committed digest. */
(() => {
  "use strict";
  const label=document.getElementById("public-anchor-status");
  const link=document.getElementById("public-anchor-link");
  if(!label||!link)return;
  fetch("public-anchor.json",{cache:"no-store"}).then(r=>{
    if(!r.ok)throw new Error("No anchor annex");
    return r.json();
  }).then(p=>{
    const valid=p.state==="confirmed" && p.chain_id===7295799 &&
      /^0x[0-9a-fA-F]{64}$/.test(p.transaction_hash||"") &&
      /^0x[0-9a-fA-F]{64}$/.test(p.commitment||"") &&
      p.verified_receipt_status===1;
    if(!valid)throw new Error("Unverified anchor");
    label.textContent="MINED · VERIFIED";
    label.classList.remove("pending");
    label.classList.add("ok");
    link.href="https://testnet-explorer.rayls.com/tx/"+p.transaction_hash;
    link.textContent="Inspect public Testnet hash commitment";
    link.hidden=false;
  }).catch(()=>{
    label.textContent="PENDING";
    link.hidden=true;
  });
})();
