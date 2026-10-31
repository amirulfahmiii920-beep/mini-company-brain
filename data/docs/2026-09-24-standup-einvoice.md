---
title: "LHDN e-Invoice Stand-up, 24 September 2026"
date: 2026-09-24
type: standup
access: all
---

# LHDN e-Invoice Stand-up, 24 September 2026

Attendees: Danial Iskandar (chair, project owner), Nurul Huda Kamal, Jason Lim
Notes by: Danial Iskandar

## Updates

- **Danial:** MyInvois sandbox credentials received on 23 September. First test call to
  the sandbox API works. Started mapping RakanPay invoice fields to the LHDN format, about
  40% done.
- **Nurul:** reviewed the integration design. Suggests a submission queue with retries, so
  that sandbox or production downtime does not block users.
- **Jason:** can give e-Invoice 1 day per week of QA time. The rest goes to RakanPay v2.

## Status

On track. Field mapping target is 15 October. Sandbox validation target is
**30 November 2026**.

## Blockers and risks

- LHDN sandbox was down for 3 hours on 23 September. A retry queue will help.
- Tax classification codes for some customer products are unclear. Danial will ask two
  pilot customers.

## Actions

| Action | Owner |
| --- | --- |
| Design submission retry queue | Nurul |
| Continue field mapping | Danial |
| Ask pilot customers about tax classification codes | Danial |
