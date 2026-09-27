# RR briefing delivery readiness

Status: staged; automatic email sending is disabled.

The public website is static GitHub Pages. It offers RSS and a user-controlled mailto request while its verified backend is unavailable. Never put a Resend API key in browser JavaScript or this repository.

A dedicated Resend opt-in segment and four opt-out-default newsletter topics have been created, with no existing subscriber opted in or emailed. Provider domain verification currently fails for DKIM and sending DNS records, so a confirmation message cannot reliably be sent from the public domain.

Activate only after: (1) owner updates DNS at the authoritative provider using the current Resend domain dashboard (do not overwrite GitHub Pages records); (2) Resend reports verified; (3) deploy a secure same-origin serverless signup endpoint with rate limits, bot protection and server-side double opt-in; (4) verify a real confirmation message, bounce and unsubscribe webhook; (5) add full privacy disclosure and deletion policy; (6) set an enabled flag in a separate deployment after passing all tests.

No automated delivery, contact collection or subscription confirmation is represented by the current static page.
