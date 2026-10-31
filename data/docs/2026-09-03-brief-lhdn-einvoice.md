---
title: "Project Brief: LHDN e-Invoice Integration"
date: 2026-09-03
type: project-brief
access: all
---

# Project Brief: LHDN e-Invoice Integration

Author: Danial Iskandar, Senior Backend Engineer
Project owner: Danial Iskandar
Technical reviewer: Nurul Huda Kamal, Engineering Lead, Integrations
Status: Approved by leadership on 3 September 2026

## 1. Problem

Malaysian businesses are moving to e-Invoicing through LHDN's MyInvois system. Our
customers are small businesses, and many of them are now asking how RakanPay will help them
comply. Without e-Invoice support, customers will have to re-enter every invoice in another
tool, and some will leave RakanPay.

## 2. Goal

Every invoice created in RakanPay can be submitted to LHDN MyInvois with one click, and the
validated e-Invoice (with its unique identifier and QR code) is stored and shown in the app.

## 3. Scope

### 3.1 In scope

1. Connect to the MyInvois API (sandbox first, then production).
2. Map RakanPay invoice fields to the LHDN e-Invoice format.
3. Submit invoices, read back the validation result, and show errors to the user in plain
   language.
4. Store the LHDN unique identifier and QR code on the invoice and on the invoice PDF.
5. Support credit notes and debit notes.

### 3.2 Out of scope

- Consolidated e-Invoices for retail sales (planned for a later phase).
- Payments. Online payments are part of RakanPay v2, a separate project.

## 4. Timeline

| Milestone | Target date |
| --- | --- |
| Sandbox credentials received | September 2026 |
| Field mapping complete | 15 October 2026 |
| All invoice types pass sandbox validation | 30 November 2026 |
| Production rollout to pilot customers | January 2027 |

## 5. Team

| Person | Role on the project |
| --- | --- |
| Danial Iskandar | Project owner, backend development |
| Nurul Huda Kamal | Technical reviewer, integration design |
| Jason Lim | QA support (shared with RakanPay v2) |

## 6. Risks

- The LHDN API and validation rules may change during the project.
- Sandbox downtime can block testing.
- Jason Lim is shared with RakanPay v2, so QA time is limited.
