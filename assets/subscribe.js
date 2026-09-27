(()=>{
"use strict";
const $=id=>document.getElementById(id),mail="ragunauthramsaroop@icloud.com";
const topics=[...document.querySelectorAll('[name="rr-topic"]')];
const selected=()=>topics.filter(x=>x.checked).map(x=>x.value);
function value(){return{name:$("sub-name").value.trim(),email:$("sub-email").value.trim(),topics:selected(),consent:$("sub-consent").checked}}
function validate(){const v=value();if(!v.email||!$("sub-email").checkValidity())throw Error("Enter a valid email address.");if(!v.topics.length)throw Error("Select at least one briefing topic.");if(!v.consent)throw Error("Read and accept the explicit email request consent.");return v}
function message(v,unsubscribe=false){if(unsubscribe)return"Please remove my address from all RR briefing and research email lists.\n\nEmail: "+v.email+"\n\nPlease confirm when the request has been processed.";
return"Hello Ragunauth,\n\nI request inclusion in the briefing topics below. I understand this opens my own email app and no request is delivered until I press Send.\n\nName: "+(v.name||"Not provided")+"\nEmail: "+v.email+"\nTopics: "+v.topics.join(", ")+"\nConsent: Explicit opt-in requested\n\nPlease confirm my subscription and provide an unsubscribe route before routine newsletters begin.\n";}
function status(text){$("sub-status").textContent=text}
function draft(unsubscribe=false){let v;try{v=validate()}catch(e){if(unsubscribe){v={email:$("sub-email").value.trim(),name:"",topics:[]};if(!v.email||!$("sub-email").checkValidity()){status("Enter the email address to unsubscribe.");return}}else{status(e.message);return}}
const subject=encodeURIComponent(unsubscribe?"RR Briefings unsubscribe request":"RR Briefings opt-in subscription request"),body=encodeURIComponent(message(v,unsubscribe));location.href="mailto:"+mail+"?subject="+subject+"&body="+body;status("Your email draft is prepared. Your request is not submitted until you send it from your email application.")}
$("sub-send").onclick=()=>draft(false);$("sub-unsubscribe").onclick=()=>draft(true);
$("sub-copy").onclick=async()=>{let v;try{v=validate()}catch(e){status(e.message);return}try{await navigator.clipboard.writeText(message(v));status("Your opt-in request was copied. Send it to "+mail+" from your email account.")}catch{status("Clipboard unavailable. Use Prepare opt-in email.")}};
const prefKey="rrBriefingPreferenceDraftV1";$("sub-save").onclick=()=>{const v=value();try{localStorage.setItem(prefKey,JSON.stringify({topics:v.topics,stored_at:new Date().toISOString()}));status("Only your topic preferences were saved in this browser. No email address was stored.")}catch{status("Local browser storage is unavailable.")}};
try{const v=JSON.parse(localStorage.getItem(prefKey)||"null");if(v?.topics)topics.forEach(x=>x.checked=v.topics.includes(x.value))}catch{}
})();