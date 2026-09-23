(()=>{
"use strict";
function run(){
 const main=document.querySelector("main");if(main&&!main.id)main.id="main-content";
 if(main&&!document.querySelector(".rr-skip-link")){const a=document.createElement("a");a.className="rr-skip-link";a.href="#main-content";a.textContent="Skip to main content";document.body.insertBefore(a,document.body.firstChild)}
 document.querySelectorAll(".field").forEach((box,i)=>{const label=box.querySelector("label"),control=box.querySelector("input,select,textarea");if(label&&control&&!label.htmlFor){if(!control.id)control.id="rr-field-"+i;label.htmlFor=control.id}});
 document.querySelectorAll("#out").forEach(x=>{if(!x.hasAttribute("aria-live"))x.setAttribute("aria-live","polite")});
 document.querySelectorAll('a[target="_blank"]').forEach(a=>{const rel=new Set((a.getAttribute("rel")||"").split(/\s+/).filter(Boolean));rel.add("noopener");rel.add("noreferrer");a.setAttribute("rel",[...rel].join(" "))});
 const st=document.createElement("style");st.textContent=".rr-skip-link{position:fixed;left:10px;top:-60px;z-index:2147483647;background:#fff;color:#08271d;padding:10px 14px;border-radius:8px;font:800 14px system-ui;box-shadow:0 4px 20px rgba(0,0,0,.25)}.rr-skip-link:focus{top:10px}*:focus-visible{outline:3px solid #b8893b!important;outline-offset:3px!important}";document.head.appendChild(st);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run();
})();