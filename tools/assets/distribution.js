/* Free sharing controls for tool pages. */
(function(){
  "use strict";
  if(!location.pathname.startsWith("/tools/")||location.pathname==="/tools/privacy/")return;
  function ready(){
    if(document.querySelector(".rr-share-strip"))return;
    const main=document.querySelector("main .wrap")||document.querySelector("main"); if(!main)return;
    const box=document.createElement("section");box.className="panel rr-share-strip";
    box.innerHTML='<h2>Share this free resource</h2><p>If this tool helps someone, pass it on. No account or paywall is required.</p><div class="actions"><button class="btn" data-rr-share="native">Share</button><button class="btn alt" data-rr-share="copy">Copy link</button><a class="btn alt" data-rr-share="linkedin" target="_blank" rel="noopener">Share on LinkedIn</a></div>';
    main.appendChild(box);
    const url=location.href.split("?")[0],title=document.title.replace(/\s*\|\s*RR Free Tools.*$/,"");
    const copy=box.querySelector('[data-rr-share="copy"]'),native=box.querySelector('[data-rr-share="native"]'),li=box.querySelector('[data-rr-share="linkedin"]');
    copy.onclick=async()=>{await navigator.clipboard.writeText(url);copy.textContent="Link copied";};
    native.onclick=async()=>{if(navigator.share)await navigator.share({title,text:"Free public tool from Ragunauth Ramsaroop",url});else{await navigator.clipboard.writeText(url);native.textContent="Link copied";}};
    li.href="https://www.linkedin.com/sharing/share-offsite/?url="+encodeURIComponent(url);
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",ready);else ready();
})();