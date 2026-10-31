---
title: "Decision Record ADR-001: Payment Provider for RakanPay v2"
date: 2026-09-18
type: decision-record
access: all
---

# ADR-001: Payment Provider for RakanPay v2

Status: Accepted
Date: 18 September 2026
Deciders: Tan Mei Ling (CTO), Priya Nair (Product Manager)
Consulted: Kumar Selvam (Finance Manager), Danial Iskandar (Senior Backend Engineer)

## 1. Context

RakanPay v2 adds a "Pay now" button to every invoice (see "Project Brief: RakanPay v2").
We need one payment provider for the launch. The leadership meeting on 14 September 2026
shortlisted two options: **Stripe** and **iPay88**.

Requirements:

1. Card payments for Malaysian businesses.
2. Built-in support for recurring billing, because recurring invoices are part of v2.
3. A clean, well-documented API that our small team can integrate quickly.
4. Reasonable fees for small businesses.
5. Fast merchant onboarding, so we can hit the launch date.

## 2. Options considered

### 2.1 Stripe

- Strong API and documentation, good test (sandbox) tools, client libraries for our stack.
- Native recurring billing and subscriptions.
- Sandbox access on the same day. Our proof of concept took Danial 2 days.
- Quoted rate for Rakan Tech: **2.5% per card transaction**, no monthly fee.

### 2.2 iPay88

- Strong local coverage, especially FPX online banking and Malaysian e-wallets.
- Local support team in Kuala Lumpur.
- Recurring billing needs extra work on our side.
- The API is older and the proof of concept was not finished after 4 days.
- Merchant onboarding estimate: 3 to 4 weeks.

## 3. Decision

**We choose Stripe** as the payment provider for RakanPay v2.

## 4. Reasons

1. **Recurring billing is built in.** This saves an estimated 3 weeks of engineering work.
2. **Developer experience.** The API, docs and sandbox let a small team move fast.
3. **Faster onboarding.** We can start testing real payment flows immediately.
4. **Fees.** 2.5% per card transaction with no monthly fee is acceptable for launch.

## 5. Consequences

- We depend on Stripe's account verification and payout review before launch. This is a
  launch risk to track.
- Local e-wallet coverage is weaker than iPay88. We will review this 3 months after launch,
  and may add iPay88 as a second provider if customers ask for e-wallets.
- Finance (Kumar Selvam) will set up the Stripe account and payout bank details.
