/* An evidence-only interaction: count public membership, never infer recipients. */
(() => {
"use strict";
const data=window.RAYLS_LIVE_HUB_DATA;
const matrix=document.getElementById("hub-matrix");
if(!data||!matrix||!Array.isArray(data.batchRows)||data.batchRows.length!==6)return;
const banks=data.bankIDs;
const counts=Object.fromEntries(banks.map(b=>[b,data.batchRows.reduce((n,row)=>n+Number(row.members.includes(b)),0)]));
const group=document.createElement("section");
group.className="bank-lens";
group.setAttribute("aria-label","Explore observed bank membership frequency");
const headline=document.createElement("div");
headline.className="bank-lens-intro";
const title=document.createElement("strong");
title.textContent="Inspect membership — not recipients";
const context=document.createElement("span");
context.textContent="Select a bank to highlight its presence across the six mined Hub batches.";
headline.append(title,context);
const toolbar=document.createElement("div");
toolbar.className="bank-lens-buttons";
toolbar.setAttribute("role","group");
toolbar.setAttribute("aria-label","Bank membership selector");
const buttons=[];
function makeButton(label,value){
 const button=document.createElement("button");
 button.className="bank-lens-button";
 button.type="button";
 button.textContent=label;
 button.setAttribute("aria-pressed",String(value==="all"));
 button.dataset.bank=value;
 button.addEventListener("click",()=>focusBank(value));
 buttons.push(button);
 toolbar.append(button);
 return button;
}
makeButton("All","all");
for(const bank of banks)makeButton("Bank "+bank,bank);
const summary=document.createElement("div");
summary.className="bank-lens-summary";
summary.setAttribute("aria-live","polite");
const score=document.createElement("strong");
const note=document.createElement("span");
summary.append(score,note);
group.append(headline,toolbar,summary);
matrix.parentElement.insertBefore(group,matrix);
function focusBank(bank){
 for(const button of buttons)button.setAttribute("aria-pressed",String(button.dataset.bank===bank));
 const table=matrix.querySelector("table.hub-membership-table");
 if(table){
  for(const [i,row] of [...table.querySelectorAll("tbody tr")].entries()){
   const cells=[...row.querySelectorAll("td")];
   const included=bank!=="all" && data.batchRows[i].members.includes(bank);
   row.classList.toggle("bank-lens-row-highlight",included);
   for(const [j,cell] of cells.entries()){
    cell.classList.toggle("bank-lens-cell-highlight",bank!=="all" && j>0 && banks[j-1]===bank && included);
    cell.classList.toggle("bank-lens-cell-muted",bank!=="all" && j>0 && banks[j-1]!==bank);
   }
  }
  for(const [j,th] of [...table.querySelectorAll("thead th")].entries()){
   th.classList.toggle("bank-lens-header-highlight",bank!=="all" && j>0 && banks[j-1]===bank);
  }
 }
 if(bank==="all"){
   score.textContent="36 observed inclusions · six batches";
   note.textContent="Each batch contains six included banks out of seven in this local environment.";
 }else{
   score.textContent="Bank "+bank+" · "+counts[bank]+"/6 observed batches";
   note.textContent="This count cannot distinguish a true recipient from a decoy. Six batches are insufficient for a recipient-inference conclusion.";
 }
}
focusBank("all");
})();
