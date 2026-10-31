---
title: "Project Brief: RakanPay v2"
date: 2026-09-01
type: project-brief
access: all
---

# Project Brief: RakanPay v2

Author: Priya Nair, Product Manager
Project owner: Priya Nair
Engineering sponsor: Tan Mei Ling, CTO
Status: Approved by leadership on 1 September 2026

## 1. Problem

Today RakanPay lets small businesses create and send invoices, but customers still get paid
outside the app (bank transfer, cash, cheque). Business owners tell us they spend hours each
month chasing payments and matching them to invoices by hand. Many also send the same
invoice every month to the same clients and have to recreate it each time.

## 2. Goal

RakanPay v2 lets a small business send an invoice and get paid inside the same app, and
automates repeat invoices.

## 3. Scope

### 3.1 In scope

1. **Online payments.** A "Pay now" button on every invoice, through a payment provider.
   The provider (Stripe or iPay88) will be chosen by 18 September 2026 in a decision record.
2. **Recurring invoices.** Weekly, monthly or yearly invoices created and sent
   automatically.
3. **Mobile app.** A first version of the RakanPay mobile app (Android and iOS) for
   creating invoices and checking payment status.
4. **Payment matching.** Paid invoices are marked as paid automatically.

### 3.2 Out of scope

- LHDN e-Invoice submission. This is a separate project, see "Project Brief: LHDN e-Invoice
  Integration".
- Multi-currency invoices.
- Accounting software exports.

## 4. Timeline

| Milestone | Target date |
| --- | --- |
| Payment provider decision | 18 September 2026 |
| Mobile engineer hired | October 2026 |
| Feature complete | 15 November 2026 |
| Code freeze and final QA | 20 November 2026 |
| **Public launch** | **1 December 2026** |

## 5. Team

| Person | Role on the project |
| --- | --- |
| Priya Nair | Project owner, product decisions |
| Tan Mei Ling | Engineering sponsor, architecture |
| Jason Lim | QA, test plans and regression testing |
| Mobile engineer (to be hired) | Mobile app |
| Farah Aziz | Launch marketing and customer communication |

## 6. Success measures

- 30% of active customers send at least one invoice with "Pay now" within 60 days of launch.
- Average time from invoice sent to paid drops from 21 days to under 10 days.

## 7. Risks

- Payment provider onboarding and account verification may take longer than expected.
- We have no mobile engineer yet. Hiring late puts the mobile app at risk.
- QA capacity is one person (Jason Lim).
