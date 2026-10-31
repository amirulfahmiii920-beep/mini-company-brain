---
title: "RakanPay v2 Stand-up, 27 October 2026"
date: 2026-10-27
type: standup
access: all
---

# RakanPay v2 Stand-up, 27 October 2026

Attendees: Priya Nair (chair), Tan Mei Ling, Danial Iskandar, Jason Lim, Ong Wei Jie
Notes by: Priya Nair

## 1. Status

On track. Code freeze on **1 December 2026**, public launch on **15 December 2026**.

## 2. Updates

- **Danial:** Stripe webhooks and recurring billing are in staging. Payment status updates
  on the invoice within 5 seconds.
- **Wei Jie:** Android invoice list and detail screens done. Starting the iOS build.
- **Mei Ling:** Stripe account review is complete, payouts approved.
- **Jason:** regression plan for launch:
  1. Full regression of v1 invoicing features.
  2. "Pay now" with test cards, including failed and refunded payments.
  3. Recurring invoices: create, pause, resume, cancel.
  4. Load test: 500 invoices paid within 10 minutes.
  5. Mobile app smoke tests on 3 Android and 2 iOS devices.

## 3. Blockers and risks

- Mobile app internal beta planned for 10 November. Tight, but possible.

## Actions

| Action | Owner |
| --- | --- |
| iOS build | Wei Jie |
| Load test scripts | Jason |
| Refund flow in staging | Danial |
