/* Privacy-safe engagement events. Never sends tool inputs or free-text content. */
(function(){
"use strict";
const slug=()=>location.pathname.split("/").filter(Boolean).slice(-1)[0]||"home",safe=s=>String(s||"").slice(0,120);
window.rrTrack=function(name,params){if(typeof window.gtag!=="function")return;const base={page_path:location.pathname,tool_slug:location.pathname.startsWith("/tools/")?slug():""};window.gtag("event",name,Object.assign(base,params||{}))};
let started=false,completed=false;
document.addEventListener("submit",e=>{if(location.pathname.startsWith("/tools/")&&e.target.closest("#tool-ui")&&!started){started=true;rrTrack("tool_started")}},true);
document.addEventListener("click",e=>{const el=e.target.closest("a,button");if(!el)return;const href=el.getAttribute("href")||"",label=safe((el.textContent||"").trim());
 if(el.matches("[data-copy],#copy,[data-export=copy]"))rrTrack("result_copied");
 else if(el.matches("[data-print],#print,[data-export=print]"))rrTrack("result_printed");
 else if(el.matches("[data-share],#share,[data-rr-share]"))rrTrack("tool_shared",{share_method:el.dataset.rrShare||"native"});
 else if(el.matches("[data-save]"))rrTrack("scenario_save_clicked");
 else if(el.matches("[data-load]"))rrTrack("scenario_restore_clicked");
 else if(el.matches("[data-compare]"))rrTrack("scenario_compare_clicked");
 else if(el.matches("[data-export]"))rrTrack("export_clicked",{export_type:el.dataset.export||""});
 else if(el.matches("[data-related-tool]"))rrTrack("related_tool_opened");
 else if(el.matches(".filter-chip"))rrTrack("tool_directory_filter",{filter_label:label});
 else if(href.includes("/methodology/"))rrTrack("methodology_opened",{link_label:label});
 else if(href.includes("/tools/downloads/"))rrTrack("template_downloaded",{file_name:href.split("/").pop()});
 else if(href.startsWith("/white-papers/"))rrTrack("white_paper_opened",{link_label:label});
 else if(href.startsWith("/executive-profile/"))rrTrack("profile_opened",{link_label:label});
 else if(href.startsWith("/topics/"))rrTrack("topic_opened",{topic_slug:href.split("/").filter(Boolean).pop()});
 else if(href.startsWith("/tools/"))rrTrack("tool_link_opened",{link_label:label})
},true);
let searchTimer;document.addEventListener("input",e=>{if(e.target?.id==="tool-search-input"){clearTimeout(searchTimer);searchTimer=setTimeout(()=>rrTrack("tool_directory_search",{query_length:String(e.target.value||"").length}),700)}},true);
document.addEventListener("change",e=>{if(e.target?.matches(".filter-chip,#tool-sort"))rrTrack("tool_directory_filter")},true);
const obs=new MutationObserver(()=>{if(!completed&&document.querySelector("#tool-result")){completed=true;rrTrack("tool_completed")}});if(document.body)obs.observe(document.body,{childList:true,subtree:true});
try{
 if("PerformanceObserver" in window){
  if(PerformanceObserver.supportedEntryTypes?.includes("largest-contentful-paint")){let lcp=0;const o=new PerformanceObserver(list=>{for(const e of list.getEntries())lcp=Math.max(lcp,e.startTime)});o.observe({type:"largest-contentful-paint",buffered:true});addEventListener("visibilitychange",()=>{if(document.visibilityState==="hidden"&&lcp)rrTrack("web_vital",{metric_name:"LCP",metric_value:Math.round(lcp)})},{once:true})}
  if(PerformanceObserver.supportedEntryTypes?.includes("layout-shift")){let cls=0;const o=new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)cls+=e.value});o.observe({type:"layout-shift",buffered:true});addEventListener("visibilitychange",()=>{if(document.visibilityState==="hidden")rrTrack("web_vital",{metric_name:"CLS",metric_value:Number(cls.toFixed(4))})},{once:true})}
  if(PerformanceObserver.supportedEntryTypes?.includes("event")){let inp=0;const o=new PerformanceObserver(list=>{for(const e of list.getEntries())if(e.interactionId)inp=Math.max(inp,e.duration)});o.observe({type:"event",durationThreshold:40,buffered:true});addEventListener("visibilitychange",()=>{if(document.visibilityState==="hidden"&&inp)rrTrack("web_vital",{metric_name:"INP",metric_value:Math.round(inp)})},{once:true})}
 }
}catch{}
})();