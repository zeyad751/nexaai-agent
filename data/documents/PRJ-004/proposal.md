# Project Proposal: Enterprise Data Foundation for Credit Risk Modeling
**Client:** Falcon Gulf Bank
**Date:** May 2022

## Business Problem
Falcon Gulf Bank's credit risk models currently draw from several
disconnected data marts maintained by different teams, requiring manual
reconciliation before each quarterly model refresh. This slows model
updates and introduces reconciliation errors that have twice required
re-running a quarterly refresh.

## Proposed Solution
NexaAI proposes a **Data-First Transformation**: consolidating the
relevant credit risk data sources into a governed Snowflake-based
foundation before any new modeling work begins, rather than layering new
models on top of the current fragmented state.

## Key Assumptions
A two-week data maturity assessment was conducted ahead of this proposal,
covering data lineage documentation, existing data ownership structure,
and the bank's data quality tooling. The assessment found Falcon Gulf's
data infrastructure to be at a **moderate-to-good maturity level** —
source systems are reasonably well documented, and a data governance
function already exists, even though it has not yet been extended to the
credit risk domain specifically. This is treated as an explicit,
verified precondition for recommending the Data-First approach here: we
would not recommend this sequencing for a client without a comparable
baseline.

## Expected Outcomes
- A single governed data foundation for credit risk modeling, replacing
  the current multi-mart reconciliation process
- Faster, more reliable quarterly model refresh cycles
- A reusable foundation for future risk-modeling initiatives beyond this
  engagement's immediate scope

## Strategy & Approach
Because the data maturity assessment confirmed a solid baseline, this
engagement is scoped as a focused 6-month data foundation build rather
than a longer remediation-plus-build effort. We are explicit with the
client that this timeline assumption depends on that baseline holding;
if source-system documentation proves less complete than assessed during
discovery, the timeline would need to be revisited.

## Indicative Investment
Estimated budget: $580K-$620K over an estimated 6-month engagement.
