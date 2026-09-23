/* Privacy-safe engagement events. Never sends tool inputs or free-text content. */
(function(){
  "use strict";
  const slug=()=>location.pathname.split("/").filter(Boolean).slice(-1)[0]||"home";
  const safe=s=>String(s||"").slice(0,120);
  window.rrTrack=function(name,params){
    if(typeof window.gtag!=="function")return;
    const base={page_path:location.pathname,tool_slug:location.pathname.startsWith("/tools/")?slug():""};
    window.gtag("event",name,Object.assign(base,params||{}));
  };
  let started=false,completed=false;
  document.addEventListener("submit",function(e){
    if(location.pathname.startsWith("/tools/")&&e.target.closest("#tool-ui")){
      if(!started){started=true;rrTrack("tool_started");}
    }
  },true);
  document.addEventListener("click",function(e){
    const el=e.target.closest("a,button"); if(!el)return;
    const href=el.getAttribute("href")||"";
    const label=safe((el.textContent||"").trim());
    if(el.matches("[data-copy],#copy"))rrTrack("result_copied");
    else if(el.matches("[data-print],#print"))rrTrack("result_printed");
    else if(el.matches("[data-share],#share,[data-rr-share]"))rrTrack("tool_shared",{share_method:el.dataset.rrShare||"native"});
    else if(href.includes("/tools/downloads/"))rrTrack("template_downloaded",{file_name:href.split("/").pop()});
    else if(href.startsWith("/white-papers/"))rrTrack("white_paper_opened",{link_label:label});
    else if(href.startsWith("/executive-profile/"))rrTrack("profile_opened",{link_label:label});
    else if(href.startsWith("/topics/"))rrTrack("topic_opened",{topic_slug:href.split("/").filter(Boolean).pop()});
  },true);
  const obs=new MutationObserver(function(){
    if(!completed&&document.querySelector("#tool-result")){
      completed=true;rrTrack("tool_completed");
    }
  });
  if(document.body)obs.observe(document.body,{childList:true,subtree:true});
})();