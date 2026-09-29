# iCloud SMTP outreach outbox

This folder is a secure trigger point for user-approved executive outreach sent from Ragunauth Ramsaroop's iCloud Mail account through Apple's SMTP service.

Never store an Apple Account password or app-specific password in this repository.

Required GitHub Actions secret:
- ICLOUD_APP_PASSWORD

Each JSON payload must set approved=true and contain no more than 10 messages. A new payload commit triggers the workflow and sends only the changed payload.

Apple iCloud SMTP endpoint used by the workflow:
- smtp.mail.me.com
- port 587
- STARTTLS
- authenticated as ragunauthramsaroop@icloud.com
