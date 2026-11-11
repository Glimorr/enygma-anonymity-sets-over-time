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
    // Post-release presentation correction. The separately published public
    // Testnet annex cannot rewrite the 93-file archive it commits to.
    const heroNote=document.querySelector("#question .small-note");
    if(heroNote && heroNote.textContent.includes("Public Testnet evidence commitments remain pending.")){
      heroNote.textContent=heroNote.textContent.replace(
        "Public Testnet evidence commitments remain pending.",
        "The final archive hash was retrospectively committed to Rayls Public Testnet."
      );
    }
    const figureTitle=document.querySelector("#figures h2");
    if(figureTitle && figureTitle.textContent.startsWith("Five original diagrams")){
      figureTitle.textContent=figureTitle.textContent.replace("Five original diagrams","Six original diagrams");
    }
  }).catch(()=>{
    label.textContent="PENDING";
    link.hidden=true;
  });
})();
