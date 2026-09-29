(()=>{
"use strict";
const addScript=src=>{if(document.querySelector('script[src="'+src+'"]'))return;const s=document.createElement("script");s.src=src;s.async=true;document.head.appendChild(s)};
const idle=(fn,timeout)=>{if("requestIdleCallback" in window)requestIdleCallback(fn,{timeout});else setTimeout(fn,Math.min(timeout,1200))};
addEventListener("load",()=>{
  idle(()=>addScript("/assets/accessibility.js"),1800);
  idle(()=>addScript("/tools/assets/analytics-loader.js"),4200);
},{once:true});
})();