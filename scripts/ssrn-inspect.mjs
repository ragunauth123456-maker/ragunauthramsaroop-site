import process from 'node:process'
import { chromium } from 'playwright'

const EMAIL = process.env.SSRN_EMAIL
const PASSWORD = process.env.SSRN_PASSWORD
if (!EMAIL || !PASSWORD) throw new Error('Missing SSRN credentials')

const browser = await chromium.launch({ headless: true, args:['--disable-blink-features=AutomationControlled'] })
const context = await browser.newContext({ viewport:{width:1440,height:1100}, userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36' })
const page = await context.newPage()
page.setDefaultTimeout(30000)

async function firstVisible(locator) {
  const count = await locator.count()
  for (let i=0;i<count;i++){ const x=locator.nth(i); if(await x.isVisible().catch(()=>false)) return x }
  return null
}
async function dismissCookieOverlay(page) {
  for (const selector of ['#onetrust-accept-btn-handler','#onetrust-reject-all-handler','.onetrust-close-btn-handler']) {
    const b=await firstVisible(page.locator(selector)).catch(()=>null); if(b) await b.click({force:true}).catch(()=>{})
  }
  await page.evaluate(()=>{document.querySelector('#onetrust-consent-sdk')?.remove();document.documentElement.style.overflow='';document.body.style.overflow=''}).catch(()=>{})
}
async function signIn() {
  await page.goto('https://hq.ssrn.com/submissions/MyPapers.cfm',{waitUntil:'domcontentloaded',timeout:60000})
  await dismissCookieOverlay(page)
  const pw=await firstVisible(page.locator('input[type="password"]'))
  if(!pw) return
  const email=await firstVisible(page.locator('input[placeholder*="Email" i],input[type="email"],input[name*="email" i],input[id*="email" i],input[name*="user" i],input[id*="user" i]'))
  if(email) await email.fill(EMAIL)
  await pw.fill(PASSWORD)
  const btn=await firstVisible(page.getByRole('button',{name:/sign in/i}))
  if(!btn) throw new Error('No sign in button')
  await btn.click({force:true})
  await page.waitForTimeout(2500)
  if(await firstVisible(page.locator('input[type="password"]'))) throw new Error('Login failed')
}
function safe(s){return String(s??'').replace(/\s+/g,' ').trim().slice(0,600)}
async function dump(label){
  console.log('--- '+label+' ---')
  console.log('URL='+page.url())
  console.log('TITLE='+safe(await page.title()))
  const h = await page.locator('h1,h2,h3').allTextContents().catch(()=>[])
  console.log('HEADINGS='+safe(h.join(' | ')))
  const body = await page.locator('body').innerText().catch(()=> '')
  console.log('BODY='+safe(body).slice(0,5000))
  const controls = await page.locator('input,textarea,select,button,a').evaluateAll(els => els.slice(0,250).map((e,i)=>({
    i,tag:e.tagName,type:e.getAttribute('type'),name:e.getAttribute('name'),id:e.id,placeholder:e.getAttribute('placeholder'),
    value:(e instanceof HTMLInputElement || e instanceof HTMLTextAreaElement || e instanceof HTMLSelectElement)?e.value:null,
    text:(e.textContent||'').trim().slice(0,160),
    href:e.getAttribute('href'),
    checked:(e instanceof HTMLInputElement)?e.checked:null,
    options:(e instanceof HTMLSelectElement)?Array.from(e.options).map(o=>({t:(o.textContent||'').trim(),v:o.value,sel:o.selected})).slice(0,80):null
  })))
  for(const x of controls){
    if(/password/i.test(String(x.type)) || /pass/i.test(String(x.name)) || /pass/i.test(String(x.id))) continue
    console.log('CTRL '+JSON.stringify(x))
  }
}
await signIn()
await page.goto('https://hq.ssrn.com/submission.cfm?submission-id=20260925-200912623',{waitUntil:'domcontentloaded',timeout:60000})
await dismissCookieOverlay(page)
await dump('DRAFT-FIRST-PAGE')
await page.screenshot({path:'ssrn-inspect.png',fullPage:true})
await browser.close()
