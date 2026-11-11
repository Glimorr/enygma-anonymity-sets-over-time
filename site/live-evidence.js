/* Local Hub evidence explorer. Real local-chain receipts, never a production privacy-attack claim. */
(()=>{
"use strict";
const d=window.RAYLS_LIVE_HUB_DATA;
const parent=document.getElementById("hub-matrix");
if(!parent||!d){if(parent)parent.textContent="Local Hub evidence is unavailable.";return}
const $=id=>document.getElementById(id);
$("live-batches").textContent=String(d.hubBatches);
$("live-envelopes").textContent=String(d.envelopes);
$("live-receipts").textContent=String(d.recheckedReceipts);
$("live-units").textContent=d.bankBalances.total+" / 5,000";
const table=document.createElement("table");
table.className="hub-membership-table";
table.setAttribute("aria-label","Presence or absence of each bank in genuine local Hub anonymity sets");
const caption=document.createElement("caption");
caption.textContent="Local Hub event membership, by mined batch. A filled cell means included, not that the bank received payment.";
table.append(caption);
const thead=document.createElement("thead"),hrow=document.createElement("tr");
["Hub batch",...d.bankIDs].forEach(label=>{const th=document.createElement("th");th.textContent=label;hrow.append(th)});
thead.append(hrow);table.append(thead);
const tbody=document.createElement("tbody");
const rowButtons=[];
let selected=-1;
function select(index){
 if(index<0||index>=d.batchRows.length)return;
 selected=index;
 for(const [i,btn] of rowButtons.entries())btn.setAttribute("aria-pressed",String(i===index));
 const row=d.batchRows[index];
 $("hub-selected-block").textContent="Block "+row.block;
 $("hub-selected-tx").textContent=row.txHash;
 $("hub-selected-members").textContent=row.members.join(" · ");
 $("hub-missing-member").textContent=d.bankIDs.filter(x=>!row.members.includes(x)).join(" · ")||"None";
 $("hub-selection-caption").textContent="One real local Hub receipt, six encrypted event envelopes, six listed member banks. This alone does not reveal who received value.";
}
d.batchRows.forEach((row,index)=>{
 const tr=document.createElement("tr"),td=document.createElement("td"),btn=document.createElement("button");
 btn.type="button";btn.className="hub-row-select";btn.textContent="#"+(index+1)+" · "+row.block;btn.setAttribute("aria-label","Inspect Hub batch "+(index+1)+" at block "+row.block);
 btn.addEventListener("click",()=>select(index));rowButtons.push(btn);td.append(btn);tr.append(td);
 d.bankIDs.forEach(bank=>{
  const cell=document.createElement("td");
  const included=row.members.includes(bank);
  cell.className=included?"hub-included":"hub-absent";
  cell.textContent=included?"●":"–";
  cell.setAttribute("aria-label","Bank "+bank+(included?" included":" absent"));
  tr.append(cell);
 });
 tbody.append(tr);
});
table.append(tbody);parent.append(table);
$("copy-hub-tx")?.addEventListener("click",()=>{
 if(selected<0||!navigator.clipboard){return}
 navigator.clipboard.writeText(d.batchRows[selected].txHash).then(()=>{
  $("copy-hub-tx").textContent="Copied";
  $("copy-hub-tx").setAttribute("aria-label","Transaction hash copied");
 }).catch(()=>{});
});
select(0);
})();
