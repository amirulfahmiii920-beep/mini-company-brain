---
title: "LHDN e-Invoice Stand-up, 22 October 2026"
date: 2026-10-22
type: standup
access: all
---

# LHDN e-Invoice Stand-up, 22 October 2026

Attendees: Nurul Huda Kamal (chair, project owner), Jason Lim, Danial Iskandar (handover
questions only)
Notes by: Nurul Huda Kamal

## 1. Updates

- **Nurul:** field mapping is complete. Tax classification code defaults are fixed.
- **Jason:** **60% of invoice types now pass sandbox validation.** Standard invoices pass.
  Credit notes and debit notes still fail on the reference to the original invoice.
- **Danial:** answered handover questions on credit notes. Handover ends on 31 October.

## 2. Vendor email

- On 21 October Nurul forwarded an email from a middleware vendor offering a ready-made
  MyInvois connector.
- Decision: not now. We will finish our own integration first and look at the vendor again
  only if we miss the November target.

## 3. Status

On track. Target for all invoice types to pass sandbox validation is still
**30 November 2026**. Production rollout to pilot customers is planned for January 2027.

## Actions

| Action | Owner |
| --- | --- |
| Fix credit and debit note references | Nurul |
| Re-run full sandbox test suite | Jason |
