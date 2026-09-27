# Fix Resend sending-domain DNS safely

Audit date: 26 September 2026. Public nameservers for **ragunauthramsaroop.com** are **launch1.spaceship.net** and **launch2.spaceship.net**. The live website points to GitHub Pages. The four Resend email records listed below were entirely absent in public DNS at the audit.

## Owner action at Spaceship

Open [Spaceship](https://www.spaceship.com/), sign in, open **Launchpad > Advanced DNS**, select **ragunauthramsaroop.com**, then **DNS records > Custom records**. Add each missing record, with TTL set to Auto or 3600. Enter host labels only, not the full domain, if Spaceship automatically appends the domain.

| Type | Host | Value | Priority |
| --- | --- | --- | --- |
| TXT | `resend._domainkey` | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCkkb5ZsDVidwWGbFFPIaLN8XNpACUNvFBEL47/rZ7ZC61g099rKSvK42BzmF7DWIrlKgXuhV14eUxJRcj9AHqjvUBtCEMw/0I7eEmCxvluo/4ztlMGUd3Rv5GhevdI7Jy15CTJi+mvYxCS/kvNkLtGQMjz5HuVugzB3Bj0F4vgbQIDAQAB` | |
| MX | `send` | `feedback-smtp.us-east-1.amazonses.com` | **10** |
| TXT | `send` | `v=spf1 include:amazonses.com ~all` | |
| CNAME | `rsend` | `send.forge.rmta.net` | |

The DKIM TXT entry contains a **public key**, not a Resend API secret. Use the exact record values currently displayed under your Resend domain settings if those values change. The `rsend` CNAME is the provider's additional sending/tracking record. No A record belongs on `send` or `rsend`.

**Preserve**: all four existing root GitHub Pages A records (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`); the `www` CNAME (`ragunauth123456-maker.github.io`); the existing nameservers; and the root Google verification TXT. These are unrelated to newsletter delivery.

## Verify without exposing credentials

Use the [GitHub DNS readiness workflow](https://github.com/ragunauth123456-maker/ragunauthramsaroop-site/actions/workflows/email-dns-readiness.yml), click **Run workflow**, and set **strict=true** after you add the four records. The workflow also checks daily, without sending mail or changing DNS. A passing DNS check means the public records exist, not that Resend has finished internal verification.

Once DNS is present, open [Resend Domains](https://resend.com/domains), select the current domain, and press **Verify / I've added the records**. Wait until **Verified**, then test sending from the verified domain. The existing website signup page intentionally remains in manual/RSS mode until a secure backend is connected, double opt-in and unsubscribe are tested, and no personal contact information is exposed on GitHub Pages.

Optional deliverability hardening after testing: publish `_dmarc` as a TXT policy with `v=DMARC1; p=none`, monitor legitimate sources, then strengthen the policy deliberately. Do not invent a DMARC reporting mailbox or modify existing user email settings.

## Alternative automation with explicit owner credentials

Spaceship provides an official full [DNS-capable MCP integration](https://www.spaceship.com/knowledgebase/spaceship-mcp/) and [API](https://docs.spaceship.dev/) with `dnsrecords:write` permission. The current connected ChatGPT Spaceship tool exposes domain availability only and does **not** grant DNS writes. The owner must either add the records in Spaceship or grant the full DNS-management integration. Never paste API keys, Resend secrets or registrar passwords in a chat or public issue.

Current fallback: existing email requests open the visitor's own email application, and both RSS feeds remain available.
