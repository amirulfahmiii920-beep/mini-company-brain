---
title: "LHDN e-Invoice Stand-up, 8 October 2026"
date: 2026-10-08
type: standup
access: all
---

# LHDN e-Invoice Stand-up, 8 October 2026

Attendees: Nurul Huda Kamal (chair), Danial Iskandar, Jason Lim, Tan Mei Ling (guest)
Notes by: Nurul Huda Kamal

## 1. Ownership change

- From today, **Nurul Huda Kamal is the owner of the LHDN e-Invoice integration**.
- **Danial Iskandar moves to RakanPay v2** to work full time on the Stripe payments
  backend (recurring billing and webhooks), which needs a dedicated backend engineer.
- Danial stays available for e-Invoice handover questions for 2 hours per week until
  31 October 2026.
- Mei Ling approved the change and will confirm it at the leadership meeting on
  12 October.

## 2. Updates

- **Danial:** field mapping is about 80% done. Handover document is in the project folder.
- **Nurul:** the submission retry queue is built and tested in staging.
- **Jason:** tested 20 sample invoices in the sandbox. 12 passed validation, 8 failed on
  missing tax classification codes.

## 3. Status

On track. Target for all invoice types to pass sandbox validation is still
**30 November 2026**.

## Actions

| Action | Owner |
| --- | --- |
| Finish field mapping | Nurul |
| Fix tax classification code defaults | Nurul |
| Handover session on credit and debit notes | Danial |
