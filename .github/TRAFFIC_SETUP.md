# RR Free Tools: privacy-first traffic and engagement measurement

## What is active today
Google Search Console is already connected for `sc-domain:ragunauthramsaroop.com`.
The GSC Wizard content group **RR Free Tools** covers both `https://ragunauthramsaroop.com/tools/` and `https://www.ragunauthramsaroop.com/tools/`. Group id: `6520cfcb-37cd-4573-ae93-4f579bab98bd`.
Snapshot on 22 September 2026: last 28 days through September 20 showed 11 organic clicks and 152 impressions for the **whole domain**, not the new tools. These tools launched after this measurement window. Recheck after Google has crawled them.
Root sitemap: `https://ragunauthramsaroop.com/sitemap.xml`; all public tools have unique canonicals and social previews.

## Optional free website visit analytics
Cloudflare Web Analytics is free and works with GitHub Pages without migrating DNS. It does not support custom button-click events, so it is for page views, visitor trends and Web Vitals rather than per-button conversion funnels.
1. Sign into an existing Cloudflare account or create a free one. Open **Web Analytics → Add a site** and enter `ragunauthramsaroop.com`.
2. In **Manage site**, copy the site beacon token from the supplied JavaScript snippet.
3. Edit `tools/assets/analytics-loader.js` and replace the blank `CLOUDFLARE_BEACON_TOKEN` with that site's token. The loader is already included sitewide and remains inert while the token is blank.
4. Update `tools/privacy/index.html` to state that Cloudflare Web Analytics is now active, preserving clear visitor disclosure.
5. Submit a PR and verify one test page view in Cloudflare's dashboard. Keep GitHub Pages and the existing DNS unchanged.

Do not install a paid analytics product or add tracking cookies. Never upload tool inputs, résumé text, health data or stakeholder names to analytics.

## SEO and QA
Each tool has a dedicated page with original methodology text, FAQs, related links and a 1200×630 social preview.
`python scripts/validate_site.py` runs locally and on GitHub Actions for pushes and PRs.
The weekly GitHub Actions workflow is prepared as `.github/rr-free-tools-qa.yml.example`. It is not yet active because the currently authorized GitHub OAuth token lacks the `workflow` scope. After explicit GitHub authorization, move the example into `.github/workflows/rr-free-tools-qa.yml`; it will then test pushes and pull requests and check public availability every Monday. Until then, run `python scripts/validate_site.py` and `python scripts/public_smoke.py` manually.
Search impressions and clicks measure search discovery, not time spent, unique engagement actions or completed assessments. Do not equate them.


## No-Cloudflare alternative: Counter.dev
Counter.dev is a hosted, no-cookie, free/pay-when-ready analytics service. It collects aggregate visitor and referrer metrics. The sitewide analytics loader now supports Counter.dev before Cloudflare, and is dormant until configured.

One-time account owner step: create a free Counter.dev account at https://counter.dev/welcome.html?sign-up using your own email and password. From its dashboard, copy the tracking code's public data-id UUID (not your password or session token). Set COUNTER_SITE_ID in tools/assets/analytics-loader.js to that UUID and publish through GitHub. Visit one page and verify the Counter.dev dashboard records a visit. Update /tools/privacy/ to disclose the active provider. This does not touch DNS or GitHub Actions permissions.

If Counter.dev is activated, do not also activate Cloudflare analytics; the loader prioritises Counter to prevent double-counting. Until either site ID is entered, no third-party visitor tracker is loaded. GSC Wizard continues to track verified organic-search clicks and impressions independently.
