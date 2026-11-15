# Project Proposal: Fraud Detection AI Platform
**Client:** Meridian National Bank
**Prepared by:** NexaAI Solutions — AI Engineering & Data & Analytics
**Date:** January 2022

## Business Problem
Meridian National Bank's current fraud detection stack relies on static,
rule-based flagging that has not kept pace with the growth in digital and
mobile transaction volume. The fraud operations team reports a rising
false-positive rate that is consuming analyst capacity, while several
recent fraud losses slipped through undetected because they did not match
any existing rule pattern.

## Proposed Solution
NexaAI proposes a machine-learning-based fraud detection platform,
combining supervised models trained on Meridian's historical transaction
and fraud-case data with a real-time scoring layer integrated into the
existing transaction pipeline. The solution will be delivered under our
**Responsible AI Framework**, given the direct financial and customer
impact of automated fraud decisions and the Central Bank's expectations
around model explainability and audit trails.

## Expected Outcomes
- Materially reduce false-positive rate versus the current rules engine
- Faster analyst triage through model-generated risk scores and explanations
- A documented, auditable model governance process suitable for regulatory review

## Key Assumptions
- Meridian's transaction and historical fraud-case data is sufficiently
  complete and labeled to support supervised model training (confirmed
  during a two-week data sampling exercise ahead of this proposal)
- Meridian will provide a dedicated fraud-operations liaison for model
  validation and feedback throughout delivery
- The Central Bank's model governance guidance will not materially change
  during the delivery window

## Strategy & Approach
Given the regulatory weight of fraud decisioning in banking, this
engagement follows NexaAI's Responsible AI Framework rather than a faster
but lighter-touch approach: every model release will pass through a
fairness and explainability review before touching production traffic.
This adds process overhead relative to a purely technical build, but is
the appropriate trade-off for a client-facing, compliance-sensitive use
case at this scale.

## Indicative Investment
Estimated budget: $1.55M–$1.65M over an estimated 22-24 month engagement,
covering model development, integration, and a phased rollout across
Meridian's retail and digital banking channels.
