---
title: "RakanPay v2 Stand-up, 22 September 2026"
date: 2026-09-22
type: standup
access: all
---

# RakanPay v2 Stand-up, 22 September 2026

Attendees: Priya Nair (chair), Tan Mei Ling, Jason Lim, Danial Iskandar (guest, Stripe
proof of concept)
Notes by: Priya Nair

## Updates

- **Mei Ling:** Stripe sandbox is wired into our staging environment, following ADR-001.
  Test card payments work end to end on a sample invoice.
- **Danial:** handed over the Stripe proof of concept code to Mei Ling. Back on e-Invoice
  full time from tomorrow.
- **Priya:** recurring invoice design is ready for review. Options: weekly, monthly,
  yearly. Customers can pause a recurring invoice.
- **Jason:** drafting the test plan for "Pay now" and recurring invoices.

## Status

On track for the **1 December 2026** launch.

## Blockers and risks

- No mobile engineer yet. Mobile app work has not started.
- Stripe merchant account verification has been submitted. Waiting on Stripe.

## Actions

| Action | Owner |
| --- | --- |
| Review recurring invoice design | Mei Ling, Jason |
| Share the test plan draft | Jason |
| Follow up with Stripe on account verification | Kumar (via Priya) |
