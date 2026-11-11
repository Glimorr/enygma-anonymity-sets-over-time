/* Independent Rayls Enygma research: motion layer only. Evidence data stays in data.js. */
(() => {
"use strict";
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const clamp = (n,a=0,b=1) => Math.min(b,Math.max(a,n));
const root=document.documentElement;
const theatre=document.getElementById("journey");
const stage=document.querySelector(".depth-scene");
const orbit=document.querySelector(".orbit");
const steps=[...document.querySelectorAll(".depth-step")];
const banks=[...document.querySelectorAll(".bank3d")];
const motionButton=document.getElementById("motion-toggle");
let motionAllowed=!reduceMotion.matches;
let currentPhase=-1;
let pointerX=0,pointerY=0;
let frameRequest=false;
const setPhase=(phase)=>{
 phase=Math.max(0,Math.min(2,phase));
 if (phase===currentPhase) return;
 currentPhase=phase;
 steps.forEach((node,i)=>{
   if(i===phase) node.setAttribute("aria-current","step");
   else node.removeAttribute("aria-current");
 });
 const lit=phase===0?["A","B","C","D","E","F"]:
   phase===1?["A","B","C","F"]:["A","B","C"];
 banks.forEach(node=>{
   const bank=node.dataset.bank;
   node.classList.toggle("active",lit.includes(bank) && bank!=="A");
   node.classList.toggle("dimmed",!lit.includes(bank));
 });
 if(stage)stage.setAttribute("data-phase",String(phase));
};
function updateScroll(){
 frameRequest=false;
 const scrollMax=Math.max(1,document.documentElement.scrollHeight-innerHeight);
 root.style.setProperty("--scroll-progress",clamp(scrollY/scrollMax).toFixed(5));
 if(!theatre||innerWidth<=800) return;
 const rect=theatre.getBoundingClientRect();
 const duration=Math.max(1,theatre.offsetHeight-innerHeight);
 const t=clamp(-rect.top/duration);
 theatre.style.setProperty("--journey",t.toFixed(4));
 if(stage) {
   stage.style.setProperty("--journey-angle",(t*215).toFixed(1)+"deg");
   stage.style.setProperty("--scene-ry",(-9+t*22+pointerX*8).toFixed(2)+"deg");
   stage.style.setProperty("--scene-rx",(8-t*9-pointerY*4).toFixed(2)+"deg");
 }
 setPhase(t < .30 ? 0 : t < .66 ? 1 : 2);
}
function scheduleScroll(){
 if(!frameRequest){frameRequest=true;requestAnimationFrame(updateScroll)}
}
steps.forEach((step,i)=>{
 step.addEventListener("click",()=>{
   setPhase(i);
   if(innerWidth>800 && theatre){
     const amount=Math.max(1,theatre.offsetHeight-innerHeight);
     const position=window.scrollY+theatre.getBoundingClientRect().top+amount*[.12,.48,.85][i];
     scrollTo({top:position,behavior:motionAllowed?"smooth":"instant"});
   }
 });
});
motionButton?.addEventListener("click",()=>{
 motionAllowed=!motionAllowed;
 document.body.classList.toggle("motion-paused",!motionAllowed);
 motionButton.setAttribute("aria-pressed",String(!motionAllowed));
 motionButton.textContent=motionAllowed?"Pause motion":"Play motion";
 if(motionAllowed) startAmbient();else cancelAnimationFrame(ambientFrame);
});
reduceMotion.addEventListener?.("change",()=>{
 motionAllowed=!reduceMotion.matches;
 document.body.classList.toggle("motion-paused",!motionAllowed);
 if(!motionAllowed)cancelAnimationFrame(ambientFrame);
 else startAmbient();
});
if(orbit){
 orbit.addEventListener("pointermove",(e)=>{
  if(!motionAllowed||e.pointerType==="touch")return;
  const box=orbit.getBoundingClientRect();
  const px=(e.clientX-box.left)/box.width-.5;
  const py=(e.clientY-box.top)/box.height-.5;
  orbit.style.setProperty("--mx",(py*-7).toFixed(1)+"deg");
  orbit.style.setProperty("--my",(px*9).toFixed(1)+"deg");
 });
 orbit.addEventListener("pointerleave",()=>{
  orbit.style.setProperty("--mx","0deg");orbit.style.setProperty("--my","0deg");
 });
}
if(theatre){
 theatre.addEventListener("pointermove",(e)=>{
  if(!motionAllowed||e.pointerType==="touch")return;
  const box=theatre.getBoundingClientRect();
  pointerX=clamp((e.clientX-box.left)/box.width,0,1)*2-1;
  pointerY=clamp((e.clientY-box.top)/box.height,0,1)*2-1;
  scheduleScroll();
 });
 theatre.addEventListener("pointerleave",()=>{pointerX=0;pointerY=0;scheduleScroll()});
}
const interactiveCards=document.querySelectorAll(".card,.figure,.metric");
if(!reduceMotion.matches){
 interactiveCards.forEach(card=>{
  card.addEventListener("pointermove",(e)=>{
   if(e.pointerType==="touch"||!motionAllowed||innerWidth<950)return;
   const rect=card.getBoundingClientRect();
   const x=(e.clientX-rect.left)/rect.width-.5;
   const y=(e.clientY-rect.top)/rect.height-.5;
   card.style.transform="perspective(1100px) rotateX("+(-y*3).toFixed(2)+"deg) rotateY("+(x*3).toFixed(2)+"deg) translateY(-3px)";
  },{passive:true});
  card.addEventListener("pointerleave",()=>{card.style.transform=""});
 });
}
addEventListener("scroll",scheduleScroll,{passive:true});
addEventListener("resize",()=>{scheduleScroll();resizeAmbient()},{passive:true});
addEventListener("pointermove",e=>{
  if(!motionAllowed)return;
  root.style.setProperty("--pointer-x",(e.clientX/innerWidth*100).toFixed(1)+"%");
  root.style.setProperty("--pointer-y",(e.clientY/innerHeight*100).toFixed(1)+"%");
},{passive:true});
setPhase(0);
scheduleScroll();

/* Dependency-free perspective starfield; illustrative, not transaction data. */
const canvas=document.getElementById("rayls-starfield");
const ctx=canvas?.getContext("2d",{alpha:true});
let stars=[],ambientFrame=0,ambientLast=0,viewWidth=0,viewHeight=0,scale=1;
let seed=0xA5B7C19;
function random(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return ((seed>>>0)%100000)/100000}
function resizeAmbient(){
 if(!ctx)return;
 scale=Math.min(2,Math.max(1,devicePixelRatio||1));
 viewWidth=innerWidth;viewHeight=innerHeight;
 canvas.width=Math.round(viewWidth*scale);canvas.height=Math.round(viewHeight*scale);
 canvas.style.width=viewWidth+"px";canvas.style.height=viewHeight+"px";
 ctx.setTransform(scale,0,0,scale,0,0);
 if(!stars.length){
  stars=Array.from({length:Math.min(165,Math.max(75,Math.round(viewWidth/11)))},(_,i)=>({
   x:(random()-.5)*2.7,y:(random()-.5)*2.2,z:.18+random()*1.65,
   r:.35+random()*1.1,phase:random()*6.283,color:i%5===0?"lime":i%3===0?"purple":"faint"
  }));
 }
}
function drawAmbient(now=0){
 if(!ctx||!motionAllowed||document.hidden)return;
 if(now-ambientLast<24){ambientFrame=requestAnimationFrame(drawAmbient);return}
 ambientLast=now;
 ctx.clearRect(0,0,viewWidth,viewHeight);
 const scrollFactor=window.scrollY/Math.max(1,document.documentElement.scrollHeight-window.innerHeight);
 const shift=scrollFactor*.21;
 const centerX=viewWidth*.52,centerY=viewHeight*.48;
 for(let i=0;i<stars.length;i++){
  const p=stars[i]; const depth=.65+p.z;
  const swayX=.009*Math.sin(now*.00013+p.phase);
  const sx=centerX+(p.x+swayX+pointerX*.07)*viewWidth/depth*.46;
  const sy=centerY+(p.y+Math.cos(now*.00018+p.phase)*.007+shift)*viewHeight/depth*.48;
  if(sx<0||sy<0||sx>viewWidth||sy>viewHeight)continue;
  const alpha=clamp(.07+(2-p.z)*.12+(Math.sin(now*.0007+p.phase)+1)*.04,0,.39);
  const color=p.color==="lime"?"rgba(236,251,62,"+alpha+")":p.color==="purple"?"rgba(178,137,245,"+alpha+")":"rgba(192,177,224,"+(alpha*.7)+")";
  ctx.beginPath();ctx.fillStyle=color;ctx.arc(sx,sy,p.r*(2.1-p.z),0,Math.PI*2);ctx.fill();
  if(i%15===0) {
   ctx.strokeStyle="rgba(165,118,224,"+(alpha*.27)+")";
   ctx.lineWidth=.6;ctx.beginPath();ctx.moveTo(sx,sy);ctx.lineTo(sx+15*(2-p.z),sy-11*(2-p.z));ctx.stroke();
  }
 }
 ambientFrame=requestAnimationFrame(drawAmbient);
}
function startAmbient(){
 if(!ctx||!motionAllowed||document.hidden)return;
 cancelAnimationFrame(ambientFrame);
 ambientFrame=requestAnimationFrame(drawAmbient);
}
document.addEventListener("visibilitychange",()=>{
 if(document.hidden)cancelAnimationFrame(ambientFrame);
 else startAmbient();
});
if(ctx){resizeAmbient();startAmbient()}
})();
