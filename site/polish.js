/* Scroll-led narrative and typographic motion. Decorative only, no evidence mutation. */
(() => {
"use strict";
const reduced=matchMedia("(prefers-reduced-motion: reduce)");
const title=document.querySelector(".hero h1");
if(title && !title.dataset.kineticEnhanced){
 title.dataset.kineticEnhanced="true";
 title.setAttribute("aria-label",title.textContent.replace(/\s+/g," ").trim());
 let index=0;
 function split(node){
  for(const child of [...node.childNodes]){
   if(child.nodeType===Node.TEXT_NODE){
    const fragment=document.createDocumentFragment();
    for(const part of child.textContent.split(/(\s+)/g)){
     if(!part) continue;
     if(/^\s+$/.test(part)){fragment.append(document.createTextNode(part));continue}
     const span=document.createElement("span");
     span.className="kinetic-word";
     span.textContent=part;
     span.setAttribute("aria-hidden","true");
     span.style.setProperty("--word-order",String(index++));
     fragment.append(span);
    }
    node.replaceChild(fragment,child);
   } else if(child.nodeType===Node.ELEMENT_NODE)split(child);
  }
 }
 split(title);
}
const motion=document.getElementById("motion-toggle");
const orbit=document.querySelector(".hero .orbit");
let paused=false;
if(orbit){
 const glow=document.createElement("div");glow.className="orbit-aura";glow.setAttribute("aria-hidden","true");orbit.prepend(glow);
 const signal=document.createElement("div");signal.className="signal-ribbon";signal.setAttribute("aria-hidden","true");orbit.append(signal);
 const chips=[
  {position:"top-right",value:"07",label:"LAB BANKS"},
  {position:"bottom-left",value:"06",label:"VISIBLE / BATCH"},
  {position:"bottom-right",value:"01",label:"REAL RECIPIENT"}
 ];
 for(const chip of chips){
  const el=document.createElement("div");el.className="holo-tag "+chip.position;
  el.setAttribute("aria-hidden","true");
  const dot=document.createElement("span");dot.className="tiny-led";el.append(dot);
  const value=document.createElement("strong");value.textContent=chip.value;el.append(value);
  const detail=document.createElement("span");detail.textContent=chip.label;el.append(detail);
  orbit.append(el);
 }
}
const chapters=[
 ["question","The question"],
 ["mechanism","Privacy model"],
 ["journey","3D walkthrough"],
 ["lab","Native observations"],
 ["live","Local Hub evidence"],
 ["figures","Research figures"],
 ["evidence","Verification"]
];
if(!document.getElementById("chapter-rail")){
 const rail=document.createElement("nav");rail.id="chapter-rail";rail.setAttribute("aria-label","Research chapter navigation");
 const refs=[];
 for(const [id,label] of chapters){
  if(!document.getElementById(id))continue;
  const a=document.createElement("a");a.href="#"+id;a.dataset.label=label;a.setAttribute("aria-label","Jump to "+label);
  const dot=document.createElement("span");dot.setAttribute("aria-hidden","true");a.append(dot);rail.append(a);refs.push([id,a]);
 }
 document.body.append(rail);
 let active="";
 let tick=false;
 function markChapter(){
  tick=false;
  const threshold=innerHeight*.39;
  let current=refs[0]?.[0]||"question";
  for(const [id] of refs){
   const section=document.getElementById(id);if(section&&section.getBoundingClientRect().top<=threshold)current=id;
  }
  if(current===active)return;
  active=current;
  for(const [id,a] of refs){
   if(id===active)a.setAttribute("aria-current","location");
   else a.removeAttribute("aria-current");
  }
 }
 addEventListener("scroll",()=>{if(!tick){tick=true;requestAnimationFrame(markChapter)}},{passive:true});
 addEventListener("resize",()=>{if(!tick){tick=true;requestAnimationFrame(markChapter)}},{passive:true});
 markChapter();
}
const sourceLines=document.querySelectorAll(".evidence-separator");
if(!reduced.matches && sourceLines.length && "IntersectionObserver" in window){
 const observer=new IntersectionObserver(entries=>{
  for(const entry of entries){
   if(entry.isIntersecting){entry.target.classList.add("in-view");observer.unobserve(entry.target)}
  }
 },{threshold:.3});
 sourceLines.forEach(el=>observer.observe(el));
}
for(const [i,fig] of [...document.querySelectorAll(".figure-grid .figure")].entries()){
 fig.dataset.index=String(i+1);
}
if(motion){
 motion.addEventListener("click",()=>{
  paused=document.body.classList.contains("motion-paused");
 });
}
})();
