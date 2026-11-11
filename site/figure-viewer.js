/* Evidence-first figure viewer. Original SVG source assets are unchanged. */
(() => {
  "use strict";
  const cards=[...document.querySelectorAll("#figures .figure")];
  const figures=cards.map((card,index)=>{
    const img=card.querySelector("img");
    const caption=card.querySelector("figcaption");
    if(!img||!caption)return null;
    const open=document.createElement("button");
    open.type="button";
    open.className="figure-open";
    open.setAttribute("aria-label","View figure "+(index+1)+" enlarged: "+caption.textContent.trim());
    img.parentNode.insertBefore(open,img);
    open.appendChild(img);
    return {src:img.getAttribute("src"),alt:img.getAttribute("alt")||"",caption:caption.textContent.trim(),open};
  }).filter(Boolean);
  if(!figures.length)return;
  const viewer=document.createElement("div");
  viewer.id="figure-viewer";
  viewer.className="figure-viewer";
  viewer.hidden=true;
  viewer.innerHTML=[
    '<div class="figure-viewer-backdrop" data-dismiss="true" aria-hidden="true"></div>',
    '<div class="figure-viewer-panel" role="dialog" aria-modal="true" aria-labelledby="figure-viewer-title" aria-describedby="figure-viewer-caption" tabindex="-1">',
    '  <header class="figure-viewer-head">',
    '    <div><p class="figure-viewer-eyebrow">Enygma / Evidence gallery</p><div class="figure-viewer-count" id="figure-viewer-title">Figure 1 of 6</div></div>',
    '    <div class="figure-viewer-actions">',
    '      <button type="button" class="viewer-control" data-viewer="prev" aria-label="Previous research figure" title="Previous figure (←)">←</button>',
    '      <button type="button" class="viewer-control" data-viewer="next" aria-label="Next research figure" title="Next figure (→)">→</button>',
    '      <button type="button" class="viewer-control viewer-close" data-viewer="close" aria-label="Close expanded figure" title="Close (Esc)">✕</button>',
    '    </div>',
    '  </header>',
    '  <div class="figure-viewer-stage" role="region" aria-label="Enlarged evidence figure, scroll to pan when zoomed" tabindex="0"><img alt="" draggable="false"/></div>',
    '  <footer class="figure-viewer-foot">',
    '    <p id="figure-viewer-caption" class="figure-viewer-caption"></p>',
    '    <div class="figure-viewer-zoom" role="group" aria-label="Figure magnification">',
    '      <button type="button" class="viewer-control" data-viewer="out" aria-label="Zoom out" title="Zoom out">−</button>',
    '      <span class="figure-viewer-zoom-label" aria-live="polite">Fit</span>',
    '      <button type="button" class="viewer-control" data-viewer="in" aria-label="Zoom in" title="Zoom in">+</button>',
    '      <button type="button" class="viewer-control" data-viewer="fit" aria-label="Fit image to screen">Fit</button>',
    '    </div>',
    '    <span class="figure-viewer-hint">ESC to close · ← → to browse</span>',
    '  </footer>',
    '</div>'
  ].join("");
  document.body.appendChild(viewer);
  const panel=viewer.querySelector(".figure-viewer-panel");
  const stage=viewer.querySelector(".figure-viewer-stage");
  const image=stage.querySelector("img");
  const title=viewer.querySelector("#figure-viewer-title");
  const caption=viewer.querySelector("#figure-viewer-caption");
  const zoomLabel=viewer.querySelector(".figure-viewer-zoom-label");
  const closeButton=viewer.querySelector('[data-viewer="close"]');
  const inButton=viewer.querySelector('[data-viewer="in"]');
  const outButton=viewer.querySelector('[data-viewer="out"]');
  const fitButton=viewer.querySelector('[data-viewer="fit"]');
  const stops=[1,1.35,1.75,2.3,3];
  let activeIndex=-1,zoomIndex=0,lastFocus=null,lastOverflow="";
  let closedTimer=null;
  const active=()=>!viewer.hidden && activeIndex>=0;
  function setZoom(index){
    zoomIndex=Math.min(stops.length-1,Math.max(0,index));
    const factor=stops[zoomIndex];
    image.style.setProperty("--figure-zoom",String(factor));
    image.classList.toggle("is-zoomed",zoomIndex>0);
    zoomLabel.textContent=zoomIndex===0?"Fit":Math.round(factor*100)+"%";
    outButton.disabled=zoomIndex===0;
    inButton.disabled=zoomIndex===stops.length-1;
    fitButton.disabled=zoomIndex===0;
    stage.scrollTop=0;stage.scrollLeft=0;
  }
  function render(index){
    activeIndex=(index+figures.length)%figures.length;
    const item=figures[activeIndex];
    image.src=item.src;
    image.alt=item.alt;
    caption.textContent=item.caption;
    title.textContent="Figure "+(activeIndex+1)+" of "+figures.length;
    setZoom(0);
  }
  function show(index){
    if(closedTimer!==null){clearTimeout(closedTimer);closedTimer=null;}
    if(!active()){
      lastFocus=document.activeElement;
      lastOverflow=document.body.style.overflow;
      document.body.style.overflow="hidden";
    }
    render(index);
    viewer.hidden=false;
    requestAnimationFrame(()=>{
      viewer.classList.add("is-visible");
      closeButton.focus({preventScroll:true});
    });
  }
  function hide(){
    if(!active())return;
    const returnTarget=figures[activeIndex].open;
    activeIndex=-1;
    viewer.classList.remove("is-visible");
    document.body.style.overflow=lastOverflow;
    (returnTarget||lastFocus)?.focus?.({preventScroll:true});
    if(closedTimer!==null)clearTimeout(closedTimer);
    closedTimer=setTimeout(()=>{
      if(activeIndex<0){viewer.hidden=true;image.removeAttribute("src");}
      closedTimer=null;
    },330);
  }
  function nextFigure(delta){if(active())render(activeIndex+delta);}
  figures.forEach((item,index)=>{
    item.open.addEventListener("click",()=>show(index));
  });
  viewer.addEventListener("click",event=>{
    if(event.target.closest('[data-dismiss="true"]')){hide();return;}
    const control=event.target.closest("[data-viewer]");
    if(!control)return;
    const action=control.dataset.viewer;
    if(action==="close")hide();
    else if(action==="next")nextFigure(1);
    else if(action==="prev")nextFigure(-1);
    else if(action==="in")setZoom(zoomIndex+1);
    else if(action==="out")setZoom(zoomIndex-1);
    else if(action==="fit")setZoom(0);
  });
  document.addEventListener("keydown",event=>{
    if(!active())return;
    if(event.key==="Escape"){event.preventDefault();hide();return;}
    if(event.key==="ArrowRight"){event.preventDefault();nextFigure(1);return;}
    if(event.key==="ArrowLeft"){event.preventDefault();nextFigure(-1);return;}
    if((event.key==="+"||event.key==="=")&&!event.ctrlKey){event.preventDefault();setZoom(zoomIndex+1);return;}
    if(event.key==="-"&&!event.ctrlKey){event.preventDefault();setZoom(zoomIndex-1);return;}
    if(event.key==="0"){event.preventDefault();setZoom(0);return;}
    if(event.key==="Tab"){
      const targets=[...panel.querySelectorAll('button:not(:disabled),[tabindex="0"]')];
      const first=targets[0],last=targets[targets.length-1];
      if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
      else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
    }
  });
  stage.addEventListener("dblclick",()=>{
    if(active())setZoom(zoomIndex===0?2:0);
  });
})();
