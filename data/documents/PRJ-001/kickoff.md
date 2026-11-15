# Kickoff Document: Fraud Detection AI Platform
**Date:** February 12, 2022
**Project ID:** PRJ-001

## Stakeholders
- **Client sponsor:** Meridian National Bank, Chief Risk Officer's team
- **Client operational lead:** Head of Fraud Operations
- **NexaAI Project Manager:** Ryan Shawky
- **NexaAI Engagement Lead:** Amr Hassan, Director of AI Engineering
- **NexaAI Data & Analytics Lead:** Mostafa Farouk, Director of Data & Analytics

## Objectives
1. Reduce false-positive fraud alerts without increasing missed-fraud rate
2. Deliver real-time transaction scoring integrated into the existing
   authorization pipeline
3. Produce a governance package (model documentation, fairness testing
   results, explainability reporting) suitable for the bank's internal
   model risk committee

## Initial Team
A 20-person cross-functional team has been assembled spanning AI
Engineering, Data & Analytics, Cloud & Infrastructure, Project Management,
Cybersecurity, and Finance — reflecting both the technical scope and the
compliance review load expected under the Responsible AI Framework.

## Known Risks at Kickoff
- **Budget:** the phased rollout across multiple banking channels
  (retail, digital, mobile) creates some estimation uncertainty on
  integration effort per channel; flagged for close tracking in the
  first two reporting cycles.
- **Regulatory:** all model releases require sign-off from the bank's
  model risk committee before reaching production traffic; committee
  review cadence is monthly, which will pace the rollout schedule.

## Initial Plan
Delivery is structured in four phases: data foundation and model
development (Q1-Q2 2022), pilot scoring on a single transaction channel
(Q3 2022), phased rollout across remaining channels (Q4 2022-Q3 2023),
and a stabilization/optimization phase through early 2024. Governance
review checkpoints are built into the transition between each phase.
