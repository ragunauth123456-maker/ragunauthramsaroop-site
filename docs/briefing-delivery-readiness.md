# RR briefing delivery readiness

Status: staged; automatic email sending is disabled.

The public website is static GitHub Pages. It offers RSS and a user-controlled mailto request while its verified backend is unavailable. Never put a Resend API key in browser JavaScript or this repository.

A dedicated Resend opt-in segment and four opt-out-default newsletter topics have been created, with no existing subscriber opted in or emailed. Resend confirmed the sending domain **verified** on 2026-09-27. All four DKIM/SPF/MX/CNAME entries are verified and the provider reports sending enabled. This does not mean the website newsletter signup endpoint is active. No existing subscriber has been enrolled or emailed.

Completed: (1) owner updated DNS without changing GitHub Pages records; (2) Resend reports **verified**, with sending enabled. Still required: (3) deploy a secure same-origin serverless signup endpoint with rate limits, bot protection and server-side double opt-in; (4) verify a real confirmation message, bounce and unsubscribe webhook; (5) add full privacy disclosure and deletion policy; (6) set an enabled flag in a separate deployment after passing all tests.

No automated delivery, contact collection or subscription confirmation is represented by the current static page.
