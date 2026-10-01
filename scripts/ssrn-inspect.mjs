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
  const accept = page.locator('#onetrust-accept-btn-handler')
  await accept.waitFor({state:'visible',timeout:7000}).catch(()=>{})
  if(await accept.isVisible().catch(()=>false)) {
    await accept.click({force:true}).catch(()=>{})
    await page.waitForTimeout(800)
  }
  const close = await firstVisible(page.locator('.onetrust-close-btn-handler')).catch(()=>null)
  if(close) await close.click({force:true}).catch(()=>{})
  await page.locator('#onetrust-consent-sdk').waitFor({state:'hidden',timeout:5000}).catch(()=>{})
}
async function signIn() {
  await page.goto('https://hq.ssrn.com/submissions/MyPapers.cfm',{waitUntil:'domcontentloaded',timeout:60000})
  await dismissCookieOverlay(page)
  const pw=await firstVisible(page.locator('input[type="password"]'))
  if(!pw) return
  const meta = await page.locator('input').evaluateAll(els => els.map((e,i)=>({i,type:e.getAttribute('type'),name:e.getAttribute('name'),id:e.id,placeholder:e.getAttribute('placeholder'),visible:!!(e.offsetWidth||e.offsetHeight||e.getClientRects().length)})))
  console.log('LOGIN_INPUTS='+JSON.stringify(meta))
  const email=await firstVisible(page.locator('input[placeholder*="Email" i],input[type="email"],input[name*="email" i],input[id*="email" i],input[name*="user" i],input[id*="user" i],input[type="text"]'))
  if(!email) throw new Error('No visible email/user input found')
  console.log('EMAIL_FIELD='+JSON.stringify({name:await email.getAttribute('name'),id:await email.getAttribute('id'),placeholder:await email.getAttribute('placeholder'),type:await email.getAttribute('type')}))
  await email.fill(EMAIL)
  await pw.fill(PASSWORD)
  console.log('FILLED_LENGTHS='+JSON.stringify({email:(await email.inputValue()).length,password:(await pw.inputValue()).length}))
  const forms=await page.locator('form').evaluateAll(fs=>fs.map((f,i)=>({i,action:f.getAttribute('action'),method:f.getAttribute('method'),id:f.id,name:f.getAttribute('name')})))
  console.log('FORMS='+JSON.stringify(forms))
  await dismissCookieOverlay(page)
  let btn=await firstVisible(page.locator('#signinBtn'))
  if(!btn) btn=await firstVisible(page.getByRole('button',{name:/sign in/i}))
  if(!btn) throw new Error('No sign in button')
  await Promise.all([
    page.waitForLoadState('domcontentloaded').catch(()=>{}),
    btn.click()
  ])
  await page.waitForTimeout(5000)
  if(await firstVisible(page.locator('input[type="password"]'))) {
    const body=await page.locator('body').innerText().catch(()=> '')
    console.log('LOGIN_FAIL_URL='+page.url())
    console.log('LOGIN_FAIL_TEXT='+body.slice(0,3000).replace(/\n/g,' | '))
    await page.screenshot({path:'ssrn-inspect.png',fullPage:true}).catch(()=>{})
    throw new Error('Login failed')
  }
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

const license6 = page.locator('#license-option-6')
if (await license6.count()) {
  await license6.check({ force: true }).catch(()=>{})
  console.log('LICENSE6_CHECKED=' + await license6.isChecked().catch(()=>false))
}
const next6 = await firstVisible(page.getByRole('button',{name:/Next Step/i}))
if(!next6) throw new Error('Step 6 Next Step not found')
await next6.click({force:true})
await page.waitForTimeout(2000)
await dump('STEP-7-REVIEW')
const labels7 = await page.locator('label').allTextContents().catch(()=>[])
console.log('STEP7_LABELS='+JSON.stringify(labels7.map(x=>safe(x)).filter(Boolean)))
const body7 = await page.locator('body').innerText().catch(()=> '')
console.log('STEP7_BODY_LONG='+body7.slice(0,14000).replace(/\n/g,' | '))

const submit = await firstVisible(page.getByRole('button',{name:/^Submit$/i}))
if(!submit) throw new Error('Submit button not found on Step 7')
await submit.click({force:true})
await page.waitForLoadState('domcontentloaded').catch(()=>{})
await page.waitForTimeout(2500)
console.log('AFTER_SUBMIT_URL='+page.url())
console.log('AFTER_SUBMIT_TEXT='+(await page.locator('body').innerText().catch(()=> '')).slice(0,9000).replace(/\n/g,' | '))

await page.goto('https://hq.ssrn.com/submission.cfm?submission-id=20260930-150901833',{waitUntil:'domcontentloaded',timeout:60000})
await dismissCookieOverlay(page)
await dump('SECOND-DRAFT-CURRENT-STEP')
await page.screenshot({path:'ssrn-inspect.png',fullPage:true})
await browser.close()
