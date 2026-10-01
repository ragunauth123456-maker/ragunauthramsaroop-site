import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { chromium } from 'playwright'

const EMAIL = process.env.SSRN_EMAIL
const PASSWORD = process.env.SSRN_PASSWORD

if (!EMAIL || !PASSWORD) {
  throw new Error('Missing SSRN_EMAIL or SSRN_PASSWORD environment variable')
}

const BASE_ASSET = 'https://d0ed54fb-3316-41e7-8a1f-a05ef6e61615.sandbox.floot.app'

const papers = [
  {
    submissionId: '20260925-200912623',
    name: 'SSRN_READY_The_Physical_Limits_of_Artificial_Intelligence.pdf',
    url: BASE_ASSET + '/_cdn/static/b4f42504-bb34-44a1-b9c7-695a07d298f8-SSRN_READY_The_Physical_Limits_of_Artificial_Intelligence.pdf'
  },
  {
    submissionId: '20260930-150901833',
    name: 'SSRN_READY_From_Ore_to_Optionality.pdf',
    url: BASE_ASSET + '/_cdn/static/9c44ac8e-ebdd-456a-829b-4d3f841a8b64-SSRN_READY_From_Ore_to_Optionality.pdf'
  },
  {
    submissionId: '20260930-150923239',
    name: 'SSRN_READY_Fresh_Water_The_Next_Strategic_Commodity.pdf',
    url: BASE_ASSET + '/_cdn/static/13b297c8-682f-4bfd-b6fc-ebd6cf967030-SSRN_READY_Fresh_Water_The_Next_Strategic_Commodity.pdf'
  },
  {
    submissionId: '20260930-190908378',
    name: 'SSRN_READY_Beyond_Employment.pdf',
    url: BASE_ASSET + '/_cdn/static/2fc7d82c-1fb3-4f3b-9b5c-97dcfa1c22b0-SSRN_READY_Beyond_Employment.pdf'
  },
  {
    submissionId: '20260930-190910213',
    name: 'SSRN_READY_Karpowership_Guyana_2035.pdf',
    url: BASE_ASSET + '/_cdn/static/2666c7fc-ef4e-4a90-a1e1-6508785a95bf-SSRN_READY_Karpowership_Guyana_2035.pdf'
  },
  {
    submissionId: '20260930-190913144',
    name: 'SSRN_READY_The_Geopolitics_of_Gold.pdf',
    url: BASE_ASSET + '/_cdn/static/c8cd1271-378b-4cbe-b9bd-8d56c5c0e94a-SSRN_READY_The_Geopolitics_of_Gold.pdf'
  },
  {
    submissionId: '20260930-190919009',
    name: 'SSRN_READY_Guyana_Development_Bank.pdf',
    url: BASE_ASSET + '/_cdn/static/57754df9-e613-4f12-9812-e6e461563365-SSRN_READY_Guyana_Development_Bank.pdf'
  },
  {
    submissionId: '20260930-190928409',
    name: 'SSRN_READY_Sovereign_AI.pdf',
    url: BASE_ASSET + '/_cdn/static/8282db85-9a13-4b60-9bef-0e5474223625-SSRN_READY_Sovereign_AI.pdf'
  },
  {
    submissionId: '20260930-190934140',
    name: 'SSRN_READY_The_Trust_Deficit.pdf',
    url: BASE_ASSET + '/_cdn/static/02900745-78bd-4347-92bd-d0fd865cc6d5-SSRN_READY_The_Trust_Deficit.pdf'
  }
]

const outDir = path.resolve('ssrn-run')
const downloadsDir = path.join(outDir, 'downloads')
await fs.mkdir(downloadsDir, { recursive: true })

async function downloadPdf(item) {
  const target = path.join(downloadsDir, item.name)
  const response = await fetch(item.url, {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  })
  if (!response.ok) throw new Error(`Download failed for ${item.name}: HTTP ${response.status}`)
  const bytes = Buffer.from(await response.arrayBuffer())
  if (bytes.length < 5 || bytes.subarray(0, 5).toString() !== '%PDF-') {
    throw new Error(`Downloaded asset is not a PDF: ${item.name}`)
  }
  await fs.writeFile(target, bytes)
  return target
}

async function firstVisible(locator) {
  const count = await locator.count()
  for (let i = 0; i < count; i += 1) {
    const candidate = locator.nth(i)
    if (await candidate.isVisible().catch(() => false)) return candidate
  }
  return null
}

async function dismissCookieOverlay(page) {
  const selectors = [
    '#onetrust-accept-btn-handler',
    '#onetrust-reject-all-handler',
    '.onetrust-close-btn-handler',
    'button[aria-label*="Close" i]'
  ]
  for (const selector of selectors) {
    const button = await firstVisible(page.locator(selector)).catch(() => null)
    if (button) {
      await button.click({ force: true }).catch(() => {})
      await page.waitForTimeout(300)
    }
  }
  await page.evaluate(() => {
    const sdk = document.querySelector('#onetrust-consent-sdk')
    if (sdk) sdk.remove()
    document.documentElement.style.overflow = ''
    document.body.style.overflow = ''
  }).catch(() => {})
}

async function signIn(page) {
  await page.goto('https://hq.ssrn.com/submissions/MyPapers.cfm', { waitUntil: 'domcontentloaded', timeout: 60000 })
  await dismissCookieOverlay(page)

  const password = await firstVisible(page.locator('input[type="password"]'))
  if (!password) {
    if (/MyPapers\.cfm/i.test(page.url())) return
    throw new Error(`Unexpected SSRN page before login: ${page.url()}`)
  }

  const emailSelectors = [
    'input[placeholder*="Email" i]',
    'input[type="email"]',
    'input[name*="email" i]',
    'input[id*="email" i]',
    'input[name*="user" i]',
    'input[id*="user" i]'
  ]
  for (const selector of emailSelectors) {
    const email = await firstVisible(page.locator(selector))
    if (email) {
      await email.fill(EMAIL)
      break
    }
  }

  await password.fill(PASSWORD)

  let signInButton = await firstVisible(page.getByRole('button', { name: /sign in/i }))
  if (!signInButton) {
    signInButton = await firstVisible(page.locator('input[type="submit"][value*="sign" i]'))
  }
  if (!signInButton) throw new Error('SSRN Sign in button was not found')

  await dismissCookieOverlay(page)
  await Promise.all([
    page.waitForLoadState('domcontentloaded').catch(() => {}),
    signInButton.click({ force: true })
  ])

  await page.waitForTimeout(2000)

  if (await firstVisible(page.locator('input[type="password"]'))) {
    const bodyText = await page.locator('body').innerText().catch(() => '')
    console.log('SSRN_LOGIN_URL=' + page.url())
    console.log('SSRN_LOGIN_TITLE=' + await page.title().catch(() => ''))
    console.log('SSRN_LOGIN_TEXT=' + bodyText.slice(0, 5000).replace(/\n/g, ' | '))
    await page.screenshot({ path: path.join(outDir, 'login-failed.png'), fullPage: true }).catch(() => {})
    throw new Error('SSRN login did not complete. Check credentials or any SSRN verification prompt.')
  }
}

async function selectPreprint(page) {
  const selects = page.locator('select')
  const count = await selects.count()
  for (let i = 0; i < count; i += 1) {
    const select = selects.nth(i)
    const options = await select.locator('option').allTextContents().catch(() => [])
    const index = options.findIndex(x => /preprint/i.test(x))
    if (index >= 0) {
      const option = select.locator('option').nth(index)
      const value = await option.getAttribute('value')
      if (value !== null) {
        await select.selectOption(value)
        return true
      }
    }
  }
  return false
}

async function ensureAuthorSelected(page) {
  const byLabel = page.getByLabel(/I am the Author/i)
  if (await byLabel.count()) {
    const control = byLabel.first()
    if (await control.isVisible().catch(() => false)) {
      await control.check().catch(() => {})
      return
    }
  }

  const labels = page.locator('label')
  const count = await labels.count()
  for (let i = 0; i < count; i += 1) {
    const label = labels.nth(i)
    const text = (await label.innerText().catch(() => '')).trim()
    if (/I am the Author/i.test(text)) {
      await label.click().catch(() => {})
      return
    }
  }
}

async function clickSave(page) {
  const candidates = [
    page.getByRole('button', { name: /save and next step/i }),
    page.getByRole('button', { name: /^save$/i }),
    page.locator('input[type="submit"][value*="Save" i]')
  ]

  for (const locator of candidates) {
    const button = await firstVisible(locator)
    if (button) {
      await Promise.all([
        page.waitForLoadState('domcontentloaded').catch(() => {}),
        button.click()
      ])
      return
    }
  }
  throw new Error('No visible SSRN Save button found')
}

const browser = await chromium.launch({
  headless: true,
  args: ['--disable-blink-features=AutomationControlled']
})

const context = await browser.newContext({
  viewport: { width: 1440, height: 1100 },
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36'
})

const page = await context.newPage()
page.setDefaultTimeout(30000)

const results = []

try {
  await signIn(page)

  if (process.env.SSRN_MODE === 'inspect') {
    const metadata = {
      '20260930-150901833': {
        title: 'From Ore to Optionality: Why Critical-Mineral Partnerships Must Deliver Industrial Capability, Not Only Supply Security',
        date: '29/09/2026',
        abstract: 'This paper examines why critical-mineral partnerships should be judged by the industrial capability they create, not only by volumes secured. It argues that criticality is relational rather than geological and that strategic chokepoints often sit in refining, processing, qualification, infrastructure, technology, finance and market access after the mine. Drawing on current institutional evidence, official policy documents, mineral-market data, comparative case analysis and selected scholarship, the study assesses value addition, export restrictions, supplier qualification, infrastructure, local participation, ESG and recycling. It proposes the OPTION framework and treats strategic optionality as the objective: dependable supply for buyers alongside multiple credible pathways for producer economies into higher-value activity, technology, finance and markets. The paper does not equate value addition with maximum domestic processing; processing choices are assessed against energy, infrastructure, technology, scale and market access.',
        keywords: ['critical minerals','industrial policy','mining','value addition','supply chains','ESG','strategic partnerships','OPTION framework']
      },
      '20260930-150923239': {
        title: 'Fresh Water: The Next Strategic Commodity',
        date: '22/09/2026',
        abstract: 'This paper argues that dependable freshwater access is becoming a strategic constraint on growth, industry, infrastructure, food security and capital allocation. It distinguishes water security from the idea that freshwater will trade like crude oil or metals. Because water is local, heavy, politically sensitive, ecologically connected and indispensable to life, the emerging economic value lies in reliable access and in the infrastructure and systems that support it, including treatment, reuse, storage, desalination, efficient irrigation, leakage reduction, monitoring and industrial closed-loop systems. The analysis examines agriculture, cities, AI and data centres, mining, energy, climate variability, capital markets and policy. It treats safe drinking water and sanitation as a human right and limits the investment thesis to infrastructure, reliability, efficiency and risk management.',
        keywords: ['water security','freshwater','infrastructure','climate risk','agriculture','data centres','mining','energy','water reuse','capital allocation']
      },
      '20260930-190908378': {
        title: 'Beyond Employment: Enterprise Stewardship and the Ownership Orientation of Executive Leadership',
        date: '16/09/2026',
        abstract: 'This paper separates legal ownership from an ownership orientation in executive and employee decision-making. A shareholder owns equity and legal rights; a manager or employee without equity does not become an owner through attitude. The paper defines ownership orientation as enterprise-wide, multi-period judgment that treats organisational resources, risks, relationships and reputation as assets held in stewardship. It integrates agency theory, stewardship theory, psychological ownership, work design, employee voice, governance, risk management and stakeholder management. The evidence does not support claims that ownership language alone transforms performance. The paper instead argues for an enterprise-stewardship system built on decision-relevant information, defined authority, accountability, employee voice, competence, ethical culture, risk controls and reciprocal fairness, with applications to leadership, governance, mining, energy and infrastructure.',
        keywords: ['enterprise stewardship','ownership orientation','executive leadership','governance','risk','psychological ownership','stakeholder management','employee voice']
      },
      '20260930-190910213': {
        title: 'Karpowership Guyana 2035: From Bridging Power to Strategic Energy Infrastructure',
        date: '16/09/2026',
        abstract: 'This strategic white paper examines Karpowership\'s potential long-term role in Guyana as the power system shifts from shortage toward rapid demand growth, new generation blocks, stronger transmission, digital control and new industrial loads. It distinguishes measured load, planning potential and firm commercial demand. The central argument is that Wales Gas-to-Energy changes the economics of Karpowership\'s current role but does not eliminate the need for reliability and system optionality. The paper proposes a portfolio-migration strategy centred on near-term bridge value, post-Wales reliability services, a gated Region Six/Berbice option, industrial and mining power agreements, domestic-gas conversion where feasible, storage and renewable firming, and stronger local technical capability. Scenario triggers, commercial architecture, execution sequencing, governance and risk controls are developed through 2035.',
        keywords: ['Karpowership','Guyana','energy','power','Gas-to-Energy','reliability','industrial power','LNG','storage','energy strategy']
      },
      '20260930-190913144': {
        title: 'The Geopolitics of Gold: Central Banks, Reserve Diversification and the Strategic Revaluation of a Monetary Asset',
        date: '14/09/2026',
        abstract: 'This paper examines gold\'s renewed role in central-bank reserve management and argues that the current cycle is best understood through valuation, diversification, geopolitical optionality and institutional credibility. It distinguishes changes in the market value of official gold holdings from changes in physical holdings and cautions against treating gold and currency reserve shares as directly interchangeable. The paper reviews recent official-sector demand, reserve composition, geopolitical considerations, responsible sourcing and domestic gold-purchase programmes. It does not interpret higher gold holdings as evidence of imminent displacement of the dollar-centred reserve system. For governments and boards, the analysis positions gold within strategic asset allocation, sovereign risk management, responsible sourcing and industrial policy, while emphasizing liquidity, governance, custody, traceability and monetary-policy risks.',
        keywords: ['gold','central banks','reserve diversification','geopolitics','monetary policy','sovereign risk','responsible sourcing','reserve management']
      },
      '20260930-190919009': {
        title: 'Guyana Development Bank: From Access to Finance to Productive Economic Participation',
        date: '21/09/2026',
        abstract: 'This paper evaluates the proposed Guyana Development Bank as a development-finance institution intended to widen productive economic participation rather than merely expand access to credit. It reviews the announced capital structure, zero-interest and collateral-free lending offer, co-financing concept, digital and assisted-access model, mentoring and business-development support, and the relationship with existing financial institutions. The analysis distinguishes implementation announcements from verified operating results and places the Bank within Guyana\'s wider credit and SME-finance system. The central policy test is additionality: whether the Bank generates productive activity that private institutions would not otherwise finance on similar terms. The paper develops governance, risk, implementation, evaluation and performance frameworks focused on borrower survival, repayment, productivity, jobs, regional inclusion and graduation into commercial finance.',
        keywords: ['Guyana Development Bank','development finance','SMEs','financial inclusion','governance','productive finance','credit','economic participation']
      },
      '20260930-190928409': {
        title: 'Sovereign AI: Who Controls the Intelligence Infrastructure of the Global Economy?',
        date: '18/09/2026',
        abstract: 'This monograph examines sovereign artificial intelligence as a system of technological, economic, legal, infrastructural and geopolitical dependencies. It argues that sovereignty cannot be reduced to server location or ownership of a single layer of the AI stack. The study defines sovereign AI as the capacity to preserve strategic choice over critical AI functions under stress and develops a twelve-domain Sovereign AI Systems Framework spanning semiconductors, compute, cloud, physical data-centre infrastructure, energy and water, connectivity, data, models, software, talent, capital and governance. It proposes a Sovereign AI Resilience Index, dependency graph, maturity model, early-warning dashboard and procurement test. Multiple pathways to 2040 are treated as stress tests rather than forecasts. The core objective is strategic optionality, legal authority and credible alternatives that reduce coercive lock-in without requiring full domestic self-sufficiency.',
        keywords: ['sovereign AI','artificial intelligence','digital sovereignty','AI compute','semiconductors','cloud computing','data governance','geopolitics','strategic autonomy','AI infrastructure']
      },
      '20260930-190934140': {
        title: 'The Trust Deficit: Managing Transformation in a Fragmented World',
        date: '21/09/2026',
        abstract: 'This monograph argues that warranted institutional trust functions as strategic infrastructure for collective action. It lowers the friction required to coordinate behaviour, absorb uncertainty, mobilise capital, implement reform, sustain compliance and maintain cooperation when interests diverge. The analysis distinguishes warranted trust from popularity, reputation or blind confidence and examines credibility, competence, fairness, voice, integrity, openness and delivery. It proposes the Trust-Execution Resilience Architecture (TERA) as a diagnostic framework rather than a validated psychometric scale or ranking system. Drawing on official, multilateral, peer-reviewed and clearly identified commercial survey evidence, the paper treats scenarios as exploratory stress tests rather than forecasts. The objective is justified trust grounded in testable claims, credible commitments, explainable decisions, visible trade-offs, correctable errors and demonstrated delivery.',
        keywords: ['institutional trust','governance','leadership','cooperation','execution capacity','legitimacy','resilience','TERA']
      }
    }

    for (const item of papers) {
      const meta = metadata[item.submissionId]
      if (!meta) continue
      await page.goto(`https://hq.ssrn.com/submission.cfm?submission-id=${item.submissionId}`, {
        waitUntil: 'domcontentloaded',
        timeout: 60000
      })
      await dismissCookieOverlay(page)
      await page.waitForTimeout(3200)
      let body = (await page.locator('body').innerText()).replace(/\s+/g,' ')
      if (/Step 2:\s*Confirm Key Submission Details/i.test(body)) {
        const title = page.locator('#title')
        const abstract = page.locator('#abstract')
        await title.fill(meta.title)
        await abstract.fill(meta.abstract)
        const dateInput = page.locator('input[placeholder="dd/mm/yyyy"]').first()
        await dateInput.fill(meta.date)
        const keywordInput = page.locator('#add-keyword')
        for (const kw of meta.keywords) {
          await keywordInput.fill(kw)
          await keywordInput.press('Enter')
          await page.waitForTimeout(120)
        }
        await page.waitForTimeout(500)
        const next = await firstVisible(page.getByRole('button', { name: /^Next Step$/i }))
        if (!next) throw new Error('Step 2 Next Step not found for ' + item.submissionId)
        await next.click({ force: true })
        await page.waitForTimeout(3500)
        body = (await page.locator('body').innerText()).replace(/\s+/g,' ')
      }
      const step = body.match(/Step\s+\d+\s*:\s*[^0-9]+?(?=\s+(?:Save|Previous Step|Next Step|Submission Progress|$))/i)?.[0] || body.slice(0,280)
      console.log('SSRN_STEP2_ADVANCE=' + item.submissionId + ' :: ' + step)
    }
    process.exit(0)
  }

  for (const item of papers) {
    const record = {
      submissionId: item.submissionId,
      file: item.name,
      status: 'started'
    }

    try {
      const pdfPath = await downloadPdf(item)
      record.bytes = (await fs.stat(pdfPath)).size

      await page.goto(`https://hq.ssrn.com/submission.cfm?submission-id=${item.submissionId}`, {
        waitUntil: 'domcontentloaded',
        timeout: 60000
      })

      if (await firstVisible(page.locator('input[type="password"]'))) {
        await signIn(page)
        await page.goto(`https://hq.ssrn.com/submission.cfm?submission-id=${item.submissionId}`, {
          waitUntil: 'domcontentloaded',
          timeout: 60000
        })
      }

      await dismissCookieOverlay(page)
      const fileInput = page.locator('input[type="file"]').first()
      await fileInput.waitFor({ state: 'attached', timeout: 30000 })

      await ensureAuthorSelected(page)
      record.preprintSelected = await selectPreprint(page)

      await fileInput.setInputFiles(pdfPath)
      await page.waitForTimeout(2500)

      const attachedNameVisible =
        await page.getByText(item.name, { exact: false }).count().catch(() => 0)

      record.filenameVisibleBeforeSave = attachedNameVisible > 0

      await clickSave(page)
      await page.waitForTimeout(2500)

      if (await firstVisible(page.locator('input[type="password"]'))) {
        throw new Error('SSRN session expired while saving the draft')
      }

      record.status = 'uploaded'
      record.afterSaveUrl = page.url()
      await page.screenshot({
        path: path.join(outDir, `${item.submissionId}-uploaded.png`),
        fullPage: true
      }).catch(() => {})
    } catch (error) {
      record.status = 'failed'
      record.error = error instanceof Error ? error.message : String(error)
      await page.screenshot({
        path: path.join(outDir, `${item.submissionId}-failed.png`),
        fullPage: true
      }).catch(() => {})
    }

    results.push(record)
    console.log(JSON.stringify(record))
  }
} finally {
  await fs.writeFile(path.join(outDir, 'results.json'), JSON.stringify(results, null, 2))
  await browser.close()
}

const uploaded = results.filter(x => x.status === 'uploaded').length
const failed = results.filter(x => x.status === 'failed').length

console.log(`SSRN upload run complete: ${uploaded} uploaded, ${failed} failed`)

if (failed > 0) process.exitCode = 1
