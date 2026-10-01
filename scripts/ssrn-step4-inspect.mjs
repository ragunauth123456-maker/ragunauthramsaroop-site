import process from 'node:process'
import { chromium } from 'playwright'

const EMAIL=process.env.SSRN_EMAIL
const PASSWORD=process.env.SSRN_PASSWORD
if(!EMAIL||!PASSWORD) throw new Error('Missing SSRN credentials')

const browser=await chromium.launch({headless:true,args:['--disable-blink-features=AutomationControlled']})
const context=await browser.newContext({viewport:{width:1440,height:1100},userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36'})
const page=await context.newPage()
page.setDefaultTimeout(30000)

async function firstVisible(loc){for(let i=0;i<await loc.count();i++){const x=loc.nth(i);if(await x.isVisible().catch(()=>false))return x}return null}
async function cookies(){const a=page.locator('#onetrust-accept-btn-handler');await a.waitFor({state:'visible',timeout:7000}).catch(()=>{});if(await a.isVisible().catch(()=>false)){await a.click({force:true});await page.waitForTimeout(700)}}
async function login(){await page.goto('https://hq.ssrn.com/submissions/MyPapers.cfm',{waitUntil:'domcontentloaded',timeout:60000});await cookies();const pw=await firstVisible(page.locator('input[type="password"]'));if(!pw)return;const em=await firstVisible(page.locator('input[name="input-email"],input[placeholder*="Email" i],input[type="email"]'));if(!em)throw new Error('No email field');await em.fill(EMAIL);await pw.fill(PASSWORD);await cookies();let b=await firstVisible(page.locator('#signinBtn'));if(!b)b=await firstVisible(page.getByRole('button',{name:/sign in/i}));if(!b)throw new Error('No sign in button');await b.click();await page.waitForTimeout(5000);if(await firstVisible(page.locator('input[type="password"]')))throw new Error('Login failed')}
async function clickBtn(name){const b=await firstVisible(page.getByRole('button',{name}));if(!b)throw new Error('Button not found '+name);await b.click({force:true});await page.waitForTimeout(1200)}
async function saveStep(){await clickBtn(/^Save$/i);await page.keyboard.press('Escape').catch(()=>{});await page.waitForTimeout(400)}
function clean(s){return String(s??'').replace(/\s+/g,' ').trim()}
async function dump(tag){console.log('=== '+tag+' ===');console.log('URL='+page.url());console.log('HEADINGS='+clean((await page.locator('h1,h2,h3').allTextContents().catch(()=>[])).join(' | ')));console.log('BODY='+clean(await page.locator('body').innerText().catch(()=> '')).slice(0,18000));const controls=await page.locator('input,textarea,select,button').evaluateAll(es=>es.slice(0,260).map((e,i)=>({i,tag:e.tagName,type:e.getAttribute('type'),id:e.id,name:e.getAttribute('name'),placeholder:e.getAttribute('placeholder'),value:('value'in e)?e.value:null,text:(e.textContent||'').trim().slice(0,500),checked:('checked'in e)?e.checked:null}))).catch(()=>[]);for(const x of controls){if(x.type==='password')continue;console.log('CTRL '+JSON.stringify(x))}}

await login()
await page.goto('https://hq.ssrn.com/submission.cfm?submission-id=20260925-200912623',{waitUntil:'domcontentloaded',timeout:60000})
await cookies()

let body=clean(await page.locator('body').innerText().catch(()=>''))
if(body.includes('Step 2: Confirm Key Submission Details')){
  const date=page.locator('input[placeholder="dd/mm/yyyy"]').first()
  if(await date.isVisible().catch(()=>false) && !await date.inputValue().catch(()=>''))await date.fill('25/09/2026')
  await saveStep()
  await clickBtn(/Next Step/i)
}
body=clean(await page.locator('body').innerText().catch(()=>''))
if(!body.includes('Step 3: Author Information'))throw new Error('Not on Step 3')

const search=page.locator('#author-search')
await search.fill(EMAIL)
await search.press('Enter')
await page.waitForTimeout(1700)
const name=page.getByText('Ragunauth Ramsaroop',{exact:true}).first()
if(!await name.isVisible().catch(()=>false))throw new Error('Exact SSRN author result not visible')
console.log('AUTHOR_NODE='+JSON.stringify(await name.evaluate(e=>({tag:e.tagName,class:e.className,parent:e.parentElement?.outerHTML?.slice(0,5000)}))))
await name.click({force:true})
await page.waitForTimeout(1000)
console.log('POST_AUTHOR_CLICK='+clean(await page.locator('body').innerText().catch(()=>'')).slice(0,7000))
await saveStep()
await clickBtn(/Next Step/i)
await dump('STEP4')
await page.screenshot({path:'ssrn-step4.png',fullPage:true})
await browser.close()
